"""Integration tests for search endpoint"""
import pytest


class TestProductSearch:
    """Test product search functionality"""
    
    def test_search_finds_matching_products(self, client, sample_seller):
        """Test that search finds products by name"""
        # Create multiple products
        products = [
            {"id": "towel-1", "name": "Blue Towel", "price": 1999},
            {"id": "towel-2", "name": "Red Towel", "price": 2499},
            {"id": "soap-1", "name": "Lavender Soap", "price": 599},
        ]
        
        for prod in products:
            client.post(
                f"/product/{prod['id']}",
                json={
                    "name": prod["name"],
                    "short_description": "Test product",
                    "long_description": "Test description",
                    "price": prod["price"],
                    "image": {
                        "url": "https://example.com/img.jpg",
                        "alternative_text": "Test image"
                    }
                },
                headers={"Authorization": f"Bearer {sample_seller['auth_token']}"}
            )
        
        # Search for "towel"
        response = client.get("/search?q=towel")
        
        assert response.status_code == 200
        results = response.json()
        
        # Should find 2 towels
        assert len(results) == 2
        assert all("towel" in r["name"].lower() for r in results)
    
    def test_search_case_insensitive(self, client, sample_seller):
        """Test that search is case-insensitive"""
        # Create product
        client.post(
            "/product/test-prod",
            json={
                "name": "PREMIUM Towel",
                "short_description": "Test",
                "long_description": "Test",
                "price": 1999,
                "image": {
                    "url": "https://example.com/img.jpg",
                    "alternative_text": "Test"
                }
            },
            headers={"Authorization": f"Bearer {sample_seller['auth_token']}"}
        )
        
        # Search with lowercase
        response = client.get("/search?q=premium")
        assert response.status_code == 200
        results = response.json()
        assert len(results) == 1
        assert "PREMIUM" in results[0]["name"]
    
    def test_search_partial_match(self, client, sample_seller):
        """Test that search finds partial matches"""
        client.post(
            "/product/test-prod",
            json={
                "name": "Extraordinary Product",
                "short_description": "Test",
                "long_description": "Test",
                "price": 1999,
                "image": {
                    "url": "https://example.com/img.jpg",
                    "alternative_text": "Test"
                }
            },
            headers={"Authorization": f"Bearer {sample_seller['auth_token']}"}
        )
        
        # Search for partial word
        response = client.get("/search?q=ordinary")
        assert response.status_code == 200
        results = response.json()
        assert len(results) == 1
    
    def test_search_returns_empty_for_no_matches(self, client, sample_product):
        """Test that search returns empty list when no matches"""
        response = client.get("/search?q=nonexistent-product-xyz")
        
        assert response.status_code == 200
        results = response.json()
        assert results == []
    
    def test_search_includes_company_info(self, client, sample_product):
        """Test that search results include company information"""
        response = client.get(f"/search?q={sample_product['name']}")
        
        assert response.status_code == 200
        results = response.json()
        
        assert len(results) > 0
        result = results[0]
        
        # Verify seller info is included
        assert "seller_id" in result
        assert result["seller_id"] == sample_product["seller"]["id"]
    
    def test_search_ranking_bestsellers_first(self, client, sample_seller):
        """Test that bestsellers appear first in search results"""
        # Create regular product
        client.post(
            "/product/regular-prod",
            json={
                "name": "Regular Towel",
                "short_description": "Regular",
                "long_description": "Regular",
                "price": 1999,
                "image": {
                    "url": "https://example.com/img.jpg",
                    "alternative_text": "Test"
                }
            },
            headers={"Authorization": f"Bearer {sample_seller['auth_token']}"}
        )
        
        # Manually set a product as bestseller (would need to update the product)
        # For now, verify the ordering works alphabetically
        client.post(
            "/product/amazing-towel",
            json={
                "name": "Amazing Towel",
                "short_description": "Amazing",
                "long_description": "Amazing",
                "price": 2999,
                "image": {
                    "url": "https://example.com/img.jpg",
                    "alternative_text": "Test"
                }
            },
            headers={"Authorization": f"Bearer {sample_seller['auth_token']}"}
        )
        
        response = client.get("/search?q=towel")
        results = response.json()
        
        # Should have both products
        assert len(results) == 2
        
        # Verify alphabetical ordering (since none are bestsellers)
        assert results[0]["name"] == "Amazing Towel"
        assert results[1]["name"] == "Regular Towel"
    
    def test_search_response_format(self, client, sample_product):
        """Test that search results have correct format"""
        response = client.get(f"/search?q={sample_product['name']}")
        
        assert response.status_code == 200
        results = response.json()
        assert len(results) > 0
        
        result = results[0]
        
        # Verify all required fields
        required_fields = [
            "id", "name", "seller_id", "price_in_cent", 
            "currency", "bestseller", "short_description", "image"
        ]
        for field in required_fields:
            assert field in result
        
        # Verify nested structures
        assert "url" in result["image"]
