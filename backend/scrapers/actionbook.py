import httpx
from backend.config import settings


class ActionBookClient:
    """Wrapper for ActionBook browser automation.

    ActionBook provides pre-computed "action manuals" — structured instructions
    for navigating property listing sites. Instead of brittle CSS selectors,
    ActionBook maintains resilient action sequences that adapt to UI changes.

    Integration options:
    - MCP Server (recommended for agent workflows)
    - CLI (for local browser automation)
    - HTTP API (for programmatic access)
    """

    def __init__(self):
        self.api_key = settings.actionbook_api_key
        self.base_url = settings.actionbook_base_url

    async def navigate_and_extract(
        self,
        site: str,
        actions: list[dict],
    ) -> dict:
        """Execute a sequence of browser actions and extract data.

        Args:
            site: Target site identifier (e.g., "propertyguru", "99co", "hdb-infoweb")
            actions: List of action steps, e.g.:
                [
                    {"action": "navigate", "url": "https://..."},
                    {"action": "type", "selector": "#search", "value": "Tampines 4 room"},
                    {"action": "click", "selector": ".search-btn"},
                    {"action": "wait", "selector": ".results"},
                    {"action": "extract", "selector": ".listing-card", "fields": [...]}
                ]
        """
        if not self.api_key:
            return {"status": "skipped", "reason": "No ActionBook API key configured"}

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "site": site,
            "actions": actions,
            "options": {
                "headless": True,
                "timeout": 30000,
            },
        }

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{self.base_url}/execute",
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            return response.json()

    async def search_propertyguru(self, town: str, flat_type: str = "") -> dict:
        """Pre-built action sequence for searching PropertyGuru HDB listings."""
        query = f"{town} {flat_type} HDB".strip()

        actions = [
            {
                "action": "navigate",
                "url": "https://www.propertyguru.com.sg/property-for-sale?market=residential&property_type=H",
            },
            {
                "action": "type",
                "selector": "input[data-automation-id='search-input'], #search-input, .search-bar input",
                "value": query,
            },
            {
                "action": "click",
                "selector": "button[data-automation-id='search-btn'], .search-btn, button[type='submit']",
            },
            {
                "action": "wait",
                "selector": ".listing-card, .listing-widget-new, [data-listing-id]",
                "timeout": 10000,
            },
            {
                "action": "extract",
                "selector": ".listing-card, .listing-widget-new",
                "fields": [
                    {"name": "title", "selector": ".listing-title, h3 a", "attribute": "text"},
                    {"name": "price", "selector": ".listing-price, .price", "attribute": "text"},
                    {"name": "address", "selector": ".listing-address, .address", "attribute": "text"},
                    {"name": "details", "selector": ".listing-details, .details", "attribute": "text"},
                    {"name": "url", "selector": "a.listing-link, h3 a", "attribute": "href"},
                ],
            },
        ]

        return await self.navigate_and_extract("propertyguru", actions)

    async def search_99co(self, town: str, flat_type: str = "") -> dict:
        """Pre-built action sequence for searching 99.co HDB listings."""
        query = f"{town} {flat_type}".strip()

        actions = [
            {
                "action": "navigate",
                "url": f"https://www.99.co/singapore/sale/hdb?query={query}",
            },
            {
                "action": "wait",
                "selector": ".search-listing-card, .listing-card, [data-testid='listing-card']",
                "timeout": 10000,
            },
            {
                "action": "extract",
                "selector": ".search-listing-card, .listing-card",
                "fields": [
                    {"name": "title", "selector": ".listing-title, h3", "attribute": "text"},
                    {"name": "price", "selector": ".listing-price, .price", "attribute": "text"},
                    {"name": "address", "selector": ".listing-address", "attribute": "text"},
                    {"name": "details", "selector": ".listing-details", "attribute": "text"},
                    {"name": "url", "selector": "a", "attribute": "href"},
                ],
            },
        ]

        return await self.navigate_and_extract("99co", actions)

    async def check_hdb_resale_portal(self, town: str, flat_type: str) -> dict:
        """Navigate HDB's official resale price checker."""
        actions = [
            {
                "action": "navigate",
                "url": "https://services2.hdb.gov.sg/webapp/BB33RTIS/BB33PResl498.jsp",
            },
            {
                "action": "select",
                "selector": "#town, select[name='town']",
                "value": town,
            },
            {
                "action": "select",
                "selector": "#flatType, select[name='flatType']",
                "value": flat_type,
            },
            {
                "action": "click",
                "selector": "input[type='submit'], button[type='submit'], .submit-btn",
            },
            {
                "action": "wait",
                "selector": "table.result, .result-table, #result",
                "timeout": 10000,
            },
            {
                "action": "extract",
                "selector": "table.result tr, .result-table tr",
                "fields": [
                    {"name": "block", "selector": "td:nth-child(1)", "attribute": "text"},
                    {"name": "street", "selector": "td:nth-child(2)", "attribute": "text"},
                    {"name": "storey", "selector": "td:nth-child(3)", "attribute": "text"},
                    {"name": "area", "selector": "td:nth-child(4)", "attribute": "text"},
                    {"name": "price", "selector": "td:nth-child(5)", "attribute": "text"},
                ],
            },
        ]

        return await self.navigate_and_extract("hdb-infoweb", actions)


actionbook_client = ActionBookClient()
