def analyze_price(listing_price: int, town: str, flat_type: str, historical_data: list) -> dict:
    avg = sum(d["resale_price"] for d in historical_data) / len(historical_data)
    diff_pct = ((listing_price - avg) / avg) * 100

    if diff_pct > 5:
        verdict = "Overpriced"
        explanation = f"This listing is {diff_pct:+.1f}% above the recent average of SGD {avg:,.0f} for {flat_type} flats in {town}. Buyers should negotiate or consider nearby alternatives."
    elif diff_pct < -5:
        verdict = "Underpriced"
        explanation = f"This listing is {abs(diff_pct):.1f}% below the recent average of SGD {avg:,.0f} for {flat_type} flats in {town}. This represents good value — act fast."
    else:
        verdict = "Fair"
        explanation = f"This listing is priced within 5% of the recent average of SGD {avg:,.0f} for {flat_type} flats in {town}. Market-aligned pricing."

    return {
        "verdict": verdict,
        "explanation": explanation,
        "avg_price": round(avg),
        "diff_pct": round(diff_pct, 1)
    }
