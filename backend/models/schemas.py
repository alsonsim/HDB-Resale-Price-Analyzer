from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# --- Request schemas ---

class TransactionQuery(BaseModel):
    town: Optional[str] = None
    flat_type: Optional[str] = None
    month_from: Optional[str] = None
    month_to: Optional[str] = None
    limit: int = 100
    offset: int = 0


class AnalyzeRequest(BaseModel):
    town: str
    flat_type: str
    asking_price: float
    floor_area_sqm: Optional[float] = None
    storey_range: Optional[str] = None


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class AlertCreate(BaseModel):
    town: str
    flat_type: str
    max_price: float


class ScrapeRequest(BaseModel):
    source: str = "propertyguru"
    town: Optional[str] = None
    flat_type: Optional[str] = None
    max_pages: int = 3


# --- Response schemas ---

class TransactionResponse(BaseModel):
    id: int
    month: str
    town: str
    flat_type: str
    block: str
    street_name: str
    storey_range: str
    floor_area_sqm: float
    flat_model: str
    lease_commence_date: str
    remaining_lease: str
    resale_price: float
    price_per_sqm: Optional[float] = None

    model_config = {"from_attributes": True}


class TrendPoint(BaseModel):
    month: str
    median_price: float
    avg_price: float
    transaction_count: int
    avg_psm: float  # price per square meter


class TrendResponse(BaseModel):
    town: str
    flat_type: Optional[str] = None
    data: list[TrendPoint]


class AnalysisResult(BaseModel):
    is_fair: bool
    fair_price_range: tuple[float, float]
    price_vs_median_pct: float
    summary: str
    ai_insight: str
    comparable_transactions: list[TransactionResponse]


class ChatResponse(BaseModel):
    reply: str
    session_id: str
    data: Optional[dict] = None


class AlertResponse(BaseModel):
    id: int
    town: str
    flat_type: str
    max_price: float
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ListingResponse(BaseModel):
    id: int
    source: str
    url: str
    title: str
    town: str
    flat_type: str
    asking_price: float
    floor_area_sqm: Optional[float] = None
    storey: Optional[str] = None
    scraped_at: datetime

    model_config = {"from_attributes": True}
