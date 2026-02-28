import os
import json
import asyncio
from dotenv import load_dotenv

load_dotenv()

AUTH = "brd-customer-hl_84d1c45e-zone-brower_hdb:r89v7zif5ap2"
SBR_WS = f"wss://{AUTH}@brd.superproxy.io:9222"

async def _scrape_async(town: str, flat_type: str) -> list[dict]:
    from playwright.async_api import async_playwright
    
    flat_map = {"4 ROOM": "4-room", "3 ROOM": "3-room", "5 ROOM": "5-room", "EXECUTIVE": "executive"}
    flat_slug = flat_map.get(flat_type.upper(), "4-room")
    town_slug = town.lower().replace(" ", "-")
    
    url = f"https://www.propertyguru.com.sg/property-for-sale?freetext={town_slug}&property_type=H&property_type_code[]=HDB&listing_type=sale&room={flat_slug}"

    async with async_playwright() as pw:
        browser = await pw.chromium.connect_over_cdp(SBR_WS)
        page = await browser.new_page()
        print(f"🌐 Navigating to PropertyGuru...")
        await page.goto(url, timeout=60000)
        await page.wait_for_timeout(6000)
        await page.screenshot(path="./data/propertyguru_screenshot.png")

        listings = await page.evaluate("""
            () => {
                const cards = document.querySelectorAll('[data-listing-id], .listing-card, [class*="ListingCard"], [class*="property-card"]');
                if (cards.length > 0) {
                    return Array.from(cards).slice(0, 10).map(card => ({
                        title: card.querySelector('[class*="title"], h3, h2')?.innerText || '',
                        price: card.querySelector('[class*="price"], [class*="Price"]')?.innerText || '',
                        address: card.querySelector('[class*="address"], [class*="Address"]')?.innerText || ''
                    }));
                }
                // Fallback: grab anything with a price
                const priceEls = document.querySelectorAll('[class*="price"], [class*="Price"]');
                return Array.from(priceEls).slice(0, 10).map(el => ({
                    price: el.innerText,
                    title: el.closest('li,article,div[class*="card"]')?.querySelector('h2,h3')?.innerText || ''
                }));
            }
        """)

        await browser.close()
        print(f"🌐 Scraped {len(listings)} PropertyGuru listings")
        return listings if listings else _fallback_scrape(town, flat_type)

def scrape_listings(town: str, flat_type: str) -> list[dict]:
    try:
        return asyncio.run(_scrape_async(town, flat_type))
    except Exception as e:
        print(f"⚠️ Browser API failed: {e}, using fallback")
        return _fallback_scrape(town, flat_type)

def _fallback_scrape(town: str, flat_type: str) -> list[dict]:
    import requests
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
