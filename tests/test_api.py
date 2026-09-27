from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app


client = TestClient(app)


def setup_function():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def test_should_reject_negative_sale_values():
    response = client.post(
        "/sales",
        json={"product": "Mouse", "value": -10, "date": "2026-09-27"},
    )

    assert response.status_code == 422


def test_should_return_empty_analytics_when_no_sales_exist():
    response = client.get("/analytics")

    assert response.status_code == 200
    assert response.json() == {
        "total_revenue": 0.0,
        "average_ticket": 0.0,
        "top_product": None,
        "sales_per_day": {},
    }


def test_should_calculate_analytics_for_sales():
    client.post(
        "/sales",
        json={"product": "Keyboard", "value": 100, "date": "2026-09-27"},
    )
    client.post(
        "/sales",
        json={"product": "Keyboard", "value": 150, "date": "2026-09-27"},
    )
    client.post(
        "/sales",
        json={"product": "Monitor", "value": 200, "date": "2026-09-28"},
    )

    response = client.get("/analytics")

    assert response.status_code == 200
    payload = response.json()
    assert payload["total_revenue"] == 450.0
    assert payload["average_ticket"] == 150.0
    assert payload["top_product"] == "Keyboard"
    assert payload["sales_per_day"]["2026-09-27"] == 250.0
    assert payload["sales_per_day"]["2026-09-28"] == 200.0


def test_should_filter_sales_by_date_range_and_apply_pagination():
    dates = ["2026-09-01", "2026-09-02", "2026-09-03", "2026-09-04", "2026-09-05"]
    for index, sale_date in enumerate(dates, start=1):
        client.post(
            "/sales",
            json={"product": f"Product {index}", "value": float(index * 10), "date": sale_date},
        )

    response = client.get(
        "/sales",
        params={"start_date": "2026-09-02", "end_date": "2026-09-04", "skip": 1, "limit": 2},
    )

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 2
    assert [sale["date"] for sale in payload] == ["2026-09-03", "2026-09-02"]
