import requests, os
from dotenv import load_dotenv
load_dotenv()

# Test SERP API (you have 1,333 requests free)
headers = {"Authorization": f"Bearer {os.getenv('BRIGHTDATA_API_KEY')}"}
params = {"q": "HDB 4 room Queenstown resale", "gl": "sg"}

r = requests.get(
    "https://api.brightdata.com/serp",
    headers=headers,
    params=params,
    timeout=30
)
print(f"Status: {r.status_code}")
print(r.text[:500])
