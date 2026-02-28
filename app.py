from flask import Flask, render_template, request, jsonify
from agent.browser import scrape_with_actionbook
from agent.context import create_session, save_to_session
from agent.analyzer import analyze_price
import requests

app = Flask(__name__)


def get_historical_data(town, flat_type):
    url = "https://data.gov.sg/api/action/datastore_search"
    try:
        r = requests.get(url, params={
            "resource_id": "d_8b84c4ee58e3cfc0ece0d773c8ca6abc",
            "limit": 1
        }, timeout=15)
        total = r.json().get("result", {}).get("total", 0)

        for window in [500, 2000, 5000, 10000]:
            last_offset = max(0, total - window)
            r2 = requests.get(url, params={
                "resource_id": "d_8b84c4ee58e3cfc0ece0d773c8ca6abc",
                "limit": window,
                "offset": last_offset
            }, timeout=30)
            records = r2.json().get("result", {}).get("records", [])
            filtered = [
                {"resale_price": int(float(rec["resale_price"]))}
                for rec in records
                if rec.get("town", "").strip().upper() == town.strip().upper()
                and rec.get("flat_type", "").strip().upper() == flat_type.strip().upper()
            ]
            if len(filtered) >= 10:
                return filtered
        return []
    except:
        return []


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    town = data["town"].strip()
    flat_type = data["flat_type"].strip()
    listing_price = int(data["listing_price"])

    session_id = create_session(f"{flat_type} in {town}")
    historical = get_historical_data(town, flat_type)
    save_to_session(session_id, "historical_data", historical)

    live_data = scrape_with_actionbook(town, flat_type)
    save_to_session(session_id, "live_listings", live_data)

    if not historical and live_data and "price" in live_data[0]:
        price_val = int(live_data[0]["price"].replace("S$", "").replace(",", ""))
        historical = [{"resale_price": price_val}]

    result = analyze_price(listing_price, town, flat_type, historical)
    return jsonify({
        "town": town,
        "flat_type": flat_type,
        "listing_price": listing_price,
        "avg_price": result["avg_price"],
        "diff_pct": round(result["diff_pct"], 1),
        "verdict": result["verdict"],
        "explanation": result["explanation"]
    })


@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    messages = data.get("messages", [])
    system_prompt = data.get("system", "")

    full_prompt = system_prompt + "\n\n"
    for msg in messages:
        role = "User" if msg["role"] == "user" else "Assistant"
        full_prompt += f"{role}: {msg['content']}\n"
    full_prompt += "Assistant:"

    try:
        res = requests.post("http://localhost:11434/api/generate", json={
            "model": "llama3.2",
            "prompt": full_prompt,
            "stream": False
        }, timeout=60)
        reply = res.json().get("response", "").strip()
    except Exception as e:
        reply = f"Ollama error: {str(e)}"

    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
