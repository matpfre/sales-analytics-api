from __future__ import annotations

from datetime import date

from sqlalchemy.orm import Session

from . import models, schemas


def create_sale(db: Session, sale: schemas.SaleCreate):
    db_sale = models.Sale(**sale.model_dump())
    db.add(db_sale)
    db.commit()
    db.refresh(db_sale)
    return db_sale


def get_sales(db: Session, *, product: str | None = None, start_date: date | None = None, end_date: date | None = None, skip: int = 0, limit: int = 100):
    query = db.query(models.Sale)

    if product:
        query = query.filter(models.Sale.product.ilike(f"%{product}%"))
    if start_date:
        query = query.filter(models.Sale.date >= start_date)
    if end_date:
        query = query.filter(models.Sale.date <= end_date)

    return query.order_by(models.Sale.date.desc(), models.Sale.id.desc()).offset(skip).limit(limit).all()


def get_sale_by_id(db: Session, sale_id: int):
    return db.query(models.Sale).filter(models.Sale.id == sale_id).first()