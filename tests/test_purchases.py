"""Integration tests for purchase endpoint"""
import pytest

from app.services.phase_manager import Phase


class TestPurchaseCreation:
    """Test purchase creation endpoint"""
    
    def test_purchase_product_success(
        self, client, sample_product, sample_buyer, set_phase
    ):
        """Test successful product purchase"""
        set_phase(Phase.BUYER_SHOPPING)
        response = client.post(
            f"/buy/{sample_product['id']}",
            headers={"Authorization": f"Bearer {sample_buyer['auth_token']}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "id" in data
        assert "product_id" in data
        assert data["product_id"] == sample_product['id']
        assert len(data["id"]) > 0

    def test_purchase_tracks_current_day(
        self,
        client,
        sample_product,
        sample_buyer,
        set_phase,
        set_day,
    ):
        """Ensure purchases record the current simulated day."""
        set_day(2)
        set_phase(Phase.BUYER_SHOPPING)
        purchase_response = client.post(
            f"/buy/{sample_product['id']}",
            headers={"Authorization": f"Bearer {sample_buyer['auth_token']}"}
        )

        assert purchase_response.status_code == 200

        stats_response = client.get(
            "/getSalesStats",
            headers={"Authorization": f"Bearer {sample_product['seller']['auth_token']}"}
        )
        assert stats_response.status_code == 200
        stats = stats_response.json()
        assert stats["purchases"]
        assert stats["purchases"][0]["purchased_at"] == 2
    
    def test_purchase_without_auth(self, client, sample_product, set_phase):
        """Test that purchase fails without authentication"""
        set_phase(Phase.BUYER_SHOPPING)
        response = client.post(
            f"/buy/{sample_product['id']}",
        )
        
        assert response.status_code == 422  # Missing required header
    
    def test_purchase_with_invalid_token(self, client, sample_product, set_phase):
        """Test that purchase fails with invalid buyer token"""
        set_phase(Phase.BUYER_SHOPPING)
        response = client.post(
            f"/buy/{sample_product['id']}",
            headers={"Authorization": "Bearer invalid-buyer-token"}
        )
        
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid authentication token"
    
    def test_purchase_nonexistent_product(
        self, client, sample_buyer, set_phase
    ):
        """Test that purchasing nonexistent product fails"""
        set_phase(Phase.BUYER_SHOPPING)
        response = client.post(
            "/buy/nonexistent-product-id",
            headers={"Authorization": f"Bearer {sample_buyer['auth_token']}"}
        )
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Product not found"
    
    def test_multiple_purchases_by_same_buyer(
        self, client, sample_product, sample_buyer, set_phase
    ):
        """Test that a buyer can make multiple purchases"""
        set_phase(Phase.BUYER_SHOPPING)
        # First purchase
        response1 = client.post(
            f"/buy/{sample_product['id']}",
            headers={"Authorization": f"Bearer {sample_buyer['auth_token']}"}
        )
        assert response1.status_code == 200
        purchase1 = response1.json()
        
        # Second purchase of same product
        response2 = client.post(
            f"/buy/{sample_product['id']}",
            headers={"Authorization": f"Bearer {sample_buyer['auth_token']}"}
        )
        assert response2.status_code == 200
        purchase2 = response2.json()
        
        # Verify different purchase IDs
        assert purchase1["id"] != purchase2["id"]
        assert purchase1["product_id"] == purchase2["product_id"]
    
    def test_multiple_buyers_purchase_same_product(
        self, client, sample_product, set_phase
    ):
        """Test that multiple buyers can purchase the same product"""
        # Create two buyers
        buyer1 = client.post(
            "/createBuyer",
        ).json()
        
        buyer2 = client.post(
            "/createBuyer",
        ).json()
        
        # Both purchase the same product
        set_phase(Phase.BUYER_SHOPPING)
        response1 = client.post(
            f"/buy/{sample_product['id']}",
            headers={"Authorization": f"Bearer {buyer1['auth_token']}"}
        )
        
        response2 = client.post(
            f"/buy/{sample_product['id']}",
            headers={"Authorization": f"Bearer {buyer2['auth_token']}"}
        )
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Verify different purchase IDs
        assert response1.json()["id"] != response2.json()["id"]
    
    def test_seller_token_cannot_make_purchase(
        self, client, sample_product, sample_seller, set_phase
    ):
        """Test that seller token cannot be used to make purchases"""
        set_phase(Phase.BUYER_SHOPPING)
        response = client.post(
            f"/buy/{sample_product['id']}",
            headers={"Authorization": f"Bearer {sample_seller['auth_token']}"}
        )
        
        # Should fail because seller token is not a buyer token
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid authentication token"

    def test_purchase_blocked_outside_buyer_phase(
        self, client, sample_product, sample_buyer, set_phase
    ):
        """Ensure purchases are rejected when marketplace is not in buyer phase"""
        set_phase(Phase.SELLER_MANAGEMENT)
        response = client.post(
            f"/buy/{sample_product['id']}",
            headers={"Authorization": f"Bearer {sample_buyer['auth_token']}"}
        )

        assert response.status_code == 403
        assert "phase" in response.json()["detail"]


class TestPurchaseWorkflow:
    """Test complete purchase workflows"""
    
    def test_complete_marketplace_workflow(self, client, sample_images, set_phase):
        """Test a complete workflow: create org, product, buyer, and purchase"""
        # Step 1: Create seller
        org = client.post(
            "/createSeller",
        ).json()
        
        assert "auth_token" in org
        
        # Step 2: Create product
        product_response = client.post(
            "/product/premium-towel",
            json={
                "name": "Premium Cotton Towel",
                "short_description": "Luxurious and soft",
                "long_description": "Made from 100% Egyptian cotton",
                "price": 3999,
                "image_ids": [sample_images["01"][0].id]
            },
            headers={"Authorization": f"Bearer {org['auth_token']}"}
        )
        assert product_response.status_code == 200
        
        # Step 3: Search for product
        search_response = client.get("/search?q=premium")
        assert search_response.status_code == 200
        search_results = search_response.json()
        assert len(search_results) == 1
        assert search_results[0]["name"] == "Premium Cotton Towel"
        
        # Step 4: Get product details
        product_details = client.get("/product/premium-towel").json()
        assert product_details["name"] == "Premium Cotton Towel"
        assert product_details["price_in_cent"] == 3999
        
        # Step 5: Create buyer
        buyer = client.post(
            "/createBuyer",
        ).json()
        
        assert "auth_token" in buyer
        
        # Step 6: Make purchase
        set_phase(Phase.BUYER_SHOPPING)
        purchase_response = client.post(
            "/buy/premium-towel",
            headers={"Authorization": f"Bearer {buyer['auth_token']}"}
        )
        
        assert purchase_response.status_code == 200
        purchase = purchase_response.json()
        assert purchase["product_id"] == "premium-towel"
        assert "id" in purchase
    
    def test_buyer_cannot_update_products(self, client, sample_product, sample_buyer):
        """Test that buyer token cannot be used to update products"""
        response = client.patch(
            f"/product/{sample_product['id']}",
            json={"price": 999},
            headers={"Authorization": f"Bearer {sample_buyer['auth_token']}"}
        )
        
        # Should fail because buyer token is not an seller token
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid authentication token"
