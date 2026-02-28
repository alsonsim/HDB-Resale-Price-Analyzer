import subprocess
import re

CDP = "wss://brd-customer-hl_84d1c45e-zone-brower_hdb:r89v7zif5ap2@brd.superproxy.io:9222"
ACTIONBOOK_PATH = r"C:\Users\alson\AppData\Roaming\npm\actionbook.ps1"

def run_actionbook(args: str) -> subprocess.CompletedProcess:
    cmd = f'powershell -ExecutionPolicy Bypass -File "{ACTIONBOOK_PATH}" --cdp "{CDP}" {args}'
    return subprocess.run(
        cmd, capture_output=True, text=True,
        shell=True, timeout=30,
        encoding='utf-8', errors='ignore'
    )

def scrape_with_actionbook(town: str, flat_type: str) -> list[dict]:
    print(f"🤖 ActionBook → Bright Data cloud browser...")

    run_actionbook('browser open "https://www.99.co/singapore/hdb-resale-price"')
    result = run_actionbook("browser text")

    content = result.stdout or ""
    print(f"✅ Got {len(content)} chars")

    flat_index = {"3 ROOM": 0, "4 ROOM": 1, "5 ROOM": 2, "EXECUTIVE": 3}
    idx = flat_index.get(flat_type.upper(), 1)

    # Match any line containing town name (case-insensitive) AND a price
    lines = content.split('\n')
    town_lines = [l for l in lines if town.upper() in l.upper() and re.search(r'S\$\s?[\d,]+', l)]
    print(f"🔍 Town lines found: {town_lines[:3]}")

    listings = []
    for line in town_lines:
        prices = re.findall(r'S\$\s?[\d,]+', line)
        if prices and idx < len(prices):
            listings.append({
                "price": prices[idx].replace(" ", ""),
                "flat_type": flat_type,
                "town": town,
                "source": "99.co via ActionBook + Bright Data"
            })

    print(f"🤖 Parsed listings: {listings}")
    return listings if listings else [{"source": "Bright Data", "status": "no data found"}]
