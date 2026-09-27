from datetime import date

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
    start_date: date | None = Query(default=None, description="Start date for filtering"),
    end_date: date | None = Query(default=None, description="End date for filtering"),
    skip: int = Query(default=0, ge=0, description="Number of rows to skip"),
    limit: int = Query(default=100, ge=1, le=1000, description="Maximum number of rows to return"),
):
    return crud.get_sales(
        db,
        product=product,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit,
    )


@app.get("/analytics", response_model=schemas.AnalyticsResponse)
def analytics_data(db: Session = Depends(get_db)):
    return analytics.get_sales_summary(db)