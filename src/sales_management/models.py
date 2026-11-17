"""Pydantic models for the sales-management service."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator

Channel = Literal["dine_in", "takeout"]


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str
    service: str


class SalesRecordCreate(BaseModel):
    """Request payload for creating a sales record."""

    order_id: str = Field(min_length=1)
    payment_id: str = Field(min_length=1)
    channel: Channel
    amount: int = Field(ge=0)
    recorded_at: str

    @field_validator("recorded_at")
    @classmethod
    def validate_iso8601(cls, value: str) -> str:
        """Ensure recorded_at is a valid ISO8601 datetime string."""
        datetime.fromisoformat(value)
        return value


class SalesRecord(BaseModel):
    """Stored sales record representation."""

    id: str
    order_id: str
    payment_id: str
    channel: Channel
    amount: int
    recorded_at: str


class SalesSummary(BaseModel):
    """Aggregated sales summary for a given period."""

    period: str
    total_amount: int
    order_count: int
    by_channel: dict[str, int]
