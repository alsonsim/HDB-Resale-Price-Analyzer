from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.database import PriceAlert, ResaleTransaction, LiveListing


class AlertService:
    """Monitor price alerts and notify when matching listings are found."""

    async def check_alerts(self, db: AsyncSession) -> list[dict]:
        """Check all active alerts against recent transactions and listings."""
        result = await db.execute(
            select(PriceAlert).where(PriceAlert.is_active == True)
        )
        alerts = result.scalars().all()

        triggered = []

        for alert in alerts:
            matches = await self._find_matches(db, alert)
            if matches:
                triggered.append({
                    "alert_id": alert.id,
                    "town": alert.town,
                    "flat_type": alert.flat_type,
                    "max_price": alert.max_price,
                    "matches": matches,
                })

        return triggered

    async def _find_matches(self, db: AsyncSession, alert: PriceAlert) -> list[dict]:
        """Find transactions or listings that match an alert's criteria."""
        matches = []

        # Check recent transactions
        txn_query = (
            select(ResaleTransaction)
            .where(
                and_(
                    ResaleTransaction.town == alert.town,
                    ResaleTransaction.flat_type == alert.flat_type,
                    ResaleTransaction.resale_price <= alert.max_price,
                )
            )
            .order_by(ResaleTransaction.month.desc())
            .limit(5)
        )
        txn_result = await db.execute(txn_query)
        for txn in txn_result.scalars():
            matches.append({
                "type": "transaction",
                "month": txn.month,
                "address": f"{txn.block} {txn.street_name}",
                "price": txn.resale_price,
                "floor_area_sqm": txn.floor_area_sqm,
                "storey_range": txn.storey_range,
            })

        # Check live listings
        listing_query = (
            select(LiveListing)
            .where(
                and_(
                    LiveListing.town == alert.town,
                    LiveListing.flat_type == alert.flat_type,
                    LiveListing.asking_price <= alert.max_price,
                )
            )
            .order_by(LiveListing.scraped_at.desc())
            .limit(5)
        )
        listing_result = await db.execute(listing_query)
        for listing in listing_result.scalars():
            matches.append({
                "type": "listing",
                "source": listing.source,
                "title": listing.title,
                "price": listing.asking_price,
                "url": listing.url,
            })

        return matches


alert_service = AlertService()
