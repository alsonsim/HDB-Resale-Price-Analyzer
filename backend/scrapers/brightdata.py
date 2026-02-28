import httpx
from backend.config import settings


class BrightDataScraper:
    """Wrapper around Bright Data SDK for scraping property listing portals.

    Bright Data handles CAPTCHA solving, proxy rotation, and anti-bot bypass
    for sites like PropertyGuru and 99.co.
    """

    SOURCES = {
        "propertyguru": {
            "base_url": "https://www.propertyguru.com.sg",
            "search_path": "/property-for-sale?market=residential&property_type=H&freetext={query}",
        },
        "99co": {
            "base_url": "https://www.99.co",
            "search_path": "/singapore/sale/hdb?query={query}",
        },
    }

    def __init__(self):
        self.api_token = settings.brightdata_api_token
        self.base_api_url = "https://api.brightdata.com"

    async def scrape_listings(
        self,
        source: str = "propertyguru",
        town: str | None = None,
        flat_type: str | None = None,
        max_pages: int = 3,
    ) -> list[dict]:
        """Scrape live HDB resale listings from a property portal.

        Uses Bright Data's scraping browser API for JavaScript-rendered pages.
        """
        if not self.api_token:
            return await self._mock_scrape(source, town, flat_type)

        source_config = self.SOURCES.get(source, self.SOURCES["propertyguru"])
        query_parts = []
        if town:
            query_parts.append(town)
        if flat_type:
            query_parts.append(flat_type)
        query = " ".join(query_parts) if query_parts else "HDB resale"

        url = source_config["base_url"] + source_config["search_path"].format(query=query)

        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }

        all_listings = []
        for page in range(1, max_pages + 1):
            page_url = f"{url}&page={page}" if page > 1 else url

            payload = {
                "url": page_url,
                "format": "raw_html",
                "wait_for_selector": ".listing-card, .listing-item, [data-listing-id]",
            }

            try:
                async with httpx.AsyncClient(timeout=60) as client:
                    response = await client.post(
                        f"{self.base_api_url}/request",
                        json=payload,
                        headers=headers,
                    )
                    response.raise_for_status()
                    data = response.json()

                listings = self._parse_listings(data, source)
                all_listings.extend(listings)

            except httpx.HTTPError:
                break

        return all_listings

    async def scrape_url(self, url: str) -> str:
        """Scrape a single URL and return the page content as markdown."""
        if not self.api_token:
            return ""

        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{self.base_api_url}/request",
                json={"url": url, "format": "markdown"},
                headers=headers,
            )
            response.raise_for_status()
            return response.json().get("content", "")

    def _parse_listings(self, raw_data: dict, source: str) -> list[dict]:
        """Parse raw scraped data into structured listing dicts.

        This is a simplified parser — in production, you'd use Bright Data's
        structured data collectors or custom parsing logic per source.
        """
        listings = raw_data.get("listings", [])
        parsed = []

        for item in listings:
            parsed.append({
                "source": source,
                "url": item.get("url", ""),
                "title": item.get("title", ""),
                "town": item.get("town", "").upper(),
                "flat_type": item.get("flat_type", ""),
                "asking_price": float(item.get("price", 0)),
                "floor_area_sqm": float(item.get("floor_area", 0)) if item.get("floor_area") else None,
                "storey": item.get("floor", ""),
            })

        return parsed

    async def _mock_scrape(self, source: str, town: str | None, flat_type: str | None) -> list[dict]:
        """Return mock data when no API token is configured (development mode)."""
        town = (town or "TAMPINES").upper()
        flat_type = flat_type or "4 ROOM"

        return [
            {
                "source": source,
                "url": f"https://{source}.com.sg/listing/mock-1",
                "title": f"{flat_type} at {town} - Well Maintained",
                "town": town,
                "flat_type": flat_type,
                "asking_price": 520000.0,
                "floor_area_sqm": 93.0,
                "storey": "07 TO 09",
            },
            {
                "source": source,
                "url": f"https://{source}.com.sg/listing/mock-2",
                "title": f"{flat_type} at {town} - Renovated",
                "town": town,
                "flat_type": flat_type,
                "asking_price": 560000.0,
                "floor_area_sqm": 95.0,
                "storey": "10 TO 12",
            },
        ]


brightdata_scraper = BrightDataScraper()
