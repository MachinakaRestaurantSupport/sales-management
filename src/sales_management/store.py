"""In-memory store and aggregation logic for sales records."""

import uuid
from datetime import datetime

from sales_management.models import SalesRecord, SalesRecordCreate, SalesSummary


class DuplicateOrderError(Exception):
    """Raised when attempting to register a sales record with an existing order_id."""

    def __init__(self, order_id: str) -> None:
        self.order_id = order_id
        super().__init__(f"Sales record for order_id '{order_id}' already exists")


class SalesStore:
    """In-memory repository for sales records and period aggregations."""

    def __init__(self) -> None:
        self._records: dict[str, SalesRecord] = {}

    def add_record(self, payload: SalesRecordCreate) -> SalesRecord:
        """Register a new sales record, rejecting duplicate order_id."""
        if payload.order_id in self._records:
            raise DuplicateOrderError(payload.order_id)

        record = SalesRecord(
            id=str(uuid.uuid4()),
            order_id=payload.order_id,
            payment_id=payload.payment_id,
            channel=payload.channel,
            amount=payload.amount,
            recorded_at=payload.recorded_at,
        )
        self._records[payload.order_id] = record
        return record

    def summarize(self, period: str) -> SalesSummary:
        """Aggregate sales totals and channel breakdowns matching the given period prefix."""
        by_channel: dict[str, int] = {"dine_in": 0, "takeout": 0}
        total_amount = 0
        order_count = 0

        for record in self._records.values():
            record_date = datetime.fromisoformat(record.recorded_at).date().isoformat()
            if record_date.startswith(period):
                total_amount += record.amount
                order_count += 1
                by_channel[record.channel] += record.amount

        return SalesSummary(
            period=period,
            total_amount=total_amount,
            order_count=order_count,
            by_channel=by_channel,
        )

    def clear(self) -> None:
        """Remove all stored sales records."""
        self._records.clear()

    def list_records(self) -> list[SalesRecord]:
        """Return all stored sales records."""
        return list(self._records.values())
