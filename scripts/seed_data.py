"""Seed the database with historical HDB resale transaction data from data.gov.sg."""

import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.models.database import init_db, async_session, ResaleTransaction
from backend.scrapers.datagov import datagov_client


async def seed(total_records: int = 10000):
    """Fetch and store HDB resale data from data.gov.sg."""
    print("Initializing database...")
    await init_db()

    print(f"Fetching up to {total_records} records from data.gov.sg...")

    batch_size = 1000
    offset = 0
    total_inserted = 0

    async with async_session() as db:
        while offset < total_records:
            limit = min(batch_size, total_records - offset)
            print(f"  Fetching batch: offset={offset}, limit={limit}")

            try:
                data = await datagov_client.fetch_transactions(limit=limit, offset=offset)
            except Exception as e:
                print(f"  Error fetching data: {e}")
                break

            records = data["records"]
            if not records:
                print("  No more records available.")
                break

            for record in records:
                area = float(record.get("floor_area_sqm", 0))
                price = float(record.get("resale_price", 0))

                txn = ResaleTransaction(
                    month=record.get("month", ""),
                    town=record.get("town", ""),
                    flat_type=record.get("flat_type", ""),
                    block=record.get("block", ""),
                    street_name=record.get("street_name", ""),
                    storey_range=record.get("storey_range", ""),
                    floor_area_sqm=area,
                    flat_model=record.get("flat_model", ""),
                    lease_commence_date=record.get("lease_commence_date", ""),
                    remaining_lease=record.get("remaining_lease", ""),
                    resale_price=price,
                    price_per_sqm=round(price / area, 2) if area > 0 else None,
                )
                db.add(txn)

            await db.commit()
            batch_count = len(records)
            total_inserted += batch_count
            offset += batch_size

            print(f"  Inserted {batch_count} records (total: {total_inserted})")

            if offset >= data.get("total", total_records):
                break

    print(f"\nDone! Total records seeded: {total_inserted}")
    print("Database: agentforge.db")


if __name__ == "__main__":
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 10000
    asyncio.run(seed(count))
