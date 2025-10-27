"""Integration tests for buyer endpoints"""
import pytest


class TestBuyerCreation:
    """Test buyer creation endpoint"""
    
    def test_create_buyer_success(self, client):
        """Test successful buyer creation"""
        response = client.post(
            "/createBuyer",
            json={"name": "John Doe"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "id" in data
        assert "name" in data
        assert "auth_token" in data
        
        # Verify values
        assert data["name"] == "John Doe"
        assert len(data["id"]) > 0
        assert len(data["auth_token"]) > 0
    
    def test_create_multiple_buyers(self, client):
        """Test creating multiple buyers with unique tokens"""
        buyer1 = client.post(
            "/createBuyer",
            json={"name": "Alice"}
        ).json()
        
        buyer2 = client.post(
            "/createBuyer",
            json={"name": "Bob"}
        ).json()
        
        # Verify different IDs and tokens
        assert buyer1["id"] != buyer2["id"]
        assert buyer1["auth_token"] != buyer2["auth_token"]
        assert buyer1["name"] == "Alice"
        assert buyer2["name"] == "Bob"
    
    def test_buyer_token_is_unique(self, client):
        """Test that each buyer gets a unique authentication token"""
        buyers = []
        for i in range(5):
            response = client.post(
                "/createBuyer",
                json={"name": f"Buyer {i}"}
            )
            buyers.append(response.json())
        
        # Check all tokens are unique
        tokens = [b["auth_token"] for b in buyers]
        assert len(tokens) == len(set(tokens))
