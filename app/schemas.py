from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class SaleCreate(BaseModel):
    product: str = Field(..., min_length=1, max_length=255)
    value: float = Field(..., gt=0, description="Sale amount must be greater than zero.")
    date: date


class SaleResponse(SaleCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)


class AnalyticsResponse(BaseModel):
    total_revenue: float
    average_ticket: float
    total_sales: int
    top_product: str | None
    sales_per_day: dict[str, float]
    revenue_by_product: dict[str, float]