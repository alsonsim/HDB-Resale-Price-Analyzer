from datetime import datetime


# All 26 HDB towns in Singapore
HDB_TOWNS = [
    "ANG MO KIO", "BEDOK", "BISHAN", "BUKIT BATOK", "BUKIT MERAH",
    "BUKIT PANJANG", "BUKIT TIMAH", "CENTRAL AREA", "CHOA CHU KANG",
    "CLEMENTI", "GEYLANG", "HOUGANG", "JURONG EAST", "JURONG WEST",
    "KALLANG/WHAMPOA", "MARINE PARADE", "PASIR RIS", "PUNGGOL",
    "QUEENSTOWN", "SEMBAWANG", "SENGKANG", "SERANGOON", "TAMPINES",
    "TOA PAYOH", "WOODLANDS", "YISHUN",
]

HDB_FLAT_TYPES = [
    "1 ROOM", "2 ROOM", "3 ROOM", "4 ROOM", "5 ROOM",
    "EXECUTIVE", "MULTI-GENERATION",
]


def remaining_lease_to_months(remaining_lease: str) -> int:
    """Convert '61 years 04 months' to total months."""
    years = 0
    months = 0
    parts = remaining_lease.split()
    for i, part in enumerate(parts):
        if part == "years" or part == "year":
            years = int(parts[i - 1])
        elif part == "months" or part == "month":
            months = int(parts[i - 1])
    return years * 12 + months


def compute_price_per_sqm(price: float, area: float) -> float | None:
    if area and area > 0:
        return round(price / area, 2)
    return None


def current_month_str() -> str:
    return datetime.now().strftime("%Y-%m")
