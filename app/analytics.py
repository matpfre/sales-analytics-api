from __future__ import annotations

from collections import defaultdict

from sqlalchemy import func
from sqlalchemy.orm import Session

from .models import Sale


def get_sales_summary(db: Session):
    sales = db.query(Sale).all()

    if not sales:
        return {
            "total_revenue": 0.0,
            "average_ticket": 0.0,
            "top_product": None,
            "sales_per_day": {},
        }

    total_revenue = sum(float(sale.value) for sale in sales)
    average_ticket = total_revenue / len(sales)

    product_totals: dict[str, float] = defaultdict(float)
    sales_per_day: dict[str, float] = defaultdict(float)

    for sale in sales:
        product_totals[sale.product] += float(sale.value)
        sales_per_day[sale.date.isoformat()] += float(sale.value)

    top_product = (
        max(product_totals.items(), key=lambda item: item[1])[0]
        if product_totals
        else None
    )

    return {
        "total_revenue": round(total_revenue, 2),
        "average_ticket": round(average_ticket, 2),
        "top_product": top_product,
        "sales_per_day": {day: round(value, 2) for day, value in sorted(sales_per_day.items())},
    }