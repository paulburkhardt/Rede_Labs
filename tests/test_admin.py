"""Tests for admin metadata endpoints."""


class TestAdminDayEndpoints:
    """Ensure the admin day management API works as expected."""

    def test_get_day_defaults_to_zero(self, client, battle_id):
        response = client.get(f"/admin/day?battle_id={battle_id}")
        assert response.status_code == 200
        assert response.json() == {"day": 0}

    def test_update_day_persists_value(self, client, battle_id):
        update_response = client.post("/admin/day", json={"battle_id": battle_id, "day": 3})
        assert update_response.status_code == 200
        assert update_response.json() == {"day": 3}

        fetch_response = client.get(f"/admin/day?battle_id={battle_id}")
        assert fetch_response.status_code == 200
        assert fetch_response.json() == {"day": 3}

    def test_update_day_rejects_negative_values(self, client, battle_id):
        response = client.post("/admin/day", json={"battle_id": battle_id, "day": -1})
        assert response.status_code == 400
        assert "non-negative" in response.json()["detail"]


class TestAdminRoundEndpoints:
    """Ensure the admin round management API works as expected."""

    def test_get_round_defaults_to_one(self, client, battle_id):
        response = client.get(f"/admin/round?battle_id={battle_id}")
        assert response.status_code == 200
        assert response.json() == {"round": 1}

    def test_update_round_persists_value(self, client, battle_id):
        update_response = client.post("/admin/round", json={"battle_id": battle_id, "round": 3})
        assert update_response.status_code == 200
        assert update_response.json() == {"round": 3}

        fetch_response = client.get(f"/admin/round?battle_id={battle_id}")
        assert fetch_response.status_code == 200
        assert fetch_response.json() == {"round": 3}

    def test_update_round_rejects_values_below_one(self, client, battle_id):
        response = client.post("/admin/round", json={"battle_id": battle_id, "round": 0})
        assert response.status_code == 400
        assert "positive integer" in response.json()["detail"]

