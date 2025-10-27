"""Integration tests for product endpoints"""
import pytest


class TestProductCreation:
    """Test product creation endpoint"""
    
    def test_create_product_success(self, client, sample_seller):
        """Test successful product creation with authentication"""
        product_data = {
            "name": "Premium Towel",
            "shortDescription": "Soft and absorbent",
            "longDescription": "Made from 100% organic cotton, perfect for daily use",
            "price": 2999,
            "image": {
                "url": "https://example.com/towel.jpg",
                "alternativText": "White towel on shelf"
            }
        }
        
        response = client.post(
            "/product/prod-123",
            json=product_data,
            headers={"Authorization": f"Bearer {sample_seller['auth_token']}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Product created successfully"
        assert data["product_id"] == "prod-123"
    
    def test_create_product_without_auth(self, client):
        """Test that product creation fails without authentication"""
        product_data = {
            "name": "Test Product",
            "shortDescription": "Test",
            "longDescription": "Test description",
            "price": 1000,
            "image": {
                "url": "https://example.com/test.jpg",
                "alternativText": "Test"
            }
        }
        
        response = client.post(
            "/product/prod-456",
            json=product_data
        )
        
        assert response.status_code == 422  # Missing required header
    
    def test_create_product_with_invalid_token(self, client):
        """Test that product creation fails with invalid token"""
        product_data = {
            "name": "Test Product",
            "shortDescription": "Test",
            "longDescription": "Test description",
            "price": 1000,
            "image": {
                "url": "https://example.com/test.jpg",
                "alternativText": "Test"
            }
        }
        
        response = client.post(
            "/product/prod-789",
            json=product_data,
            headers={"Authorization": "Bearer invalid-token-12345"}
        )
        
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid authentication token"
    
    def test_create_duplicate_product_id(self, client, sample_seller):
        """Test that creating a product with duplicate ID fails"""
        product_data = {
            "name": "Product One",
            "shortDescription": "First product",
            "longDescription": "Description",
            "price": 1000,
            "image": {
                "url": "https://example.com/1.jpg",
                "alternativText": "Image 1"
            }
        }
        
        # Create first product
        response1 = client.post(
            "/product/duplicate-id",
            json=product_data,
            headers={"Authorization": f"Bearer {sample_seller['auth_token']}"}
        )
        assert response1.status_code == 200
        
        # Try to create second product with same ID
        product_data["name"] = "Product Two"
        response2 = client.post(
            "/product/duplicate-id",
            json=product_data,
            headers={"Authorization": f"Bearer {sample_seller['auth_token']}"}
        )
        
        assert response2.status_code == 400
        assert "already exists" in response2.json()["detail"]


class TestProductUpdate:
    """Test product update endpoint"""
    
    def test_update_product_success(self, client, sample_product):
        """Test successful product update"""
        update_data = {
            "name": "Updated Product Name",
            "price": 2499
        }
        
        response = client.patch(
            f"/product/{sample_product['id']}",
            json=update_data,
            headers={"Authorization": f"Bearer {sample_product['seller']['auth_token']}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Product updated successfully"
        
        # Verify the update
        get_response = client.get(f"/product/{sample_product['id']}")
        product = get_response.json()
        assert product["name"] == "Updated Product Name"
        assert product["priceInCent"] == 2499
    
    def test_update_product_partial(self, client, sample_product):
        """Test partial product update (only some fields)"""
        update_data = {"price": 1599}
        
        response = client.patch(
            f"/product/{sample_product['id']}",
            json=update_data,
            headers={"Authorization": f"Bearer {sample_product['seller']['auth_token']}"}
        )
        
        assert response.status_code == 200
        
        # Verify only price changed
        get_response = client.get(f"/product/{sample_product['id']}")
        product = get_response.json()
        assert product["priceInCent"] == 1599
        assert product["name"] == sample_product["name"]  # Unchanged
    
    def test_update_product_without_auth(self, client, sample_product):
        """Test that product update fails without authentication"""
        response = client.patch(
            f"/product/{sample_product['id']}",
            json={"price": 999}
        )
        
        assert response.status_code == 422  # Missing required header
    
    def test_update_product_with_wrong_org_token(self, client, sample_product, sample_seller):
        """Test that seller cannot update another seller's product"""
        # Create a second seller
        other_org = client.post(
            "/createSeller",
            json={"name": "Other Corp"}
        ).json()
        
        # Try to update first org's product with second org's token
        response = client.patch(
            f"/product/{sample_product['id']}",
            json={"price": 999},
            headers={"Authorization": f"Bearer {other_org['auth_token']}"}
        )
        
        assert response.status_code == 403
        assert "only update your own products" in response.json()["detail"]
    
    def test_update_nonexistent_product(self, client, sample_seller):
        """Test updating a product that doesn't exist"""
        response = client.patch(
            "/product/nonexistent-id",
            json={"price": 999},
            headers={"Authorization": f"Bearer {sample_seller['auth_token']}"}
        )
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Product not found"


class TestProductRetrieval:
    """Test product retrieval endpoint"""
    
    def test_get_product_success(self, client, sample_product):
        """Test successful product retrieval"""
        response = client.get(f"/product/{sample_product['id']}")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure
        assert data["id"] == sample_product["id"]
        assert data["name"] == sample_product["name"]
        assert data["shortDescription"] == sample_product["shortDescription"]
        assert data["longDescription"] == sample_product["longDescription"]
        assert data["priceInCent"] == sample_product["price"]
        assert data["currency"] == "USD"
        assert "company" in data
        assert data["company"]["name"] == ""  # Sellers no longer have names
        assert "image" in data
    
    def test_get_nonexistent_product(self, client):
        """Test retrieving a product that doesn't exist"""
        response = client.get("/product/nonexistent-product-id")
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Product not found"
    
    def test_get_product_includes_seller_info(self, client, sample_product):
        """Test that product details include seller information"""
        response = client.get(f"/product/{sample_product['id']}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "company" in data
        assert "id" in data["company"]
        assert "name" in data["company"]
        assert data["company"]["id"] == sample_product["seller"]["id"]
        assert data["company"]["name"] == ""  # Sellers no longer have names
