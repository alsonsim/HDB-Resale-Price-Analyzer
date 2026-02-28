import statistics

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.database import ResaleTransaction
from backend.models.schemas import AnalysisResult, TransactionResponse
from backend.agent.llm_client import llm_client
from backend.agent.prompts import PRICE_ANALYSIS_PROMPT, SYSTEM_PROMPT


class AnalyticsService:
    """Price analysis, trend computation, and fair value estimation."""

    async def analyze_price(
        self,
        db: AsyncSession,
        town: str,
        flat_type: str,
        asking_price: float,
        floor_area_sqm: float | None = None,
        storey_range: str | None = None,
    ) -> AnalysisResult:
        """Analyze whether a listing is fairly priced vs recent comparables."""
        town = town.upper()
        flat_type = flat_type.upper()

        # Fetch comparable transactions (same town + flat type, last 12 months)
        query = (
            select(ResaleTransaction)
            .where(
                and_(
                    ResaleTransaction.town == town,
                    ResaleTransaction.flat_type == flat_type,
                )
            )
            .order_by(ResaleTransaction.month.desc())
            .limit(50)
        )
        result = await db.execute(query)
        comparables = result.scalars().all()

        if not comparables:
            return AnalysisResult(
                is_fair=True,
                fair_price_range=(0, 0),
                price_vs_median_pct=0,
                summary="No comparable transactions found in the database. Try syncing data first.",
                ai_insight="Insufficient data to provide AI analysis.",
                comparable_transactions=[],
            )

        prices = [t.resale_price for t in comparables]
        median_price = statistics.median(prices)
        avg_price = statistics.mean(prices)
        min_price = min(prices)
        max_price = max(prices)
        std_dev = statistics.stdev(prices) if len(prices) > 1 else 0

        # Price per sqm analysis
        psm_values = [t.price_per_sqm for t in comparables if t.price_per_sqm]
        avg_psm = statistics.mean(psm_values) if psm_values else 0

        # Fair price range: median +/- 1 standard deviation
        fair_low = max(min_price, median_price - std_dev)
        fair_high = min(max_price, median_price + std_dev)

        # How does asking price compare
        price_vs_median_pct = round(((asking_price - median_price) / median_price) * 100, 1)
        is_fair = fair_low <= asking_price <= fair_high

        # Build comparable data string for AI prompt
        comparable_lines = []
        for t in comparables[:15]:
            comparable_lines.append(
                f"- {t.month} | {t.block} {t.street_name} | {t.storey_range} | "
                f"{t.floor_area_sqm}sqm | ${t.resale_price:,.0f} | "
                f"{t.flat_model} | Lease: {t.remaining_lease}"
            )

        period = f"{comparables[-1].month} to {comparables[0].month}"

        # Generate AI insight
        prompt = PRICE_ANALYSIS_PROMPT.format(
            town=town,
            flat_type=flat_type,
            asking_price=asking_price,
            floor_area_sqm=floor_area_sqm or "N/A",
            storey_range=storey_range or "N/A",
            comparable_data="\n".join(comparable_lines),
            median_price=median_price,
            avg_psm=avg_psm,
            min_price=min_price,
            max_price=max_price,
            txn_count=len(comparables),
            period=period,
        )

        try:
            ai_insight = await llm_client.generate(
                system_prompt=SYSTEM_PROMPT,
                user_message=prompt,
            )
        except Exception as e:
            ai_insight = (
                f"AI analysis unavailable: {e}\n\n"
                f"Based on data: The asking price of ${asking_price:,.0f} is "
                f"{'within' if is_fair else 'outside'} the fair range of "
                f"${fair_low:,.0f} - ${fair_high:,.0f}. "
                f"It is {abs(price_vs_median_pct):.1f}% "
                f"{'above' if price_vs_median_pct > 0 else 'below'} the median."
            )

        summary = (
            f"{'Fair price' if is_fair else 'Potentially overpriced' if price_vs_median_pct > 0 else 'Below market'} | "
            f"Asking: ${asking_price:,.0f} | Median: ${median_price:,.0f} | "
            f"{price_vs_median_pct:+.1f}% vs median | "
            f"Based on {len(comparables)} transactions ({period})"
        )

        comparable_responses = [
            TransactionResponse.model_validate(t) for t in comparables[:10]
        ]

        return AnalysisResult(
            is_fair=is_fair,
            fair_price_range=(round(fair_low), round(fair_high)),
            price_vs_median_pct=price_vs_median_pct,
            summary=summary,
            ai_insight=ai_insight,
            comparable_transactions=comparable_responses,
        )

    async def get_town_stats(self, db: AsyncSession, town: str) -> dict:
        """Get aggregate statistics for a town."""
        query = (
            select(
                ResaleTransaction.flat_type,
                func.count(ResaleTransaction.id).label("count"),
                func.avg(ResaleTransaction.resale_price).label("avg_price"),
                func.min(ResaleTransaction.resale_price).label("min_price"),
                func.max(ResaleTransaction.resale_price).label("max_price"),
                func.avg(ResaleTransaction.price_per_sqm).label("avg_psm"),
            )
            .where(ResaleTransaction.town == town.upper())
            .group_by(ResaleTransaction.flat_type)
        )
        result = await db.execute(query)
        rows = result.all()

        stats = {}
        for row in rows:
            stats[row.flat_type] = {
                "count": row.count,
                "avg_price": round(row.avg_price, 2),
                "min_price": row.min_price,
                "max_price": row.max_price,
                "avg_psm": round(row.avg_psm, 2) if row.avg_psm else None,
            }
        return stats


analytics_service = AnalyticsService()
