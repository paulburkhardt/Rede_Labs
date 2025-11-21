"""Integration tests for buyer endpoints"""
import pytest


class TestBuyerCreation:
    """Test buyer creation endpoint"""
    
    def test_create_buyer_success(self, client):
        """Test successful buyer creation"""
        payload = {"name": "Buyer One"}
        response = client.post(
            "/createBuyer",
            json=payload,
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "id" in data
        assert "auth_token" in data
        assert data["name"] == payload["name"]
        
        # Verify values
        assert len(data["id"]) > 0
        assert len(data["auth_token"]) > 0
    
    def test_create_multiple_buyers(self, client):
        """Test creating multiple buyers with unique tokens"""
        buyer1 = client.post(
            "/createBuyer",
            json={"name": "Buyer A"},
        ).json()
        
        buyer2 = client.post(
            "/createBuyer",
            json={"name": "Buyer B"},
        ).json()
        
        # Verify different IDs and tokens
        assert buyer1["id"] != buyer2["id"]
        assert buyer1["auth_token"] != buyer2["auth_token"]
        assert buyer1["name"] == "Buyer A"
        assert buyer2["name"] == "Buyer B"
    
    def test_buyer_token_is_unique(self, client):
        """Test that each buyer gets a unique authentication token"""
        buyers = []
        for i in range(5):
            response = client.post(
                "/createBuyer",
                json={"name": f"Buyer {i+1}"},
            )
            buyers.append(response.json())
        
        # Check all tokens are unique
        tokens = [b["auth_token"] for b in buyers]
        assert len(tokens) == len(set(tokens))

    def test_get_current_buyer_profile(self, client):
        """Verify that buyers can fetch their own profile using their token"""
        buyer = client.post(
            "/createBuyer",
            json={"name": "Profile Buyer"},
        ).json()

        response = client.get(
            "/buyer/me",
            headers={"Authorization": f"Bearer {buyer['auth_token']}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == buyer["id"]
        assert data["name"] == buyer["name"]
        assert data["auth_token"] == buyer["auth_token"]
