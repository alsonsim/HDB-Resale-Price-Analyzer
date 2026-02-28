import requests, os
from dotenv import load_dotenv
load_dotenv()

user = os.getenv("BRIGHTDATA_USER")
pwd = os.getenv("BRIGHTDATA_PASS")
print(f"Testing with user: {user}")

proxies = {
    "https": f"http://{user}:{pwd}@brd.superproxy.io:22225",
}
r = requests.get("https://geo.brdtest.com/mygeo.json", proxies=proxies, verify=False, timeout=15)
print(r.json())
