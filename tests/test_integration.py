"""Integration tests for complex scenarios and edge cases"""
import pytest


class TestAuthenticationSecurity:
    """Test authentication and authorization security"""
    
    def test_bearer_token_with_and_without_prefix(self, client, sample_seller):
        """Test that both 'Bearer token' and 'token' formats work"""
        product_data = {
            "name": "Test Product",
            "shortDescription": "Test",
            "longDescription": "Test",
            "price": 1999,
            "image": {
                "url": "https://example.com/img.jpg",
                "alternativText": "Test"
            }
        }
        
        # Test with "Bearer " prefix
        response1 = client.post(
            "/product/test-1",
            json=product_data,
            headers={"Authorization": f"Bearer {sample_seller['auth_token']}"}
        )
        assert response1.status_code == 200
        
        # Test without "Bearer " prefix
        response2 = client.post(
            "/product/test-2",
            json=product_data,
            headers={"Authorization": sample_seller['auth_token']}
        )
        assert response2.status_code == 200
    
    def test_token_isolation_between_orgs(self, client):
        """Test that sellers cannot access each other's resources"""
        # Create two sellers
        seller1 = client.post(
            "/createSeller",
        ).json()
        
        seller2 = client.post(
            "/createSeller",
        ).json()
        
        # Seller 1 creates a product
        client.post(
            "/product/org1-product",
            json={
                "name": "Org 1 Product",
                "shortDescription": "Test",
                "longDescription": "Test",
                "price": 1999,
                "image": {
                    "url": "https://example.com/img.jpg",
                    "alternativText": "Test"
                }
            },
            headers={"Authorization": f"Bearer {seller1['auth_token']}"}
        )
        
        # Org 2 tries to update Org 1's product
        response = client.patch(
            "/product/org1-product",
            json={"price": 999},
            headers={"Authorization": f"Bearer {seller2['auth_token']}"}
        )
        
        assert response.status_code == 403
    
    def test_token_isolation_between_buyers(self, client, sample_product):
        """Test that buyer tokens are properly isolated"""
        buyer1 = client.post(
            "/createBuyer",
            json={"name": "Buyer 1"}
        ).json()
        
        buyer2 = client.post(
            "/createBuyer",
            json={"name": "Buyer 2"}
        ).json()
        
        # Both should be able to purchase
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
        assert response1.json()["id"] != response2.json()["id"]


class TestMultipleSellersAndProducts:
    """Test scenarios with multiple sellers and products"""
    
    def test_multiple_orgs_with_similar_products(self, client):
        """Test that multiple sellers can have products with similar names"""
        # Create two sellers
        org1 = client.post(
            "/createSeller",
        ).json()
        
        org2 = client.post(
            "/createSeller",
        ).json()
        
        # Both create products with similar names
        product_data = {
            "name": "Premium Towel",
            "shortDescription": "Great towel",
            "longDescription": "Very nice towel",
            "price": 1999,
            "image": {
                "url": "https://example.com/towel.jpg",
                "alternativText": "Towel"
            }
        }
        
        client.post(
            "/product/brand-a-towel",
            json=product_data,
            headers={"Authorization": f"Bearer {org1['auth_token']}"}
        )
        
        client.post(
            "/product/brand-b-towel",
            json=product_data,
            headers={"Authorization": f"Bearer {org2['auth_token']}"}
        )
        
        # Search should find both
        response = client.get("/search?q=premium")
        results = response.json()
        
        assert len(results) == 2
        seller_ids = [r["seller_id"] for r in results]
        # Should have both seller IDs
        assert len(set(seller_ids)) == 2
    
    def test_seller_can_manage_multiple_products(self, client, sample_seller):
        """Test that one seller can create and manage multiple products"""
        products = []
        
        # Create 5 products
        for i in range(5):
            response = client.post(
                f"/product/prod-{i}",
                json={
                    "name": f"Product {i}",
                    "shortDescription": f"Description {i}",
                    "longDescription": f"Long description {i}",
                    "price": 1000 + (i * 100),
                    "image": {
                        "url": f"https://example.com/img{i}.jpg",
                        "alternativText": f"Image {i}"
                    }
                },
                headers={"Authorization": f"Bearer {sample_seller['auth_token']}"}
            )
            assert response.status_code == 200
            products.append(f"prod-{i}")
        
        # Verify all products exist and belong to same seller
        for prod_id in products:
            response = client.get(f"/product/{prod_id}")
            assert response.status_code == 200
            product = response.json()
            assert product["seller_id"] == sample_seller["id"]
        
        # Update one of them
        response = client.patch(
            "/product/prod-2",
            json={"price": 5999},
            headers={"Authorization": f"Bearer {sample_seller['auth_token']}"}
        )
        assert response.status_code == 200


class TestDataConsistency:
    """Test data consistency across operations"""
    
    def test_product_data_consistency_after_update(self, client, sample_product):
        """Test that product data remains consistent after updates"""
        original_name = sample_product["name"]
        original_org = sample_product["seller"]["id"]
        
        # Update only the price
        client.patch(
            f"/product/{sample_product['id']}",
            json={"price": 9999},
            headers={"Authorization": f"Bearer {sample_product['seller']['auth_token']}"}
        )
        
        # Verify other fields unchanged
        response = client.get(f"/product/{sample_product['id']}")
        product = response.json()
        
        assert product["name"] == original_name
        assert product["seller_id"] == original_org
        assert product["priceInCent"] == 9999
    
    def test_search_reflects_updates(self, client, sample_product):
        """Test that search results reflect product updates"""
        # Update product name
        new_name = "Completely Different Name"
        client.patch(
            f"/product/{sample_product['id']}",
            json={"name": new_name},
            headers={"Authorization": f"Bearer {sample_product['seller']['auth_token']}"}
        )
        
        # Search with new name
        response = client.get(f"/search?q=completely")
        results = response.json()
        
        assert len(results) == 1
        assert results[0]["name"] == new_name
        
        # Old name should not be found
        response = client.get(f"/search?q={sample_product['name']}")
        results = response.json()
        assert len(results) == 0
    
    def test_company_info_consistent_across_endpoints(self, client, sample_product):
        """Test that company information is consistent across different endpoints"""
        # Get from product detail
        detail_response = client.get(f"/product/{sample_product['id']}")
        detail_seller_id = detail_response.json()["seller_id"]
        
        # Get from search
        search_response = client.get(f"/search?q={sample_product['name']}")
        search_seller_id = search_response.json()[0]["seller_id"]
        
        # Should be identical
        assert detail_seller_id == search_seller_id == sample_product["seller"]["id"]


class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_product_with_zero_price(self, client, sample_seller):
        """Test creating a product with zero price"""
        response = client.post(
            "/product/free-product",
            json={
                "name": "Free Sample",
                "shortDescription": "Free",
                "longDescription": "Free product",
                "price": 0,
                "image": {
                    "url": "https://example.com/free.jpg",
                    "alternativText": "Free"
                }
            },
            headers={"Authorization": f"Bearer {sample_seller['auth_token']}"}
        )
        
        assert response.status_code == 200
        
        # Verify it was created
        product = client.get("/product/free-product").json()
        assert product["priceInCent"] == 0
    
    def test_product_with_very_long_description(self, client, sample_seller):
        """Test creating a product with very long descriptions"""
        long_text = "A" * 10000
        
        response = client.post(
            "/product/long-desc",
            json={
                "name": "Product with long description",
                "shortDescription": long_text,
                "longDescription": long_text,
                "price": 1999,
                "image": {
                    "url": "https://example.com/img.jpg",
                    "alternativText": "Test"
                }
            },
            headers={"Authorization": f"Bearer {sample_seller['auth_token']}"}
        )
        
        assert response.status_code == 200
    
    def test_search_with_special_characters(self, client, sample_seller):
        """Test search with special characters"""
        # Create product with special characters
        client.post(
            "/product/special-prod",
            json={
                "name": "Product & Co. (Premium)",
                "shortDescription": "Test",
                "longDescription": "Test",
                "price": 1999,
                "image": {
                    "url": "https://example.com/img.jpg",
                    "alternativText": "Test"
                }
            },
            headers={"Authorization": f"Bearer {sample_seller['auth_token']}"}
        )
        
        # Search should still work
        response = client.get("/search?q=premium")
        assert response.status_code == 200
        results = response.json()
        assert len(results) == 1
    
    def test_empty_search_query(self, client, sample_product):
        """Test search with empty query - should this return all products or error?"""
        # This might fail depending on FastAPI validation
        # Currently Query(...) requires a value
        pass  # Skip for now as it would require query parameter


class TestAPIHealth:
    """Test API health and basic endpoints"""
    
    def test_root_endpoint(self, client):
        """Test root endpoint returns correct information"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "docs" in data
    
    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
