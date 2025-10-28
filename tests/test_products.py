"""Integration tests for product endpoints"""
import pytest


class TestProductCreation:
    """Test product creation endpoint"""
    
    def test_create_product_success(self, client, sample_seller):
        """Test successful product creation with authentication"""
        product_data = {
            "name": "Premium Towel",
            "short_description": "Soft and absorbent",
            "long_description": "Made from 100% organic cotton, perfect for daily use",
            "price": 2999,
            "image": {
                "url": "https://example.com/towel.jpg",
                "alternative_text": "White towel on shelf"
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
            "short_description": "Test",
            "long_description": "Test description",
            "price": 1000,
            "image": {
                "url": "https://example.com/test.jpg",
                "alternative_text": "Test"
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
            "short_description": "Test",
            "long_description": "Test description",
            "price": 1000,
            "image": {
                "url": "https://example.com/test.jpg",
                "alternative_text": "Test"
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
            "short_description": "First product",
            "long_description": "Description",
            "price": 1000,
            "image": {
                "url": "https://example.com/1.jpg",
                "alternative_text": "Image 1"
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
        assert product["price_in_cent"] == 2499
    
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
        assert product["price_in_cent"] == 1599
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
        assert data["short_description"] == sample_product["short_description"]
        assert data["long_description"] == sample_product["long_description"]
        assert data["price_in_cent"] == sample_product["price"]
        assert data["currency"] == "USD"
        assert "seller_id" in data
        assert data["seller_id"] == sample_product["seller"]["id"]
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
        
        assert "seller_id" in data
        assert data["seller_id"] == sample_product["seller"]["id"]


class TestProductRanking:
    """Test product ranking endpoints"""
    
    def test_update_single_product_ranking(self, client, sample_product):
        """Test updating a single product's ranking"""
        response = client.patch(
            f"/product/{sample_product['id']}/ranking",
            params={"ranking": 5}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Product ranking updated successfully"
        assert data["product_id"] == sample_product["id"]
        assert data["ranking"] == 5
    
    def test_update_single_ranking_nonexistent_product(self, client):
        """Test updating ranking for a product that doesn't exist"""
        response = client.patch(
            "/product/nonexistent-id/ranking",
            params={"ranking": 3}
        )
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Product not found"
    
    def test_batch_update_product_rankings_success(self, client, sample_seller):
        """Test batch updating multiple product rankings"""
        # Create multiple products
        products = []
        for i in range(3):
            product_data = {
                "name": f"Product {i}",
                "short_description": f"Description {i}",
                "long_description": f"Long description {i}",
                "price": 1000 + i * 100,
                "image": {
                    "url": f"https://example.com/product{i}.jpg",
                    "alternative_text": f"Product {i}"
                }
            }
            create_response = client.post(
                f"/product/batch-test-{i}",
                json=product_data,
                headers={"Authorization": f"Bearer {sample_seller['auth_token']}"}
            )
            assert create_response.status_code == 200
            products.append(f"batch-test-{i}")
        
        # Batch update rankings
        batch_data = {
            "rankings": [
                {"product_id": products[0], "ranking": 1},
                {"product_id": products[1], "ranking": 2},
                {"product_id": products[2], "ranking": 3}
            ]
        }
        
        response = client.patch(
            "/product/batch/rankings",
            json=batch_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "Updated 3 product rankings" in data["message"]
        assert data["updated_count"] == 3
        assert data["errors"] is None
    
    def test_batch_update_with_nonexistent_products(self, client, sample_product):
        """Test batch update with mix of existing and nonexistent products"""
        batch_data = {
            "rankings": [
                {"product_id": sample_product["id"], "ranking": 1},
                {"product_id": "nonexistent-1", "ranking": 2},
                {"product_id": "nonexistent-2", "ranking": 3}
            ]
        }
        
        response = client.patch(
            "/product/batch/rankings",
            json=batch_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["updated_count"] == 1  # Only the existing product updated
        assert data["errors"] is not None
        assert len(data["errors"]) == 2
        assert "nonexistent-1" in data["errors"][0]
        assert "nonexistent-2" in data["errors"][1]
    
    def test_batch_update_empty_list(self, client):
        """Test batch update with empty rankings list"""
        batch_data = {"rankings": []}
        
        response = client.patch(
            "/product/batch/rankings",
            json=batch_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["updated_count"] == 0
    
    def test_ranking_in_update_endpoint(self, client, sample_product):
        """Test that ranking can be updated via the regular product update endpoint"""
        update_data = {
            "name": "Updated Name",
            "ranking": 10
        }
        
        response = client.patch(
            f"/product/{sample_product['id']}",
            json=update_data,
            headers={"Authorization": f"Bearer {sample_product['seller']['auth_token']}"}
        )
        
        assert response.status_code == 200
        
        # Verify the ranking was updated (check via search endpoint)
        search_response = client.get(f"/search?q={update_data['name']}")
        assert search_response.status_code == 200
        results = search_response.json()
        
        # Find our product in results
        product = next((p for p in results if p["id"] == sample_product["id"]), None)
        assert product is not None
        assert product["ranking"] == 10
    
    def test_ranking_persists_in_search_results(self, client, sample_seller):
        """Test that rankings are returned in search results"""
        # Create product
        product_data = {
            "name": "Ranked Product",
            "short_description": "Test ranking",
            "long_description": "Test ranking persistence",
            "price": 1500,
            "image": {
                "url": "https://example.com/ranked.jpg",
                "alternative_text": "Ranked"
            }
        }
        
        create_response = client.post(
            "/product/ranked-product-1",
            json=product_data,
            headers={"Authorization": f"Bearer {sample_seller['auth_token']}"}
        )
        assert create_response.status_code == 200
        
        # Set ranking
        rank_response = client.patch(
            "/product/ranked-product-1/ranking",
            params={"ranking": 42}
        )
        assert rank_response.status_code == 200
        
        # Search and verify ranking appears
        search_response = client.get("/search?q=Ranked")
        assert search_response.status_code == 200
        results = search_response.json()
        
        product = next((p for p in results if p["id"] == "ranked-product-1"), None)
        assert product is not None
        assert product["ranking"] == 42
    
    def test_ranking_not_in_product_details(self, client, sample_product):
        """Test that ranking is NOT returned in product detail endpoint"""
        # Set a ranking first
        client.patch(
            f"/product/{sample_product['id']}/ranking",
            params={"ranking": 7}
        )
        
        # Get product details
        response = client.get(f"/product/{sample_product['id']}")
        assert response.status_code == 200
        data = response.json()
        
        # Verify ranking is not in the response
        assert "ranking" not in data


class TestRankingWithPurchaseStats:
    """Test ranking updates based on purchase statistics"""
    
    def test_update_rankings_based_on_purchase_stats(self, client):
        """Test complete workflow: create sellers, products, purchases, update rankings"""
        # Create two sellers
        seller1 = client.post("/createSeller").json()
        seller2 = client.post("/createSeller").json()
        
        # Create buyer
        buyer = client.post("/createBuyer", json={"name": "Test Buyer"}).json()
        
        # Create products for each seller
        product1_data = {
            "name": "Popular Product",
            "short_description": "Best seller",
            "long_description": "This will have more purchases",
            "price": 1000,
            "image": {"url": "https://example.com/p1.jpg", "alternative_text": "P1"}
        }
        client.post(
            "/product/popular-1",
            json=product1_data,
            headers={"Authorization": f"Bearer {seller1['auth_token']}"}
        )
        
        product2_data = {
            "name": "Less Popular Product",
            "short_description": "Fewer sales",
            "long_description": "This will have fewer purchases",
            "price": 1000,
            "image": {"url": "https://example.com/p2.jpg", "alternative_text": "P2"}
        }
        client.post(
            "/product/unpopular-1",
            json=product2_data,
            headers={"Authorization": f"Bearer {seller2['auth_token']}"}
        )
        
        # Make purchases - more for product1
        for _ in range(5):
            client.post(
                "/buy/popular-1",
                json={"product_id": "popular-1"},
                headers={"Authorization": f"Bearer {buyer['auth_token']}"}
            )
        
        for _ in range(2):
            client.post(
                "/buy/unpopular-1",
                json={"product_id": "unpopular-1"},
                headers={"Authorization": f"Bearer {buyer['auth_token']}"}
            )
        
        # Get purchase stats
        stats_response = client.get("/buy/stats/by-seller")
        assert stats_response.status_code == 200
        stats = stats_response.json()
        
        # Verify stats
        assert len(stats) == 2
        seller1_stats = next(s for s in stats if s["seller_id"] == seller1["id"])
        seller2_stats = next(s for s in stats if s["seller_id"] == seller2["id"])
        assert seller1_stats["purchase_count"] == 5
        assert seller2_stats["purchase_count"] == 2
        
        # Sort and assign rankings
        sorted_stats = sorted(stats, key=lambda x: x["purchase_count"], reverse=True)
        rankings = []
        for rank, stat in enumerate(sorted_stats, start=1):
            # Get products for this seller
            search_response = client.get(f"/search?q=")
            products = [p for p in search_response.json() if p["seller_id"] == stat["seller_id"]]
            for product in products:
                rankings.append({"product_id": product["id"], "ranking": rank})
        
        # Batch update rankings
        batch_response = client.patch(
            "/product/batch/rankings",
            json={"rankings": rankings}
        )
        assert batch_response.status_code == 200
        assert batch_response.json()["updated_count"] == 2
        
        # Verify rankings in search results
        search_response = client.get("/search?q=")
        products = search_response.json()
        
        popular_product = next(p for p in products if p["id"] == "popular-1")
        unpopular_product = next(p for p in products if p["id"] == "unpopular-1")
        
        assert popular_product["ranking"] == 1  # More purchases = better rank
        assert unpopular_product["ranking"] == 2  # Fewer purchases = worse rank
