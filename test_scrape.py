import requests
from bs4 import BeautifulSoup

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
response = requests.get("https://www.99.co/singapore/hdb-resale-price", headers=headers)
soup = BeautifulSoup(response.text, "html.parser")
text = soup.get_text()

# Save to file to inspect
with open("99co_raw.txt", "w", encoding="utf-8") as f:
    f.write(text)

print("Saved! Total chars:", len(text))
print("Contains Queenstown?", "Queenstown" in text)
