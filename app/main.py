from fastapi import Depends, FastAPI, HTTPException, Query, status
from sqlalchemy.orm import Session

from . import analytics, crud, schemas
from .database import Base, SessionLocal, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sales Analytics API",
    version="1.1.0",
    description="API para cadastro e análise de vendas.",
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/sales", response_model=schemas.SaleResponse, status_code=status.HTTP_201_CREATED)
def create_sale(sale: schemas.SaleCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_sale(db, sale)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error creating sale: {exc}") from exc


@app.get("/sales", response_model=list[schemas.SaleResponse])
def list_sales(
    db: Session = Depends(get_db),
    product: str | None = Query(default=None, description="Filter by product name"),
):
    sales = crud.get_sales(db)
    if product is not None:
        sales = [sale for sale in sales if sale.product.lower() == product.lower()]
    return sales


@app.get("/analytics", response_model=schemas.AnalyticsResponse)
def analytics_data(db: Session = Depends(get_db)):
    return analytics.get_sales_summary(db)