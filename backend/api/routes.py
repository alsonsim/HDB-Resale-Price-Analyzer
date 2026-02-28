from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.database import get_db, ResaleTransaction, LiveListing, PriceAlert
from backend.models.schemas import (
    TransactionQuery,
    TransactionResponse,
    TrendResponse,
    TrendPoint,
    AnalyzeRequest,
    AnalysisResult,
    ChatRequest,
    ChatResponse,
    AlertCreate,
    AlertResponse,
    ScrapeRequest,
    ListingResponse,
)
from backend.scrapers.datagov import datagov_client
from backend.services.analytics import analytics_service
from backend.agent.orchestrator import agent_orchestrator

router = APIRouter()


# --- Transactions ---

@router.get("/transactions", response_model=list[TransactionResponse])
async def get_transactions(
    town: str | None = Query(None),
    flat_type: str | None = Query(None),
    month_from: str | None = Query(None),
    month_to: str | None = Query(None),
    limit: int = Query(100, le=500),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db),
):
    """Query stored HDB resale transactions."""
    query = select(ResaleTransaction)

    conditions = []
    if town:
        conditions.append(ResaleTransaction.town == town.upper())
    if flat_type:
        conditions.append(ResaleTransaction.flat_type == flat_type.upper())
    if month_from:
        conditions.append(ResaleTransaction.month >= month_from)
    if month_to:
        conditions.append(ResaleTransaction.month <= month_to)

    if conditions:
        query = query.where(and_(*conditions))

    query = query.order_by(ResaleTransaction.month.desc()).limit(limit).offset(offset)
    result = await db.execute(query)
    return result.scalars().all()


# --- Trends ---

@router.get("/trends/{town}", response_model=TrendResponse)
async def get_trends(
    town: str,
    flat_type: str | None = Query(None),
    months: int = Query(24, le=120),
    db: AsyncSession = Depends(get_db),
):
    """Get monthly price trend data for a town."""
    conditions = [ResaleTransaction.town == town.upper()]
    if flat_type:
        conditions.append(ResaleTransaction.flat_type == flat_type.upper())

    query = (
        select(
            ResaleTransaction.month,
            func.avg(ResaleTransaction.resale_price).label("avg_price"),
            func.count(ResaleTransaction.id).label("count"),
            func.avg(ResaleTransaction.price_per_sqm).label("avg_psm"),
        )
        .where(and_(*conditions))
        .group_by(ResaleTransaction.month)
        .order_by(ResaleTransaction.month.desc())
        .limit(months)
    )
    result = await db.execute(query)
    rows = result.all()

    data = []
    for row in reversed(rows):
        data.append(
            TrendPoint(
                month=row.month,
                median_price=row.avg_price,  # using avg as approximation
                avg_price=round(row.avg_price, 2),
                transaction_count=row.count,
                avg_psm=round(row.avg_psm, 2) if row.avg_psm else 0,
            )
        )

    return TrendResponse(town=town.upper(), flat_type=flat_type, data=data)


# --- AI Analysis ---

@router.post("/analyze", response_model=AnalysisResult)
async def analyze_listing(
    request: AnalyzeRequest,
    db: AsyncSession = Depends(get_db),
):
    """Analyze whether a listing is fairly priced using AI."""
    return await analytics_service.analyze_price(
        db=db,
        town=request.town,
        flat_type=request.flat_type,
        asking_price=request.asking_price,
        floor_area_sqm=request.floor_area_sqm,
        storey_range=request.storey_range,
    )


# --- Chat ---

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    """Chat with the AI agent about HDB resale market."""
    return await agent_orchestrator.handle_query(
        message=request.message,
        session_id=request.session_id,
        db=db,
    )


# --- Scraping ---

@router.post("/scrape/listings")
async def scrape_listings(request: ScrapeRequest):
    """Trigger a live listing scrape from property portals."""
    from backend.scrapers.brightdata import brightdata_scraper

    results = await brightdata_scraper.scrape_listings(
        source=request.source,
        town=request.town,
        flat_type=request.flat_type,
        max_pages=request.max_pages,
    )
    return {"status": "ok", "listings_scraped": len(results)}


@router.post("/scrape/datagov")
async def sync_datagov(
    town: str | None = Query(None),
    limit: int = Query(1000, le=5000),
    db: AsyncSession = Depends(get_db),
):
    """Sync transactions from data.gov.sg into the local database."""
    data = await datagov_client.fetch_transactions(town=town, limit=limit)
    records = data["records"]

    count = 0
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
        count += 1

    await db.commit()
    return {"status": "ok", "records_synced": count, "total_available": data["total"]}


# --- Alerts ---

@router.get("/alerts", response_model=list[AlertResponse])
async def get_alerts(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(PriceAlert).where(PriceAlert.is_active == True).order_by(PriceAlert.created_at.desc())
    )
    return result.scalars().all()


@router.post("/alerts", response_model=AlertResponse)
async def create_alert(alert: AlertCreate, db: AsyncSession = Depends(get_db)):
    db_alert = PriceAlert(
        town=alert.town.upper(),
        flat_type=alert.flat_type.upper(),
        max_price=alert.max_price,
    )
    db.add(db_alert)
    await db.commit()
    await db.refresh(db_alert)
    return db_alert


@router.delete("/alerts/{alert_id}")
async def delete_alert(alert_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PriceAlert).where(PriceAlert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.is_active = False
    await db.commit()
    return {"status": "ok"}


# --- Metadata ---

@router.get("/towns")
async def get_towns():
    from backend.utils.helpers import HDB_TOWNS
    return {"towns": HDB_TOWNS}


@router.get("/flat-types")
async def get_flat_types():
    from backend.utils.helpers import HDB_FLAT_TYPES
    return {"flat_types": HDB_FLAT_TYPES}
