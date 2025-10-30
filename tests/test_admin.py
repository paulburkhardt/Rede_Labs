"""Tests for admin metadata endpoints."""


class TestAdminDayEndpoints:
    """Ensure the admin day management API works as expected."""

    def test_get_day_defaults_to_zero(self, client):
        response = client.get("/admin/day")
        assert response.status_code == 200
        assert response.json() == {"day": 0}

    def test_update_day_persists_value(self, client):
        update_response = client.post("/admin/day", json={"day": 3})
        assert update_response.status_code == 200
        assert update_response.json() == {"day": 3}

        fetch_response = client.get("/admin/day")
        assert fetch_response.status_code == 200
        assert fetch_response.json() == {"day": 3}

    def test_update_day_rejects_negative_values(self, client):
        response = client.post("/admin/day", json={"day": -1})
        assert response.status_code == 400
        assert "non-negative" in response.json()["detail"]
