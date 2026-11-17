"""Unit tests for the sales-management service."""

from fastapi.testclient import TestClient

from sales_management.main import create_app


def _make_client() -> TestClient:
    return TestClient(create_app())


def test_health() -> None:
    """GET /health returns service status."""
    client = _make_client()
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "sales-management"}


def test_create_sales_record_and_reject_duplicate() -> None:
    """POST /sales/records creates a record (201) and rejects duplicate order_id (409)."""
    client = _make_client()
    payload = {
        "order_id": "ord-001",
        "payment_id": "pay-001",
        "channel": "dine_in",
        "amount": 2500,
        "recorded_at": "2026-11-16T12:30:00+09:00",
    }

    first = client.post("/sales/records", json=payload)
    assert first.status_code == 201
    body = first.json()
    assert body["id"]
    assert body["order_id"] == "ord-001"
    assert body["payment_id"] == "pay-001"
    assert body["channel"] == "dine_in"
    assert body["amount"] == 2500
    assert body["recorded_at"] == "2026-11-16T12:30:00+09:00"

    duplicate = client.post("/sales/records", json=payload)
    assert duplicate.status_code == 409


def test_create_sales_record_validation() -> None:
    """Invalid amount, channel, or recorded_at returns HTTP 422."""
    client = _make_client()

    bad_amount = client.post(
        "/sales/records",
        json={
            "order_id": "ord-neg",
            "payment_id": "pay-neg",
            "channel": "dine_in",
            "amount": -100,
            "recorded_at": "2026-11-16T12:30:00+09:00",
        },
    )
    assert bad_amount.status_code == 422

    bad_channel = client.post(
        "/sales/records",
        json={
            "order_id": "ord-ch",
            "payment_id": "pay-ch",
            "channel": "delivery",
            "amount": 1000,
            "recorded_at": "2026-11-16T12:30:00+09:00",
        },
    )
    assert bad_channel.status_code == 422

    bad_datetime = client.post(
        "/sales/records",
        json={
            "order_id": "ord-dt",
            "payment_id": "pay-dt",
            "channel": "takeout",
            "amount": 1000,
            "recorded_at": "not-a-date",
        },
    )
    assert bad_datetime.status_code == 422


def test_sales_summaries_daily_monthly_yearly_and_channels() -> None:
    """Daily, monthly, and yearly summaries aggregate totals, counts, and channels."""
    client = _make_client()
    records = [
        {
            "order_id": "ord-101",
            "payment_id": "pay-101",
            "channel": "dine_in",
            "amount": 1200,
            "recorded_at": "2026-11-16T11:00:00+09:00",
        },
        {
            "order_id": "ord-102",
            "payment_id": "pay-102",
            "channel": "takeout",
            "amount": 800,
            "recorded_at": "2026-11-16T13:15:00+09:00",
        },
        {
            "order_id": "ord-103",
            "payment_id": "pay-103",
            "channel": "dine_in",
            "amount": 3000,
            "recorded_at": "2026-11-20T19:00:00+09:00",
        },
        {
            "order_id": "ord-104",
            "payment_id": "pay-104",
            "channel": "takeout",
            "amount": 1500,
            "recorded_at": "2026-10-05T18:00:00+09:00",
        },
        {
            "order_id": "ord-105",
            "payment_id": "pay-105",
            "channel": "dine_in",
            "amount": 5000,
            "recorded_at": "2025-12-31T20:00:00+09:00",
        },
    ]

    for record in records:
        res = client.post("/sales/records", json=record)
        assert res.status_code == 201

    daily = client.get("/sales/summary/daily", params={"date": "2026-11-16"})
    assert daily.status_code == 200
    assert daily.json() == {
        "period": "2026-11-16",
        "total_amount": 2000,
        "order_count": 2,
        "by_channel": {"dine_in": 1200, "takeout": 800},
    }

    monthly = client.get("/sales/summary/monthly", params={"month": "2026-11"})
    assert monthly.status_code == 200
    assert monthly.json() == {
        "period": "2026-11",
        "total_amount": 5000,
        "order_count": 3,
        "by_channel": {"dine_in": 4200, "takeout": 800},
    }

    yearly = client.get("/sales/summary/yearly", params={"year": "2026"})
    assert yearly.status_code == 200
    assert yearly.json() == {
        "period": "2026",
        "total_amount": 6500,
        "order_count": 4,
        "by_channel": {"dine_in": 4200, "takeout": 2300},
    }

    empty_day = client.get("/sales/summary/daily", params={"date": "2026-01-01"})
    assert empty_day.status_code == 200
    assert empty_day.json() == {
        "period": "2026-01-01",
        "total_amount": 0,
        "order_count": 0,
        "by_channel": {"dine_in": 0, "takeout": 0},
    }


def test_summary_query_validation() -> None:
    """Invalid date/month/year query parameters return HTTP 422."""
    client = _make_client()
    assert client.get("/sales/summary/daily", params={"date": "2026-11"}).status_code == 422
    assert client.get("/sales/summary/monthly", params={"month": "2026"}).status_code == 422
    assert client.get("/sales/summary/yearly", params={"year": "26"}).status_code == 422


def test_sales_ui_screens() -> None:
    """Sales UI screens render daily, monthly, and records HTML views."""
    client = _make_client()
    client.post(
        "/sales/records",
        json={
            "order_id": "ord-ui-1",
            "payment_id": "pay-ui-1",
            "channel": "dine_in",
            "amount": 1500,
            "recorded_at": "2026-11-16T12:00:00+09:00",
        },
    )
    for path in ("/ui/sales/daily", "/ui/sales/monthly", "/ui/sales/records"):
        res = client.get(path)
        assert res.status_code == 200
        assert "売上管理" in res.text
