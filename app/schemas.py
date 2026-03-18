from pydantic import BaseModel
from datetime import date

class SaleCreate(BaseModel):
    product: str
    value: float
    date: date

class SaleResponse(SaleCreate):
    id: int

    class Config:
        orm_mode = True