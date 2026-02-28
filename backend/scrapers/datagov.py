import httpx

from backend.config import settings


class DataGovClient:
    """Client for Singapore's data.gov.sg HDB resale flat prices API."""

    def __init__(self):
        self.base_url = settings.datagov_base_url
        self.dataset_id = settings.datagov_dataset_id

    async def fetch_transactions(
        self,
        town: str | None = None,
        flat_type: str | None = None,
        month: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> dict:
        """Fetch HDB resale transactions from data.gov.sg.

        Args:
            town: Filter by town (e.g. "TAMPINES")
            flat_type: Filter by flat type (e.g. "4 ROOM")
            month: Filter by month (e.g. "2024-07")
            limit: Number of records per page (max 1000)
            offset: Record offset for pagination
        """
        params = {
            "resource_id": self.dataset_id,
            "limit": min(limit, 1000),
            "offset": offset,
        }

        filters = {}
        if town:
            filters["town"] = town.upper()
        if flat_type:
            filters["flat_type"] = flat_type.upper()
        if month:
            filters["month"] = month

        if filters:
            import json
            params["filters"] = json.dumps(filters)

        params["sort"] = "month desc, resale_price desc"

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()

        result = data.get("result", {})
        return {
            "records": result.get("records", []),
            "total": result.get("total", 0),
            "limit": limit,
            "offset": offset,
        }

    async def fetch_all_for_town(
        self,
        town: str,
        flat_type: str | None = None,
        months_back: int = 12,
    ) -> list[dict]:
        """Fetch all recent transactions for a town (paginated)."""
        all_records = []
        offset = 0
        batch_size = 500

        while True:
            result = await self.fetch_transactions(
                town=town,
                flat_type=flat_type,
                limit=batch_size,
                offset=offset,
            )
            records = result["records"]
            if not records:
                break

            all_records.extend(records)
            offset += batch_size

            if offset >= result["total"]:
                break

        # Filter to recent months if needed
        if months_back:
            from datetime import datetime, timedelta

            cutoff = (
                datetime.now() - timedelta(days=months_back * 30)
            ).strftime("%Y-%m")
            all_records = [r for r in all_records if r.get("month", "") >= cutoff]

        return all_records

    async def fetch_bulk(self, limit: int = 5000, offset: int = 0) -> dict:
        """Fetch a large batch for seeding the database."""
        return await self.fetch_transactions(limit=limit, offset=offset)


datagov_client = DataGovClient()
