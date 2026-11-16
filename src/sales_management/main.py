"""FastAPI application entrypoint for the sales-management service."""

from typing import Annotated

from fastapi import FastAPI, HTTPException, Query, status

from sales_management.models import (
    HealthResponse,
    SalesRecord,
    SalesRecordCreate,
    SalesSummary,
)
from sales_management.store import DuplicateOrderError, SalesStore


def create_app(store: SalesStore | None = None) -> FastAPI:
    """Create and configure the FastAPI application."""
    application = FastAPI(title="Sales Management Service", version="0.1.0")
    sales_store = store or SalesStore()

    @application.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        return HealthResponse(status="ok", service="sales-management")

    @application.post(
        "/sales/records",
        response_model=SalesRecord,
        status_code=status.HTTP_201_CREATED,
    )
    def create_sales_record(payload: SalesRecordCreate) -> SalesRecord:
        try:
            return sales_store.add_record(payload)
        except DuplicateOrderError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(exc),
            ) from exc

    @application.get("/sales/summary/daily", response_model=SalesSummary)
    def get_daily_summary(
        date: Annotated[str, Query(pattern=r"^\d{4}-\d{2}-\d{2}$")],
    ) -> SalesSummary:
        return sales_store.summarize(date)

    @application.get("/sales/summary/monthly", response_model=SalesSummary)
    def get_monthly_summary(
        month: Annotated[str, Query(pattern=r"^\d{4}-\d{2}$")],
    ) -> SalesSummary:
        return sales_store.summarize(month)

    @application.get("/sales/summary/yearly", response_model=SalesSummary)
    def get_yearly_summary(
        year: Annotated[str, Query(pattern=r"^\d{4}$")],
    ) -> SalesSummary:
        return sales_store.summarize(year)

    return application


app = create_app()
