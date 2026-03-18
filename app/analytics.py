import pandas as pd
from sqlalchemy.orm import Session
from .models import Sale

def get_sales_summary(db: Session):
    sales = db.query(Sale).all()

    if not sales:
        return {"message": "No data"}

    data = [{
        "product": s.product,
        "value": s.value,
        "date": s.date
    } for s in sales]

    df = pd.DataFrame(data)

    total_revenue = df["value"].sum()
    avg_ticket = round(df["value"].mean(), 2)

    top_product = (
        df.groupby("product")["value"]
        .sum()
        .sort_values(ascending=False)
        .idxmax()
    )

    sales_per_day = df.groupby("date")["value"].sum().to_dict()

    return {
        "total_revenue": round(float(total_revenue), 2),
        "average_ticket": round(float(avg_ticket), 2),
        "top_product": top_product,
        "sales_per_day": sales_per_day
    }