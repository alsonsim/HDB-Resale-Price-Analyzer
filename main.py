from agent.scraper import scrape_listings
from agent.browser import navigate_hdb_portal
from agent.context import create_session, save_to_session
from agent.analyzer import analyze_price
import requests, json

def get_historical_data(town, flat_type):
    url = "https://data.gov.sg/api/action/datastore_search"
    params = {
        "resource_id": "d_8b84c4ee58e3cfc0ece0d773c8ca6abc",
        "limit": 500,
        "filters": json.dumps({
            "town": town.upper(),
            "flat_type": flat_type.upper()
        })
    }
    r = requests.get(url, params=params, timeout=15)
    data = r.json()
    
    # Handle both possible structures
    if "result" in data:
        records = data["result"]["records"]
    elif "data" in data:
        records = data["data"]
    else:
        print("Unexpected structure:", data)
        return []
    
    print(f"📊 Loaded {len(records)} historical transactions")
    return [{"resale_price": int(rec["resale_price"])} for rec in records]


if __name__ == "__main__":
    town = input("Enter town (e.g. QUEENSTOWN): ").strip()
    flat_type = input("Enter flat type (e.g. 4 ROOM): ").strip()
    listing_price = int(input("Enter listing price (SGD): ").strip())

    # 1. Start Acontext session
    session_id = create_session(f"{flat_type} in {town}")

    # 2. Get historical data
    historical = get_historical_data(town, flat_type)
    save_to_session(session_id, "historical_data", historical)
    print(f"📊 Loaded {len(historical)} historical transactions")

    # 3. Scrape live listings
    live_data = scrape_listings(town, flat_type)
    save_to_session(session_id, "live_listings", live_data)

    # 4. Analyze + generate verdict
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
