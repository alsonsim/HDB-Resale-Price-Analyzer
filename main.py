from agent.scraper import scrape_listings
from agent.browser import scrape_with_actionbook
from agent.context import create_session, save_to_session
from agent.analyzer import analyze_price
import requests

def get_historical_data(town, flat_type):
    url = "https://data.gov.sg/api/action/datastore_search"
    try:
        r = requests.get(url, params={
            "resource_id": "d_8b84c4ee58e3cfc0ece0d773c8ca6abc",
            "limit": 1
        }, timeout=15)
        total = r.json().get("result", {}).get("total", 0)

        # Try increasing window until we get results
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

            print(f"📊 Window {window}: {len(filtered)} matches")
            if len(filtered) >= 10:
                print(f"📊 Loaded {len(filtered)} historical transactions")
                return filtered

        return []
    except Exception as e:
        print(f"⚠️ Failed: {e}")
        return []



if __name__ == "__main__":
    town = input("Enter town (e.g. QUEENSTOWN): ").strip()
    flat_type = input("Enter flat type (e.g. 4 ROOM): ").strip()
    listing_price = int(input("Enter listing price (SGD): ").strip())

    session_id = create_session(f"{flat_type} in {town}")

    historical = get_historical_data(town, flat_type)
    save_to_session(session_id, "historical_data", historical)

    live_data = scrape_with_actionbook(town, flat_type)
    save_to_session(session_id, "live_listings", live_data)

    if not historical and live_data and "price" in live_data[0]:
        price_val = int(live_data[0]["price"].replace("S$", "").replace(",", ""))
        historical = [{"resale_price": price_val}]
        print(f"📊 Using live median as fallback: {live_data[0]['price']}")

    result = analyze_price(listing_price, town, flat_type, historical)
    print("\n🏠 HDB Price Analysis")
    print("=" * 40)
    print(f"Town:        {town}")
    print(f"Flat Type:   {flat_type}")
    print(f"Listed:      SGD {listing_price:,}")
    print(f"Market Avg:  SGD {result['avg_price']:,}")
    print(f"Difference:  {result['diff_pct']:+.1f}%")
    print(f"Verdict:     {result['verdict']}")
    print(f"Analysis:    {result['explanation']}")
