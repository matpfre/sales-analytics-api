from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from .database import SessionLocal, engine, Base
from . import crud, schemas, analytics

Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/sales")
def create_sale(sale: schemas.SaleCreate, db: Session = Depends(get_db)):
    return crud.create_sale(db, sale)

@app.get("/sales")
def list_sales(db: Session = Depends(get_db)):
    return crud.get_sales(db)

@app.get("/analytics")
def analytics_data(db: Session = Depends(get_db)):
    return analytics.get_sales_summary(db)