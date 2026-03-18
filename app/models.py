from sqlalchemy import Column, Integer, String, Float, Date
from .database import Base

class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    product = Column(String)
    value = Column(Float)
    date = Column(Date)