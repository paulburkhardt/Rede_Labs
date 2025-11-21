"""Integration tests for complex scenarios and edge cases"""
import pytest

from app.services.phase_manager import Phase


class TestAuthenticationSecurity:
    """Test authentication and authorization security"""
    
    def test_bearer_token_with_and_without_prefix(self, client, battle_id, sample_seller, sample_images):
        """Test that both 'Bearer token' and 'token' formats work"""
        product_data = {
            "name": "Test Product",
            "short_description": "Test",
            "long_description": "Test",
            "price": 1999,
            "image_ids": [sample_images["01"][0].id],
            "towel_variant": "budget"
        }

        # Test with "Bearer " prefix
        response1 = client.post(
            f"/product/test-1-{battle_id[:8]}",
            json=product_data,
            headers={"Authorization": f"Bearer {sample_seller['auth_token']}"}
        )
        assert response1.status_code == 200

        # Test without "Bearer " prefix
        response2 = client.post(
            f"/product/test-2-{battle_id[:8]}",
            json=product_data,
            headers={"Authorization": sample_seller['auth_token']}
        )
        assert response2.status_code == 200
    
    def test_token_isolation_between_orgs(self, client, battle_id, sample_images):
        """Test that sellers cannot access each other's resources"""
        # Create two sellers
        seller1 = client.post(
            "/createSeller",
            json={"battle_id": battle_id}
        ).json()

        seller2 = client.post(
            "/createSeller",
            json={"battle_id": battle_id}
        ).json()
        
        # Seller 1 creates a product
        product_id = f"org1-product-{battle_id[:8]}"
        client.post(
            f"/product/{product_id}",
            json={
                "name": "Org 1 Product",
                "short_description": "Test",
                "long_description": "Test",
                "price": 1999,
                "image_ids": [sample_images["01"][0].id],
                "towel_variant": "budget"
            },
            headers={"Authorization": f"Bearer {seller1['auth_token']}"}
        )

        # Org 2 tries to update Org 1's product
        response = client.patch(
            f"/product/{product_id}",
            json={"price": 999, "towel_variant": "budget"},
            headers={"Authorization": f"Bearer {seller2['auth_token']}"}
        )
        
        assert response.status_code == 403
    
    def test_token_isolation_between_buyers(self, client, battle_id, sample_product, set_phase):
        """Test that buyer tokens are properly isolated"""
        buyer1 = client.post(
            "/createBuyer",
            json={"battle_id": battle_id}
        ).json()

        buyer2 = client.post(
            "/createBuyer",
            json={"battle_id": battle_id}
        ).json()
        
        # Both should be able to purchase
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
        assert response1.json()["id"] != response2.json()["id"]


class TestMultipleSellersAndProducts:
    """Test scenarios with multiple sellers and products"""
    
    def test_multiple_orgs_with_similar_products(self, client, battle_id, sample_images):
        """Test that multiple sellers can have products with similar names"""
        # Create two sellers
        org1 = client.post(
            "/createSeller",
            json={"battle_id": battle_id}
        ).json()

        org2 = client.post(
            "/createSeller",
            json={"battle_id": battle_id}
        ).json()
        
        # Both create products with similar names
        product_data = {
            "name": "Premium Towel",
            "short_description": "Great towel",
            "long_description": "Very nice towel",
            "price": 1999,
            "image_ids": [sample_images["01"][0].id],
            "towel_variant": "budget"
        }

        client.post(
            f"/product/brand-a-towel-{battle_id[:8]}",
            json=product_data,
            headers={"Authorization": f"Bearer {org1['auth_token']}"}
        )

        client.post(
            f"/product/brand-b-towel-{battle_id[:8]}",
            json=product_data,
            headers={"Authorization": f"Bearer {org2['auth_token']}"}
        )
        
        # Search should find both
        response = client.get(f"/search?battle_id={battle_id}&q=premium")
        results = response.json()
        
        assert len(results) == 2
        seller_ids = [r["seller_id"] for r in results]
        # Should have both seller IDs
        assert len(set(seller_ids)) == 2
    
    def test_seller_can_manage_multiple_products(self, client, battle_id, sample_seller, sample_images):
        """Test that one seller can create and manage multiple products"""
        products = []

        # Create 5 products
        for i in range(5):
            prod_id = f"prod-{i}-{battle_id[:8]}"
            response = client.post(
                f"/product/{prod_id}",
                json={
                    "name": f"Product {i}",
                    "short_description": f"Description {i}",
                    "long_description": f"Long description {i}",
                    "price": 1000 + (i * 100),
                    "image_ids": [sample_images["01"][0].id],
                    "towel_variant": "budget"
                },
                headers={"Authorization": f"Bearer {sample_seller['auth_token']}"}
            )
            assert response.status_code == 200
            products.append(prod_id)

        # Verify all products exist and belong to same seller
        for prod_id in products:
            response = client.get(f"/product/{prod_id}")
            assert response.status_code == 200
            product = response.json()
            assert product["seller_id"] == sample_seller["id"]
        
        # Update one of them
        response = client.patch(
            f"/product/{products[2]}",
            json={"price": 5999, "towel_variant": "budget"},
            headers={"Authorization": f"Bearer {sample_seller['auth_token']}"}
        )
        assert response.status_code == 200


class TestDataConsistency:
    """Test data consistency across operations"""
    
    def test_product_data_consistency_after_update(self, client, battle_id, sample_product):
        """Test that product data remains consistent after updates"""
        original_name = sample_product["name"]
        original_org = sample_product["seller"]["id"]
        
        # Update only the price
        client.patch(
            f"/product/{sample_product['id']}",
            json={"price": 9999, "towel_variant": "budget"},
            headers={"Authorization": f"Bearer {sample_product['seller']['auth_token']}"}
        )
        
        # Verify other fields unchanged
        response = client.get(f"/product/{sample_product['id']}")
        product = response.json()
        
        assert product["name"] == original_name
        assert product["seller_id"] == original_org
        assert product["price_in_cent"] == 9999
    
    def test_search_reflects_updates(self, client, battle_id, sample_product):
        """Test that search results reflect product updates"""
        # Update product name
        new_name = "Completely Different Name"
        client.patch(
            f"/product/{sample_product['id']}",
            json={"name": new_name, "towel_variant": "budget"},
            headers={"Authorization": f"Bearer {sample_product['seller']['auth_token']}"}
        )
        
        # Search with new name
        response = client.get(f"/search?battle_id={battle_id}&q=completely")
        results = response.json()
        
        assert len(results) == 1
        assert results[0]["name"] == new_name    
    
    def test_company_info_consistent_across_endpoints(self, client, battle_id, sample_product):
        """Test that company information is consistent across different endpoints"""
        # Get from product detail
        detail_response = client.get(f"/product/{sample_product['id']}")
        detail_seller_id = detail_response.json()["seller_id"]
        
        # Get from search
        search_response = client.get(f"/search?battle_id={battle_id}&q={sample_product['name']}")
        search_seller_id = search_response.json()[0]["seller_id"]
        
        # Should be identical
        assert detail_seller_id == search_seller_id == sample_product["seller"]["id"]


class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_product_with_zero_price(self, client, battle_id, sample_seller, sample_images):
        """Test that creating a product with zero price is rejected"""
        response = client.post(
            f"/product/free-product-{battle_id[:8]}",
            json={
                "name": "Free Sample",
                "short_description": "Free",
                "long_description": "Free product",
                "price": 0,
                "image_ids": [sample_images["01"][0].id],
                "towel_variant": "budget"
            },
            headers={"Authorization": f"Bearer {sample_seller['auth_token']}"}
        )
        
        # Zero price should be rejected
        assert response.status_code == 422
        assert "price" in response.json()["detail"][0]["loc"]
        assert "greater than 0" in response.json()["detail"][0]["msg"]
    
    def test_product_with_very_long_description(self, client, battle_id, sample_seller, sample_images):
        """Test creating a product with very long descriptions"""
        long_text = "A" * 10000

        response = client.post(
            f"/product/long-desc-{battle_id[:8]}",
            json={
                "name": "Product with long description",
                "short_description": long_text,
                "long_description": long_text,
                "price": 1999,
                "image_ids": [sample_images["01"][0].id],
                "towel_variant": "budget"
            },
            headers={"Authorization": f"Bearer {sample_seller['auth_token']}"}
        )

        assert response.status_code == 200

    def test_search_with_special_characters(self, client, battle_id, sample_seller, sample_images):
        """Test search with special characters"""
        # Create product with special characters
        client.post(
            f"/product/special-prod-{battle_id[:8]}",
            json={
                "name": "Product & Co. (Premium)",
                "short_description": "Test",
                "long_description": "Test",
                "price": 1999,
                "image_ids": [sample_images["01"][0].id],
                "towel_variant": "budget"
            },
            headers={"Authorization": f"Bearer {sample_seller['auth_token']}"}
        )
        
        # Search should still work
        response = client.get(f"/search?battle_id={battle_id}&q=premium")
        assert response.status_code == 200
        results = response.json()
        assert len(results) == 1
    
    def test_empty_search_query(self, client, battle_id, sample_product):
        """Test search with empty query - should this return all products or error?"""
        # This might fail depending on FastAPI validation
        # Currently Query(...) requires a value
        pass  # Skip for now as it would require query parameter


class TestSalesStats:
    """Test sales statistics endpoint"""
    
    def test_get_sales_stats_no_sales(self, client, battle_id, sample_seller, sample_images):
        """Test getSalesStats with no sales returns empty data"""
        response = client.get(
            "/getSalesStats",
            headers={"Authorization": f"Bearer {sample_seller['auth_token']}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["seller_id"] == sample_seller["id"]
        assert data["total_sales"] == 0
        assert data["total_revenue_in_cent"] == 0
        assert data["purchases"] == []
    
    def test_get_sales_stats_with_single_purchase(
        self, client, battle_id, sample_seller, sample_buyer, sample_images, set_phase
    ):
        """Test getSalesStats with a single purchase"""
        product_id = f"test-prod-1-{battle_id[:8]}"
        # Create a product
        product_data = {
            "name": "Test Product",
            "short_description": "Test",
            "long_description": "Test",
            "price": 2500,
            "image_ids": [sample_images["01"][0].id],
            "towel_variant": "budget"
        }
        client.post(
            f"/product/{product_id}",
            json=product_data,
            headers={"Authorization": f"Bearer {sample_seller['auth_token']}"}
        )

        # Make a purchase
        set_phase(Phase.BUYER_SHOPPING)
        client.post(
            f"/buy/{product_id}",
            headers={"Authorization": f"Bearer {sample_buyer['auth_token']}"}
        )

        # Get sales stats
        response = client.get(
            "/getSalesStats",
            headers={"Authorization": f"Bearer {sample_seller['auth_token']}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["seller_id"] == sample_seller["id"]
        assert data["total_sales"] == 1
        assert data["total_revenue_in_cent"] == 2500
        assert len(data["purchases"]) == 1

        purchase = data["purchases"][0]
        assert purchase["product_id"] == product_id
        assert purchase["product_name"] == "Test Product"
        assert purchase["buyer_id"] == sample_buyer["id"]
        assert purchase["price_in_cent"] == 2500
        assert purchase["currency"] == "USD"
        assert "purchased_at" in purchase
        assert "round" in purchase
        assert isinstance(purchase["round"], int)
    
    def test_get_sales_stats_with_multiple_purchases(
        self, client, battle_id, sample_seller, sample_images, set_phase
    ):
        """Test getSalesStats with multiple purchases from different buyers"""
        # Create two products
        for i in range(2):
            client.post(
                f"/product/prod-{i}-{battle_id[:8]}",
                json={
                    "name": f"Product {i}",
                    "short_description": "Test",
                    "long_description": "Test",
                    "price": 1000 * (i + 1),
                    "image_ids": [sample_images["01"][0].id],
                    "towel_variant": "budget"
                },
                headers={"Authorization": f"Bearer {sample_seller['auth_token']}"}
            )

        # Create three buyers and make purchases
        set_phase(Phase.BUYER_SHOPPING)
        for i in range(3):
            buyer = client.post(
                "/createBuyer",
                json={"battle_id": battle_id}
            ).json()

            # Each buyer purchases product 0
            client.post(
                f"/buy/prod-0-{battle_id[:8]}",
                headers={"Authorization": f"Bearer {buyer['auth_token']}"}
            )

        # One buyer purchases product 1
        buyer = client.post(
            "/createBuyer",
            json={"battle_id": battle_id}
        ).json()
        client.post(
            f"/buy/prod-1-{battle_id[:8]}",
            headers={"Authorization": f"Bearer {buyer['auth_token']}"}
        )
        
        # Get sales stats
        response = client.get(
            "/getSalesStats",
            headers={"Authorization": f"Bearer {sample_seller['auth_token']}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_sales"] == 4
        assert data["total_revenue_in_cent"] == (1000 * 3) + (2000 * 1)  # 5000
        assert len(data["purchases"]) == 4
    
    def test_get_sales_stats_only_returns_own_sales(
        self, client, battle_id, sample_images, set_phase
    ):
        """Test that getSalesStats only returns sales for the authenticated seller"""
        # Create two sellers
        seller1 = client.post("/createSeller", json={"battle_id": battle_id}).json()
        seller2 = client.post("/createSeller", json={"battle_id": battle_id}).json()
        
        # Each seller creates a product
        seller1_prod = f"seller1-prod-{battle_id[:8]}"
        seller2_prod = f"seller2-prod-{battle_id[:8]}"

        client.post(
            f"/product/{seller1_prod}",
            json={
                "name": "Seller 1 Product",
                "short_description": "Test",
                "long_description": "Test",
                "price": 1000,
                "image_ids": [sample_images["01"][0].id],
                "towel_variant": "budget"
            },
            headers={"Authorization": f"Bearer {seller1['auth_token']}"}
        )

        client.post(
            f"/product/{seller2_prod}",
            json={
                "name": "Seller 2 Product",
                "short_description": "Test",
                "long_description": "Test",
                "price": 2000,
                "image_ids": [sample_images["01"][0].id],
                "towel_variant": "budget"
            },
            headers={"Authorization": f"Bearer {seller2['auth_token']}"}
        )

        # Create a buyer
        buyer = client.post(
            "/createBuyer",
            json={"battle_id": battle_id}
        ).json()

        # Buyer purchases from both sellers
        set_phase(Phase.BUYER_SHOPPING)
        client.post(
            f"/buy/{seller1_prod}",
            headers={"Authorization": f"Bearer {buyer['auth_token']}"}
        )
        client.post(
            f"/buy/{seller2_prod}",
            headers={"Authorization": f"Bearer {buyer['auth_token']}"}
        )

        # Get sales stats for seller 1
        response1 = client.get(
            "/getSalesStats",
            headers={"Authorization": f"Bearer {seller1['auth_token']}"}
        )
        data1 = response1.json()
        assert data1["total_sales"] == 1
        assert data1["total_revenue_in_cent"] == 1000
        assert data1["purchases"][0]["product_id"] == seller1_prod

        # Get sales stats for seller 2
        response2 = client.get(
            "/getSalesStats",
            headers={"Authorization": f"Bearer {seller2['auth_token']}"}
        )
        data2 = response2.json()
        assert data2["total_sales"] == 1
        assert data2["total_revenue_in_cent"] == 2000
        assert data2["purchases"][0]["product_id"] == seller2_prod
    
    def test_get_sales_stats_requires_authentication(self, client, battle_id, sample_images):
        """Test that getSalesStats requires valid authentication"""
        # No authorization header
        response = client.get("/getSalesStats")
        assert response.status_code == 422  # Missing required header
        
        # Invalid token
        response = client.get(
            "/getSalesStats",
            headers={"Authorization": "Bearer invalid-token"}
        )
        assert response.status_code == 401
        assert "Invalid authentication token" in response.json()["detail"]
    
    def test_get_sales_stats_with_bearer_prefix_variations(
        self, client, battle_id, sample_seller, sample_buyer, sample_images, set_phase
    ):
        """Test that getSalesStats works with and without Bearer prefix"""
        product_id = f"test-prod-{battle_id[:8]}"
        # Create and purchase a product
        client.post(
            f"/product/{product_id}",
            json={
                "name": "Test Product",
                "short_description": "Test",
                "long_description": "Test",
                "price": 1500,
                "image_ids": [sample_images["01"][0].id],
                "towel_variant": "budget"
            },
            headers={"Authorization": f"Bearer {sample_seller['auth_token']}"}
        )
        set_phase(Phase.BUYER_SHOPPING)
        client.post(
            f"/buy/{product_id}",
            headers={"Authorization": f"Bearer {sample_buyer['auth_token']}"}
        )
        
        # Test with Bearer prefix
        response1 = client.get(
            "/getSalesStats",
            headers={"Authorization": f"Bearer {sample_seller['auth_token']}"}
        )
        assert response1.status_code == 200
        assert response1.json()["total_sales"] == 1
        
        # Test without Bearer prefix
        response2 = client.get(
            "/getSalesStats",
            headers={"Authorization": sample_seller['auth_token']}
        )
        assert response2.status_code == 200
        assert response2.json()["total_sales"] == 1
    
    def test_get_sales_stats_purchase_order(
        self, client, battle_id, sample_seller, sample_buyer, sample_images, set_phase
    ):
        """Test that purchases are returned in the correct order"""
        # Create multiple products
        product_ids = []
        for i in range(3):
            product_id = f"prod-{i}-{battle_id[:8]}"
            client.post(
                f"/product/{product_id}",
                json={
                    "name": f"Product {i}",
                    "short_description": "Test",
                    "long_description": "Test",
                    "price": 1000 * (i + 1),
                    "image_ids": [sample_images["01"][0].id],
                    "towel_variant": "budget"
                },
                headers={"Authorization": f"Bearer {sample_seller['auth_token']}"}
            )
            product_ids.append(product_id)

        set_phase(Phase.BUYER_SHOPPING)
        for i, product_id in enumerate(product_ids):
            client.post(
                f"/buy/{product_id}",
                headers={"Authorization": f"Bearer {sample_buyer['auth_token']}"}
            )
        
        # Get sales stats
        response = client.get(
            "/getSalesStats",
            headers={"Authorization": f"Bearer {sample_seller['auth_token']}"}
        )
        
        data = response.json()
        assert len(data["purchases"]) == 3
        
        # Verify all purchases have day numbers
        for purchase in data["purchases"]:
            assert "purchased_at" in purchase
            assert isinstance(purchase["purchased_at"], int)
            assert "round" in purchase
            assert isinstance(purchase["round"], int)


class TestLeaderboard:
    """Test leaderboard endpoint"""

    @staticmethod
    def _get_round_data(payload, round_number=None):
        """Retrieve the leaderboard payload for the requested round."""
        target_round = payload["current_round"] if round_number is None else round_number
        for round_data in payload.get("rounds", []):
            if round_data["round"] == target_round:
                return round_data
        raise AssertionError(f"Round {target_round} data not found in payload")

    @classmethod
    def _get_leaderboard(cls, payload, round_number=None):
        """Return leaderboard entries for the requested round."""
        return cls._get_round_data(payload, round_number)["leaderboard"]

    @staticmethod
    def _get_overall(payload):
        """Return overall leaderboard entries."""
        return payload["overall"]["leaderboard"]
    
    def test_leaderboard_no_sales(self, client, battle_id, sample_images):
        """Test leaderboard with no sales returns sellers with zero revenue"""
        # Create two sellers
        seller1 = client.post("/createSeller", json={"battle_id": battle_id}).json()
        seller2 = client.post("/createSeller", json={"battle_id": battle_id}).json()

        # Get leaderboard
        response = client.get(f"/buy/stats/leaderboard?battle_id={battle_id}")
        
        assert response.status_code == 200
        data = response.json()
        current_leaderboard = self._get_leaderboard(data)
        assert len(current_leaderboard) == 2
        
        # All sellers should have zero profit
        for entry in current_leaderboard:
            assert entry["purchase_count"] == 0
            assert entry["total_profit_cents"] == 0
            assert entry["total_profit_dollars"] == 0.0
        assert set(data["overall"]["winners"]) == {
            seller1["id"],
            seller2["id"],
        }
        overall = self._get_overall(data)
        for entry in overall:
            assert entry["round_wins"] == 0
    
    def test_leaderboard_single_seller_single_purchase(
        self, client, battle_id, sample_seller, sample_buyer, sample_images, set_phase
    ):
        """Test leaderboard with a single seller and single purchase"""
        product_id = f"test-prod-{battle_id[:8]}"
        # Create a product
        client.post(
            f"/product/{product_id}",
            json={
                "name": "Test Product",
                "short_description": "Test",
                "long_description": "Test",
                "price": 2500,
                "image_ids": [sample_images["01"][0].id],
                "towel_variant": "budget"
            },
            headers={"Authorization": f"Bearer {sample_seller['auth_token']}"}
        )

        # Make a purchase
        set_phase(Phase.BUYER_SHOPPING)
        client.post(
            f"/buy/{product_id}",
            headers={"Authorization": f"Bearer {sample_buyer['auth_token']}"}
        )

        # Get leaderboard
        response = client.get(f"/buy/stats/leaderboard?battle_id={battle_id}")

        assert response.status_code == 200
        data = response.json()
        leaderboard = self._get_leaderboard(data)
        assert len(leaderboard) == 1
        
        entry = leaderboard[0]
        assert entry["seller_id"] == sample_seller["id"]
        assert entry["purchase_count"] == 1
        # Profit = price (2500) - wholesale_cost (800) = 1700
        assert entry["total_profit_cents"] == 1700
        assert entry["total_profit_dollars"] == 17.0
    
    def test_leaderboard_multiple_sellers_sorted_by_revenue(
        self, client, battle_id, sample_images, set_phase
    ):
        """Test leaderboard with multiple sellers sorted by total revenue"""
        # Create three sellers
        sellers = []
        for i in range(3):
            seller = client.post("/createSeller", json={"battle_id": battle_id}).json()
            sellers.append(seller)

        # Create a buyer
        buyer = client.post(
            "/createBuyer",
            json={"battle_id": battle_id}
        ).json()
        
        # Seller 0: 2 products at $10 and $20 = $30 total
        s0_p1 = f"s0-p1-{battle_id[:8]}"
        s0_p2 = f"s0-p2-{battle_id[:8]}"
        s1_p1 = f"s1-p1-{battle_id[:8]}"
        s2_p1 = f"s2-p1-{battle_id[:8]}"

        client.post(
            f"/product/{s0_p1}",
            json={
                "name": "Product 1",
                "short_description": "Test",
                "long_description": "Test",
                "price": 1000,
                "image_ids": [sample_images["01"][0].id],
                "towel_variant": "budget"
            },
            headers={"Authorization": f"Bearer {sellers[0]['auth_token']}"}
        )
        client.post(
            f"/product/{s0_p2}",
            json={
                "name": "Product 2",
                "short_description": "Test",
                "long_description": "Test",
                "price": 2000,
                "image_ids": [sample_images["01"][0].id],
                "towel_variant": "budget"
            },
            headers={"Authorization": f"Bearer {sellers[0]['auth_token']}"}
        )

        # Seller 1: 1 product at $50 = $50 total (highest)
        client.post(
            f"/product/{s1_p1}",
            json={
                "name": "Product 3",
                "short_description": "Test",
                "long_description": "Test",
                "price": 5000,
                "image_ids": [sample_images["01"][0].id],
                "towel_variant": "budget"
            },
            headers={"Authorization": f"Bearer {sellers[1]['auth_token']}"}
        )

        # Seller 2: 1 product at $5 = $5 total (lowest)
        client.post(
            f"/product/{s2_p1}",
            json={
                "name": "Product 4",
                "short_description": "Test",
                "long_description": "Test",
                "price": 500,
                "image_ids": [sample_images["01"][0].id],
                "towel_variant": "budget"
            },
            headers={"Authorization": f"Bearer {sellers[2]['auth_token']}"}
        )

        set_phase(Phase.BUYER_SHOPPING)

        client.post(
            f"/buy/{s0_p1}",
            headers={"Authorization": f"Bearer {buyer['auth_token']}"}
        )
        client.post(
            f"/buy/{s0_p2}",
            headers={"Authorization": f"Bearer {buyer['auth_token']}"}
        )
        client.post(
            f"/buy/{s1_p1}",
            headers={"Authorization": f"Bearer {buyer['auth_token']}"}
        )
        client.post(
            f"/buy/{s2_p1}",
            headers={"Authorization": f"Bearer {buyer['auth_token']}"}
        )
        
        # Get leaderboard
        response = client.get(f"/buy/stats/leaderboard?battle_id={battle_id}")

        assert response.status_code == 200
        data = response.json()
        leaderboard = self._get_leaderboard(data)
        assert len(leaderboard) == 3
        
        # Verify sorting by profit (descending)
        # Seller 1: profit = 5000 - 800 = 4200
        assert leaderboard[0]["seller_id"] == sellers[1]["id"]
        assert leaderboard[0]["total_profit_cents"] == 4200
        assert leaderboard[0]["total_profit_dollars"] == 42.0
        assert leaderboard[0]["purchase_count"] == 1
        
        # Seller 0: profit = (1000 - 800) + (2000 - 800) = 200 + 1200 = 1400
        assert leaderboard[1]["seller_id"] == sellers[0]["id"]
        assert leaderboard[1]["total_profit_cents"] == 1400
        assert leaderboard[1]["total_profit_dollars"] == 14.0
        assert leaderboard[1]["purchase_count"] == 2
        
        # Seller 2: profit = 500 - 800 = -300 (loss)
        assert leaderboard[2]["seller_id"] == sellers[2]["id"]
        assert leaderboard[2]["total_profit_cents"] == -300
        assert leaderboard[2]["total_profit_dollars"] == -3.0
        assert leaderboard[2]["purchase_count"] == 1

        overall = self._get_overall(data)
        assert overall[0]["seller_id"] == sellers[1]["id"]
        assert overall[0]["round_wins"] == 1
        assert data["overall"]["winners"] == [sellers[1]["id"]]
    
    def test_leaderboard_same_product_multiple_purchases(
        self, client, battle_id, sample_seller, sample_images, set_phase
    ):
        """Test leaderboard when the same product is purchased multiple times"""
        product_id = f"popular-prod-{battle_id[:8]}"
        # Create a product
        client.post(
            f"/product/{product_id}",
            json={
                "name": "Popular Product",
                "short_description": "Test",
                "long_description": "Test",
                "price": 1500,
                "image_ids": [sample_images["01"][0].id],
                "towel_variant": "budget"
            },
            headers={"Authorization": f"Bearer {sample_seller['auth_token']}"}
        )

        # Create three buyers and each purchases the same product
        set_phase(Phase.BUYER_SHOPPING)
        for i in range(3):
            buyer = client.post(
                "/createBuyer",
                json={"battle_id": battle_id}
            ).json()
            client.post(
                f"/buy/{product_id}",
                headers={"Authorization": f"Bearer {buyer['auth_token']}"}
            )
        
        # Get leaderboard
        response = client.get(f"/buy/stats/leaderboard?battle_id={battle_id}")

        assert response.status_code == 200
        data = response.json()
        leaderboard = self._get_leaderboard(data)
        assert len(leaderboard) == 1
        
        entry = leaderboard[0]
        assert entry["seller_id"] == sample_seller["id"]
        assert entry["purchase_count"] == 3
        # Profit per purchase = 1500 - 800 = 700, total = 700 * 3 = 2100
        assert entry["total_profit_cents"] == 2100
        assert entry["total_profit_dollars"] == 21.0
    
    def test_leaderboard_seller_with_no_purchases(
        self, client, battle_id, sample_images, set_phase
    ):
        """Test leaderboard includes sellers with products but no purchases"""
        # Create two sellers
        seller1 = client.post("/createSeller", json={"battle_id": battle_id}).json()
        seller2 = client.post("/createSeller", json={"battle_id": battle_id}).json()
        
        # Both create products
        s1_prod = f"s1-prod-{battle_id[:8]}"
        s2_prod = f"s2-prod-{battle_id[:8]}"

        client.post(
            f"/product/{s1_prod}",
            json={
                "name": "Product 1",
                "short_description": "Test",
                "long_description": "Test",
                "price": 1000,
                "image_ids": [sample_images["01"][0].id],
                "towel_variant": "budget"
            },
            headers={"Authorization": f"Bearer {seller1['auth_token']}"}
        )
        client.post(
            f"/product/{s2_prod}",
            json={
                "name": "Product 2",
                "short_description": "Test",
                "long_description": "Test",
                "price": 2000,
                "image_ids": [sample_images["01"][0].id],
                "towel_variant": "budget"
            },
            headers={"Authorization": f"Bearer {seller2['auth_token']}"}
        )

        # Only seller 1 gets a purchase
        buyer = client.post(
            "/createBuyer",
            json={"battle_id": battle_id}
        ).json()
        set_phase(Phase.BUYER_SHOPPING)
        client.post(
            f"/buy/{s1_prod}",
            headers={"Authorization": f"Bearer {buyer['auth_token']}"}
        )
        
        # Get leaderboard
        response = client.get(f"/buy/stats/leaderboard?battle_id={battle_id}")

        assert response.status_code == 200
        data = response.json()
        leaderboard = self._get_leaderboard(data)
        assert len(leaderboard) == 2
        
        # Find seller 1 and seller 2 in the results
        seller1_data = next((s for s in leaderboard if s["seller_id"] == seller1["id"]), None)
        seller2_data = next((s for s in leaderboard if s["seller_id"] == seller2["id"]), None)
        
        assert seller1_data is not None
        # Profit = 1000 - 800 = 200
        assert seller1_data["total_profit_cents"] == 200
        assert seller1_data["purchase_count"] == 1
        
        assert seller2_data is not None
        assert seller2_data["total_profit_cents"] == 0
        assert seller2_data["purchase_count"] == 0
        
        # Seller 1 should be ranked higher (earlier in list) than seller 2
        seller1_index = leaderboard.index(seller1_data)
        seller2_index = leaderboard.index(seller2_data)
        assert seller1_index < seller2_index
    
    def test_leaderboard_with_free_products(
        self, client, battle_id, sample_seller, sample_buyer, sample_images, set_phase
    ):
        """Test leaderboard with products that have very low price (1 cent)"""
        product_id = f"cheap-prod-{battle_id[:8]}"
        # Create a very low price product (1 cent)
        response = client.post(
            f"/product/{product_id}",
            json={
                "name": "Cheap Product",
                "short_description": "Test",
                "long_description": "Test",
                "price": 1,
                "image_ids": [sample_images["01"][0].id],
                "towel_variant": "budget"
            },
            headers={"Authorization": f"Bearer {sample_seller['auth_token']}"}
        )
        assert response.status_code == 200

        # Purchase the cheap product
        set_phase(Phase.BUYER_SHOPPING)
        client.post(
            f"/buy/{product_id}",
            headers={"Authorization": f"Bearer {sample_buyer['auth_token']}"}
        )
        
        # Get leaderboard
        response = client.get(f"/buy/stats/leaderboard?battle_id={battle_id}")

        assert response.status_code == 200
        data = response.json()
        leaderboard = self._get_leaderboard(data)
        assert len(leaderboard) == 1
        
        entry = leaderboard[0]
        assert entry["seller_id"] == sample_seller["id"]
        assert entry["purchase_count"] == 1
        # Profit = 1 - 800 = -799 (loss)
        assert entry["total_profit_cents"] == -799
        assert entry["total_profit_dollars"] == -7.99
    
    def test_leaderboard_mixed_prices(self, client, battle_id, sample_images, set_phase):
        """Test leaderboard with various price points"""
        # Create seller
        seller = client.post("/createSeller", json={"battle_id": battle_id}).json()
        buyer = client.post("/createBuyer", json={"battle_id": battle_id}).json()
        
        # Create products with different prices (excluding 0 since it's not allowed)
        prices = [1, 99, 1000, 9999, 100000]  # $0.01, $0.99, $10, $99.99, $1000
        product_ids: list[str] = []
        for i, price in enumerate(prices):
            product_id = f"prod-{i}-{battle_id[:8]}"
            client.post(
                f"/product/{product_id}",
                json={
                    "name": f"Product {i}",
                    "short_description": "Test",
                    "long_description": "Test",
                    "price": price,
                    "image_ids": [sample_images["01"][0].id],
                    "towel_variant": "budget"
                },
                headers={"Authorization": f"Bearer {seller['auth_token']}"}
            )
            product_ids.append(product_id)

        set_phase(Phase.BUYER_SHOPPING)
        for i, product_id in enumerate(product_ids):
            client.post(
                f"/buy/{product_id}",
                headers={"Authorization": f"Bearer {buyer['auth_token']}"}
            )
        
        # Get leaderboard
        response = client.get(f"/buy/stats/leaderboard?battle_id={battle_id}")

        assert response.status_code == 200
        data = response.json()
        leaderboard = self._get_leaderboard(data)
        assert len(leaderboard) == 1
        
        entry = leaderboard[0]
        # Calculate expected profit: sum(price - 800) for each price
        # prices = [1, 99, 1000, 9999, 100000]
        # profits = [-799, -701, 200, 9199, 99200] = 107099
        expected_profit = sum(p - 800 for p in prices)
        assert entry["total_profit_cents"] == expected_profit
        assert entry["total_profit_dollars"] == expected_profit / 100.0
        assert entry["purchase_count"] == 5
    
    def test_leaderboard_response_structure(self, client, battle_id, sample_seller, sample_images):
        """Test that leaderboard response has correct structure"""
        response = client.get(f"/buy/stats/leaderboard?battle_id={battle_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "current_round" in data
        assert "rounds" in data
        assert "overall" in data

        assert isinstance(data["rounds"], list)
        if data["rounds"]:
            round_entry = data["rounds"][0]
            assert "round" in round_entry
            assert "is_current_round" in round_entry
            assert "leaderboard" in round_entry
            assert "winners" in round_entry

            leaderboard = round_entry["leaderboard"]
            assert isinstance(leaderboard, list)

            if leaderboard:
                entry = leaderboard[0]
                assert "seller_id" in entry
                assert "purchase_count" in entry
                assert "total_profit_cents" in entry
                assert "total_profit_dollars" in entry

                assert isinstance(entry["seller_id"], str)
                assert isinstance(entry["purchase_count"], int)
                assert isinstance(entry["total_profit_cents"], int)
                assert isinstance(entry["total_profit_dollars"], float)

        assert "leaderboard" in data["overall"]
        assert "winners" in data["overall"]

    def test_leaderboard_across_rounds(
        self,
        client,
        battle_id,
        sample_images,
        set_phase,
        set_round,
    ):
        """Leaderboard should track each round and overall winners."""
        seller1 = client.post("/createSeller", json={"battle_id": battle_id}).json()
        seller2 = client.post("/createSeller", json={"battle_id": battle_id}).json()
        buyer = client.post("/createBuyer", json={"battle_id": battle_id}).json()

        seller1_prod = f"seller1-prod-{battle_id[:8]}"
        seller2_prod = f"seller2-prod-{battle_id[:8]}"

        client.post(
            f"/product/{seller1_prod}",
            json={
                "name": "Round 1 Winner",
                "short_description": "Test",
                "long_description": "Test",
                "price": 5000,
                "image_ids": [sample_images["01"][0].id],
                "towel_variant": "budget",
            },
            headers={"Authorization": f"Bearer {seller1['auth_token']}"},
        )
        client.post(
            f"/product/{seller2_prod}",
            json={
                "name": "Round 2 Winner",
                "short_description": "Test",
                "long_description": "Test",
                "price": 7000,
                "image_ids": [sample_images["01"][0].id],
                "towel_variant": "budget",
            },
            headers={"Authorization": f"Bearer {seller2['auth_token']}"},
        )

        set_phase(Phase.BUYER_SHOPPING)
        # Round 1 purchases – seller 1 wins
        for _ in range(2):
            client.post(
                f"/buy/{seller1_prod}",
                headers={"Authorization": f"Bearer {buyer['auth_token']}"},
            )

        # Move to round 2
        set_round(2)
        set_phase(Phase.BUYER_SHOPPING)
        # Round 2 purchases – seller 2 wins
        for _ in range(3):
            client.post(
                f"/buy/{seller2_prod}",
                headers={"Authorization": f"Bearer {buyer['auth_token']}"},
            )

        response = client.get(f"/buy/stats/leaderboard?battle_id={battle_id}")
        assert response.status_code == 200
        data = response.json()

        assert data["current_round"] == 2
        round1 = self._get_round_data(data, 1)
        round2 = self._get_round_data(data, 2)

        assert round1["winners"] == [seller1["id"]]
        assert round2["winners"] == [seller2["id"]]

        leaderboard_round1 = round1["leaderboard"]
        leaderboard_round2 = round2["leaderboard"]
        seller1_round1 = next(entry for entry in leaderboard_round1 if entry["seller_id"] == seller1["id"])
        seller2_round1 = next(entry for entry in leaderboard_round1 if entry["seller_id"] == seller2["id"])
        seller1_round2 = next(entry for entry in leaderboard_round2 if entry["seller_id"] == seller1["id"])
        seller2_round2 = next(entry for entry in leaderboard_round2 if entry["seller_id"] == seller2["id"])

        assert seller1_round1["purchase_count"] == 2
        assert seller2_round1["purchase_count"] == 0
        assert seller2_round2["purchase_count"] == 3
        assert seller1_round2["purchase_count"] == 0

        overall = self._get_overall(data)
        assert overall[0]["round_wins"] == 1
        assert set(data["overall"]["winners"]) == {seller1["id"], seller2["id"]}


class TestPhaseAdministration:
    """Test administrative phase management endpoints"""

    def test_get_phase_returns_current_phase(self, client, battle_id):
        """Default phase should be seller management"""
        response = client.get(f"/admin/phase?battle_id={battle_id}")
        assert response.status_code == 200
        assert response.json()["phase"] == Phase.SELLER_MANAGEMENT.value

    def test_update_phase_changes_current_phase(self, client, battle_id):
        """Phase update should persist and be retrievable"""
        update_response = client.post(
            "/admin/phase", json={"battle_id": battle_id, "phase": Phase.BUYER_SHOPPING.value}
        )
        assert update_response.status_code == 200
        assert update_response.json()["phase"] == Phase.BUYER_SHOPPING.value

        fetch_response = client.get(f"/admin/phase?battle_id={battle_id}")
        assert fetch_response.status_code == 200
        assert fetch_response.json()["phase"] == Phase.BUYER_SHOPPING.value

    def test_update_phase_requires_valid_admin_key(self, client, battle_id):
        """Invalid admin key should be rejected"""
        response = client.post(
            "/admin/phase",
            json={"battle_id": battle_id, "phase": Phase.BUYER_SHOPPING.value},
            headers={"X-Admin-Key": "wrong-key"},
        )
        assert response.status_code == 401
        assert "Invalid or missing admin key" in response.json()["detail"]


class TestAPIHealth:
    """Test API health and basic endpoints"""
    
    def test_root_endpoint(self, client, battle_id, sample_images):
        """Test root endpoint returns correct information"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "docs" in data
    
    def test_health_endpoint(self, client, battle_id, sample_images):
        """Test health check endpoint"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
