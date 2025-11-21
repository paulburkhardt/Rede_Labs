"""Integration tests for seller endpoints"""
import pytest


class TestSellerCreation:
    """Test seller creation endpoint"""
    
    def test_create_seller_success(self, client, battle_id):
        """Test successful seller creation"""
        response = client.post(
            "/createSeller",
            json={"battle_id": battle_id}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "id" in data
        assert "auth_token" in data
        
        # Verify values
        assert len(data["id"]) > 0
        assert len(data["auth_token"]) > 0
    
    def test_create_multiple_sellers(self, client, battle_id):
        """Test creating multiple sellers with unique tokens"""
        seller1 = client.post(
            "/createSeller",
            json={"battle_id": battle_id}
        ).json()
        
        seller2 = client.post(
            "/createSeller",
            json={"battle_id": battle_id}
        ).json()
        
        # Verify different IDs and tokens
        assert seller1["id"] != seller2["id"]
        assert seller1["auth_token"] != seller2["auth_token"]

    