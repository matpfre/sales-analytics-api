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
