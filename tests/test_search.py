"""Integration tests for search endpoint"""
import pytest


class TestProductSearch:
    """Test product search functionality"""
    
    def test_search_finds_matching_products(self, client, sample_seller, sample_images):
        """Test that search finds products by name"""
        # Create multiple products
        products = [
            {"id": "towel-1", "name": "Blue Towel", "price": 1999},
            {"id": "towel-2", "name": "Red Towel", "price": 2499},
            {"id": "soap-1", "name": "Lavender Soap", "price": 599},
        ]
        
        for prod in products:
            name_lower = prod["name"].lower()
            if "towel" in name_lower:
                short_desc = f"A quality towel set - {name_lower}"
                long_desc = f"This {name_lower} is a soft towel perfect for everyday use"
            else:
                short_desc = "A soothing lavender soap for daily use"
                long_desc = "Gentle soap with lavender scent"
            client.post(
                f"/product/{prod['id']}",
                json={
                    "name": prod["name"],
                    # Ensure only towel products include 'towel' in descriptions
                    "short_description": short_desc,
                    "long_description": long_desc,
                    "price": prod["price"],
                    "image_ids": [sample_images["01"][0].id],
                    "towel_variant": "budget"
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
    
    def test_search_case_insensitive(self, client, sample_seller, sample_images):
        """Test that search is case-insensitive"""
        # Create product
        client.post(
            "/product/test-prod",
            json={
                "name": "PREMIUM Towel",
                "short_description": "this is a premium towel",
                "long_description": "The Premium towel is extra soft",
                "price": 1999,
                "image_ids": [sample_images["01"][0].id],
                "towel_variant": "budget"
            },
            headers={"Authorization": f"Bearer {sample_seller['auth_token']}"}
        )
        
        # Search with lowercase
        response = client.get("/search?q=premium")
        assert response.status_code == 200
        results = response.json()
        assert len(results) == 1
        assert "PREMIUM" in results[0]["name"]
    
    def test_search_partial_match(self, client, sample_seller, sample_images):
        """Test that search finds partial matches"""
        client.post(
            "/product/test-prod",
            json={
                "name": "Extraordinary Product",
                "short_description": "An ordinary but extraordinary item",
                "long_description": "Truly extraordinary quality for ordinary needs",
                "price": 1999,
                "image_ids": [sample_images["01"][0].id],
                "towel_variant": "budget"
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
        # Ensure query matches across all fields; use 'test' which is present in name and descriptions
        response = client.get("/search?q=test")
        
        assert response.status_code == 200
        results = response.json()
        
        assert len(results) > 0
        result = results[0]
        
        # Verify seller info is included
        assert "seller_id" in result
        assert result["seller_id"] == sample_product["seller"]["id"]
    
    def test_search_ranking_priority(self, client, sample_seller, sample_images):
        """Test that ranking takes priority in search ordering"""
        # Create two matching products
        client.post(
            "/product/regular-prod",
            json={
                "name": "Regular Towel",
                "short_description": "Regular towel",
                "long_description": "Regular towel item",
                "price": 1999,
                "image_ids": [sample_images["01"][0].id],
                "towel_variant": "budget"
            },
            headers={"Authorization": f"Bearer {sample_seller['auth_token']}"}
        )
        
        client.post(
            "/product/amazing-towel",
            json={
                "name": "Amazing Towel",
                "short_description": "Amazing towel",
                "long_description": "Amazing towel item",
                "price": 2999,
                "image_ids": [sample_images["01"][0].id],
                "towel_variant": "budget"
            },
            headers={"Authorization": f"Bearer {sample_seller['auth_token']}"}
        )
        
        # Set explicit rankings: amazing-towel rank 1 (best), regular-prod rank 10 (worse)
        client.patch(
            "/product/amazing-towel",
            json={"ranking": 1},
            headers={"Authorization": f"Bearer {sample_seller['auth_token']}"}
        )
        client.patch(
            "/product/regular-prod",
            json={"ranking": 10},
            headers={"Authorization": f"Bearer {sample_seller['auth_token']}"}
        )
        
        response = client.get("/search?q=towel")
        results = response.json()
        
        # Should have both products
        assert len(results) == 2
        # Verify ranking ordering (rank 1 = best comes first)
        assert results[0]["name"] == "Amazing Towel"
        assert results[1]["name"] == "Regular Towel"
    
    def test_search_response_format(self, client, sample_product):
        """Test that search results have correct format"""
        response = client.get("/search?q=test")
        
        assert response.status_code == 200
        results = response.json()
        assert len(results) > 0
        
        result = results[0]
        
        # Verify all required fields
        required_fields = [
            "id", "name", "seller_id", "price_in_cent", 
            "currency", "bestseller", "short_description", "images"
        ]
        for field in required_fields:
            assert field in result
        # Ranking may be present
        assert "ranking" in result
        
        # Verify nested structures
        assert isinstance(result["images"], list)
        assert len(result["images"]) > 0
        assert "id" in result["images"][0]
        assert "image_description" in result["images"][0]
        assert "product_number" in result["images"][0]
        # Verify no base64 in response
        assert "base64" not in result["images"][0]

    def test_search_keyword_only_in_title(self, client, sample_seller, sample_images):
        """Keyword present only in product name should match"""
        client.post(
            "/product/only-title",
            json={
                "name": "UniqueTitleKeyword Item",
                "short_description": "Plain short description",
                "long_description": "Plain long description",
                "price": 1500,
                "image_ids": [sample_images["01"][0].id],
            "towel_variant": "budget"
            },
            headers={"Authorization": f"Bearer {sample_seller['auth_token']}"},
        )

        response = client.get("/search?q=uniquetitlekeyword")
        assert response.status_code == 200
        results = response.json()
        assert any(r["id"] == "only-title" for r in results)

    def test_search_keyword_only_in_short_description(self, client, sample_seller, sample_images):
        """Keyword present only in short_description should match"""
        client.post(
            "/product/only-short",
            json={
                "name": "Generic Item",
                "short_description": "Includes UniqueShortKeyword in short",
                "long_description": "Plain long description",
                "price": 1600,
                "image_ids": [sample_images["01"][0].id],
            "towel_variant": "budget"
            },
            headers={"Authorization": f"Bearer {sample_seller['auth_token']}"},
        )

        response = client.get("/search?q=uniqueshortkeyword")
        assert response.status_code == 200
        results = response.json()
        assert any(r["id"] == "only-short" for r in results)

    def test_search_keyword_only_in_long_description(self, client, sample_seller, sample_images):
        """Keyword present only in long_description should match"""
        client.post(
            "/product/only-long",
            json={
                "name": "Generic Item",
                "short_description": "Plain short description",
                "long_description": "This paragraph contains UniqueLongKeyword only here.",
                "price": 1700,
                "image_ids": [sample_images["01"][0].id],
            "towel_variant": "budget"
            },
            headers={"Authorization": f"Bearer {sample_seller['auth_token']}"},
        )

        response = client.get("/search?q=uniquelongkeyword")
        assert response.status_code == 200
        results = response.json()
        assert any(r["id"] == "only-long" for r in results)
