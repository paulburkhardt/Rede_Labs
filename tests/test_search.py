"""Integration tests for search endpoint"""
import pytest


class TestProductSearch:
    """Test product search functionality"""
    
    def test_search_finds_matching_products(self, client, battle_id, sample_seller, sample_images):
        """Test that search finds products by name"""
        # Create multiple products
        products = [
            {"id": f"towel-1-{battle_id[:8]}", "name": "Blue Towel", "price": 1999},
            {"id": f"towel-2-{battle_id[:8]}", "name": "Red Towel", "price": 2499},
            {"id": f"soap-1-{battle_id[:8]}", "name": "Lavender Soap", "price": 599},
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
        response = client.get(f"/search?battle_id={battle_id}&q=towel")
        
        assert response.status_code == 200
        results = response.json()
        
        # Should find 2 towels
        assert len(results) == 2
        assert all("towel" in r["name"].lower() for r in results)
    
    def test_search_case_insensitive(self, client, battle_id, sample_seller, sample_images):
        """Test that search is case-insensitive"""
        product_id = f"test-prod-case-{battle_id[:8]}"
        # Create product
        client.post(
            f"/product/{product_id}",
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
        response = client.get(f"/search?battle_id={battle_id}&q=premium")
        assert response.status_code == 200
        results = response.json()
        assert len(results) == 1
        assert "PREMIUM" in results[0]["name"]
    
    def test_search_partial_match(self, client, battle_id, sample_seller, sample_images):
        """Test that search finds partial matches"""
        product_id = f"test-prod-partial-{battle_id[:8]}"
        client.post(
            f"/product/{product_id}",
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
        response = client.get(f"/search?battle_id={battle_id}&q=ordinary")
        assert response.status_code == 200
        results = response.json()
        assert len(results) == 1
    
    def test_search_returns_empty_for_no_matches(self, client, battle_id, sample_product):
        """Test that search returns empty list when no matches"""
        response = client.get(f"/search?battle_id={battle_id}&q=nonexistent-product-xyz")
        
        assert response.status_code == 200
        results = response.json()
        assert results == []
    
    def test_search_includes_company_info(self, client, battle_id, sample_product):
        """Test that search results include company information"""
        # Ensure query matches across all fields; use 'test' which is present in name and descriptions
        response = client.get(f"/search?battle_id={battle_id}&q=test")
        
        assert response.status_code == 200
        results = response.json()
        
        assert len(results) > 0
        result = results[0]
        
        # Verify seller info is included
        assert "seller_id" in result
        assert result["seller_id"] == sample_product["seller"]["id"]
    
    def test_search_ranking_priority(self, client, battle_id, sample_seller, sample_images):
        """Test that ranking takes priority in search ordering"""
        product_id_1 = f"regular-prod-{battle_id[:8]}"
        product_id_2 = f"amazing-towel-{battle_id[:8]}"

        # Create two matching products
        client.post(
            f"/product/{product_id_1}",
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
            f"/product/{product_id_2}",
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
            f"/product/{product_id_2}",
            json={"ranking": 1, "towel_variant": "budget"},
            headers={"Authorization": f"Bearer {sample_seller['auth_token']}"}
        )
        client.patch(
            f"/product/{product_id_1}",
            json={"ranking": 10, "towel_variant": "budget"},
            headers={"Authorization": f"Bearer {sample_seller['auth_token']}"}
        )
        
        response = client.get(f"/search?battle_id={battle_id}&q=towel")
        results = response.json()
        
        # Should have both products
        assert len(results) == 2
        # Verify ranking ordering (rank 1 = best comes first)
        assert results[0]["name"] == "Amazing Towel"
        assert results[1]["name"] == "Regular Towel"

    def test_search_response_format(self, client, battle_id, sample_product):
        """Test that search results have correct format"""
        response = client.get(f"/search?battle_id={battle_id}&q=test")
        
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

    def test_search_keyword_only_in_title(self, client, battle_id, sample_seller, sample_images):
        """Keyword present only in product name should match"""
        product_id = f"only-title-{battle_id[:8]}"
        client.post(
            f"/product/{product_id}",
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

        response = client.get(f"/search?battle_id={battle_id}&q=uniquetitlekeyword")
        assert response.status_code == 200
        results = response.json()
        assert any(r["id"] == product_id for r in results)

    def test_search_keyword_only_in_short_description(self, client, battle_id, sample_seller, sample_images):
        """Keyword present only in short_description should match"""
        product_id = f"only-short-{battle_id[:8]}"
        client.post(
            f"/product/{product_id}",
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

        response = client.get(f"/search?battle_id={battle_id}&q=uniqueshortkeyword")
        assert response.status_code == 200
        results = response.json()
        assert any(r["id"] == product_id for r in results)

    def test_search_keyword_only_in_long_description(self, client, battle_id, sample_seller, sample_images):
        """Keyword present only in long_description should match"""
        product_id = f"only-long-{battle_id[:8]}"
        client.post(
            f"/product/{product_id}",
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

        response = client.get(f"/search?battle_id={battle_id}&q=uniquelongkeyword")
        assert response.status_code == 200
        results = response.json()
        assert any(r["id"] == product_id for r in results)
