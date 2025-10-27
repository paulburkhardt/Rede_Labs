"""Integration tests for purchase endpoint"""
import pytest


class TestPurchaseCreation:
    """Test purchase creation endpoint"""
    
    def test_purchase_product_success(self, client, sample_product, sample_buyer):
        """Test successful product purchase"""
        response = client.post(
            f"/buy/{sample_product['id']}",
            json={"productId": sample_product['id']},
            headers={"Authorization": f"Bearer {sample_buyer['auth_token']}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "id" in data
        assert "productId" in data
        assert data["productId"] == sample_product['id']
        assert len(data["id"]) > 0
    
    def test_purchase_without_auth(self, client, sample_product):
        """Test that purchase fails without authentication"""
        response = client.post(
            f"/buy/{sample_product['id']}",
            json={"productId": sample_product['id']}
        )
        
        assert response.status_code == 422  # Missing required header
    
    def test_purchase_with_invalid_token(self, client, sample_product):
        """Test that purchase fails with invalid buyer token"""
        response = client.post(
            f"/buy/{sample_product['id']}",
            json={"productId": sample_product['id']},
            headers={"Authorization": "Bearer invalid-buyer-token"}
        )
        
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid authentication token"
    
    def test_purchase_nonexistent_product(self, client, sample_buyer):
        """Test that purchasing nonexistent product fails"""
        response = client.post(
            "/buy/nonexistent-product-id",
            json={"productId": "nonexistent-product-id"},
            headers={"Authorization": f"Bearer {sample_buyer['auth_token']}"}
        )
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Product not found"
    
    def test_multiple_purchases_by_same_buyer(self, client, sample_product, sample_buyer):
        """Test that a buyer can make multiple purchases"""
        # First purchase
        response1 = client.post(
            f"/buy/{sample_product['id']}",
            json={"productId": sample_product['id']},
            headers={"Authorization": f"Bearer {sample_buyer['auth_token']}"}
        )
        assert response1.status_code == 200
        purchase1 = response1.json()
        
        # Second purchase of same product
        response2 = client.post(
            f"/buy/{sample_product['id']}",
            json={"productId": sample_product['id']},
            headers={"Authorization": f"Bearer {sample_buyer['auth_token']}"}
        )
        assert response2.status_code == 200
        purchase2 = response2.json()
        
        # Verify different purchase IDs
        assert purchase1["id"] != purchase2["id"]
        assert purchase1["productId"] == purchase2["productId"]
    
    def test_multiple_buyers_purchase_same_product(self, client, sample_product):
        """Test that multiple buyers can purchase the same product"""
        # Create two buyers
        buyer1 = client.post(
            "/createBuyer",
            json={"name": "Buyer One"}
        ).json()
        
        buyer2 = client.post(
            "/createBuyer",
            json={"name": "Buyer Two"}
        ).json()
        
        # Both purchase the same product
        response1 = client.post(
            f"/buy/{sample_product['id']}",
            json={"productId": sample_product['id']},
            headers={"Authorization": f"Bearer {buyer1['auth_token']}"}
        )
        
        response2 = client.post(
            f"/buy/{sample_product['id']}",
            json={"productId": sample_product['id']},
            headers={"Authorization": f"Bearer {buyer2['auth_token']}"}
        )
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Verify different purchase IDs
        assert response1.json()["id"] != response2.json()["id"]
    
    def test_seller_token_cannot_make_purchase(self, client, sample_product, sample_seller):
        """Test that seller token cannot be used to make purchases"""
        response = client.post(
            f"/buy/{sample_product['id']}",
            json={"productId": sample_product['id']},
            headers={"Authorization": f"Bearer {sample_seller['auth_token']}"}
        )
        
        # Should fail because seller token is not a buyer token
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid authentication token"


class TestPurchaseWorkflow:
    """Test complete purchase workflows"""
    
    def test_complete_marketplace_workflow(self, client):
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
                "shortDescription": "Luxurious and soft",
                "longDescription": "Made from 100% Egyptian cotton",
                "price": 3999,
                "image": {
                    "url": "https://example.com/premium-towel.jpg",
                    "alternativText": "White premium towel"
                }
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
        assert product_details["priceInCent"] == 3999
        
        # Step 5: Create buyer
        buyer = client.post(
            "/createBuyer",
            json={"name": "Jane Customer"}
        ).json()
        
        assert "auth_token" in buyer
        
        # Step 6: Make purchase
        purchase_response = client.post(
            "/buy/premium-towel",
            json={"productId": "premium-towel"},
            headers={"Authorization": f"Bearer {buyer['auth_token']}"}
        )
        
        assert purchase_response.status_code == 200
        purchase = purchase_response.json()
        assert purchase["productId"] == "premium-towel"
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
