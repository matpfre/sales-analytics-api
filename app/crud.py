from __future__ import annotations

from sqlalchemy.orm import Session

from . import models, schemas


def create_sale(db: Session, sale: schemas.SaleCreate):
    db_sale = models.Sale(**sale.model_dump())
    db.add(db_sale)
    db.commit()
    db.refresh(db_sale)
    return db_sale


def get_sales(db: Session):
    return db.query(models.Sale).order_by(models.Sale.date.desc(), models.Sale.id.desc()).all()


def get_sale_by_id(db: Session, sale_id: int):
    return db.query(models.Sale).filter(models.Sale.id == sale_id).first()