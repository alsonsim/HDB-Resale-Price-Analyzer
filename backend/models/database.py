from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, func
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from backend.config import settings


class Base(DeclarativeBase):
    pass


class ResaleTransaction(Base):
    __tablename__ = "resale_transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    month = Column(String, index=True)                # "2024-07"
    town = Column(String, index=True)                  # "TAMPINES"
    flat_type = Column(String, index=True)             # "4 ROOM"
    block = Column(String)                             # "406"
    street_name = Column(String)                       # "TAMPINES ST 41"
    storey_range = Column(String)                      # "07 TO 09"
    floor_area_sqm = Column(Float)                     # 93.0
    flat_model = Column(String)                        # "Model A"
    lease_commence_date = Column(String)               # "1985"
    remaining_lease = Column(String)                   # "61 years 04 months"
    resale_price = Column(Float)                       # 450000.0
    price_per_sqm = Column(Float, nullable=True)       # computed field
    created_at = Column(DateTime, server_default=func.now())


class LiveListing(Base):
    __tablename__ = "live_listings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String)                            # "propertyguru" | "99co"
    url = Column(String, unique=True)
    title = Column(String)
    town = Column(String, index=True)
    flat_type = Column(String, index=True)
    asking_price = Column(Float)
    floor_area_sqm = Column(Float, nullable=True)
    storey = Column(String, nullable=True)
    listed_date = Column(String, nullable=True)
    scraped_at = Column(DateTime, server_default=func.now())


class PriceAlert(Base):
    __tablename__ = "price_alerts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    town = Column(String, index=True)
    flat_type = Column(String)
    max_price = Column(Float)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())


engine = create_async_engine(settings.database_url, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    async with async_session() as session:
        yield session
