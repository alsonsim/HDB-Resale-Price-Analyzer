import requests


def analyze_price(listing_price, town, flat_type, historical_data):
    if not historical_data:
        return {
            "avg_price": 0,
            "diff_pct": 0.0,
            "verdict": "Insufficient Data",
            "explanation": f"No historical data found for {flat_type} in {town}."
        }

    avg = sum(d["resale_price"] for d in historical_data) / len(historical_data)
    diff_pct = (listing_price - avg) / avg * 100
    verdict = "Underpriced" if diff_pct < -5 else "Overpriced" if diff_pct > 5 else "Fair"

    prompt = f"""You are a Singapore HDB property analyst.
A {flat_type} flat in {town} is listed at SGD {listing_price:,}.
The recent market average is SGD {int(avg):,} based on {len(historical_data)} transactions.
The listing is {abs(diff_pct):.1f}% {'below' if diff_pct < 0 else 'above'} market average.
Verdict: {verdict}.
Give a 2-3 sentence analysis for a buyer. Be concise and practical."""

    try:
        r = requests.post("http://localhost:11434/api/generate", json={
            "model": "llama3.2",
            "prompt": prompt,
            "stream": False
        }, timeout=30)
        explanation = r.json().get("response", "").strip()
    except Exception:
        explanation = f"This listing is {abs(diff_pct):.1f}% {'below' if diff_pct < 0 else 'above'} the recent average of SGD {int(avg):,} for {flat_type} flats in {town}."

    return {
        "avg_price": int(avg),
        "diff_pct": diff_pct,
        "verdict": verdict,
        "explanation": explanation
    }
