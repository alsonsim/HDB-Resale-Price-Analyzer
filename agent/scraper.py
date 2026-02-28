import requests
import os
import json
from dotenv import load_dotenv
from bs4 import BeautifulSoup

load_dotenv()

API_TOKEN = os.getenv("BRIGHTDATA_API_KEY")
SERP_ZONE = os.getenv("BRIGHTDATA_SERP_ZONE")  # e.g. "serp_api1"

def scrape_listings(town: str, flat_type: str) -> list[dict]:
    query = f"HDB {flat_type} {town} resale price site:99.co"
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "zone": SERP_ZONE,
        "url": f"https://www.google.com/search?q={query.replace(' ', '+')}&gl=sg&hl=en&brd_json=1",
        "format": "raw"
    }
    r = requests.post("https://api.brightdata.com/request", headers=headers, json=payload, timeout=30)
    print(f"🌐 Bright Data SERP status: {r.status_code}")
    
    if r.status_code == 200:
        data = r.json()
        results = data.get("organic", [])
        listings = [{"title": x.get("title"), "url": x.get("link"), "snippet": x.get("description")} for x in results[:10]]
        print(f"🌐 Got {len(listings)} SERP results")
        return listings
    else:
        print(f"⚠️ SERP failed: {r.text[:100]}, using fallback")
        return _fallback_scrape(town, flat_type)

def _fallback_scrape(town: str, flat_type: str) -> list[dict]:
    url = "https://data.gov.sg/api/action/datastore_search"
    params = {
        "resource_id": "d_8b84c4ee58e3cfc0ece0d773c8ca6abc",
        "limit": 10,
        "filters": json.dumps({"town": town.upper(), "flat_type": flat_type.upper()}),
        "sort": "month desc"
    }
    r = requests.get(url, params=params, timeout=15)
    records = r.json().get("result", {}).get("records", [])
    print(f"🌐 Fallback: fetched {len(records)} recent listings")
    return [{"title": f"{rec['flat_type']} at {rec['street_name']}", "price": int(rec["resale_price"]), "month": rec["month"]} for rec in records]
