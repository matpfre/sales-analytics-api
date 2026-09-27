from sqlalchemy import Column, Date, Float, Integer, String

from .database import Base


class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    product = Column(String(255), nullable=False, index=True)
    value = Column(Float, nullable=False)
    date = Column(Date, nullable=False, index=True)