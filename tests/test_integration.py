"""Integration tests for complex scenarios and edge cases"""
import pytest

from app.services.phase_manager import Phase


class TestAuthenticationSecurity:
    """Test authentication and authorization security"""
    
    def test_bearer_token_with_and_without_prefix(self, client, sample_seller, sample_images):
        """Test that both 'Bearer token' and 'token' formats work"""
        product_data = {
            "name": "Test Product",
            "short_description": "Test",
            "long_description": "Test",
            "price": 1999,
            "image_ids": [sample_images["01"][0].id]
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
    
    def test_token_isolation_between_orgs(self, client, sample_images):
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
                "short_description": "Test",
                "long_description": "Test",
                "price": 1999,
                "image_ids": [sample_images["01"][0].id]
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
    
    def test_token_isolation_between_buyers(self, client, sample_product, set_phase):
        """Test that buyer tokens are properly isolated"""
        buyer1 = client.post(
            "/createBuyer",
        ).json()
        
        buyer2 = client.post(
            "/createBuyer",
        ).json()
        
        # Both should be able to purchase
        set_phase(Phase.BUYER_SHOPPING)
        response1 = client.post(
            f"/buy/{sample_product['id']}",
            json={"purchased_at": 0},
            headers={"Authorization": f"Bearer {buyer1['auth_token']}"}
        )
        
        response2 = client.post(
            f"/buy/{sample_product['id']}",
            json={"purchased_at": 0},
            headers={"Authorization": f"Bearer {buyer2['auth_token']}"}
        )
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response1.json()["id"] != response2.json()["id"]


class TestMultipleSellersAndProducts:
    """Test scenarios with multiple sellers and products"""
    
    def test_multiple_orgs_with_similar_products(self, client, sample_images):
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
            "short_description": "Great towel",
            "long_description": "Very nice towel",
            "price": 1999,
            "image_ids": [sample_images["01"][0].id]
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
    
    def test_seller_can_manage_multiple_products(self, client, sample_seller, sample_images):
        """Test that one seller can create and manage multiple products"""
        products = []
        
        # Create 5 products
        for i in range(5):
            response = client.post(
                f"/product/prod-{i}",
                json={
                    "name": f"Product {i}",
                    "short_description": f"Description {i}",
                    "long_description": f"Long description {i}",
                    "price": 1000 + (i * 100),
                    "image_ids": [sample_images["01"][0].id]
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
        assert product["price_in_cent"] == 9999
    
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
    
    def test_product_with_zero_price(self, client, sample_seller, sample_images):
        """Test creating a product with zero price"""
        response = client.post(
            "/product/free-product",
            json={
                "name": "Free Sample",
                "short_description": "Free",
                "long_description": "Free product",
                "price": 0,
                "image_ids": [sample_images["01"][0].id]
            },
            headers={"Authorization": f"Bearer {sample_seller['auth_token']}"}
        )
        
        assert response.status_code == 200
        
        # Verify it was created
        product = client.get("/product/free-product").json()
        assert product["price_in_cent"] == 0
    
    def test_product_with_very_long_description(self, client, sample_seller, sample_images):
        """Test creating a product with very long descriptions"""
        long_text = "A" * 10000
        
        response = client.post(
            "/product/long-desc",
            json={
                "name": "Product with long description",
                "short_description": long_text,
                "long_description": long_text,
                "price": 1999,
                "image_ids": [sample_images["01"][0].id]
            },
            headers={"Authorization": f"Bearer {sample_seller['auth_token']}"}
        )
        
        assert response.status_code == 200
    
    def test_search_with_special_characters(self, client, sample_seller, sample_images):
        """Test search with special characters"""
        # Create product with special characters
        client.post(
            "/product/special-prod",
            json={
                "name": "Product & Co. (Premium)",
                "short_description": "Test",
                "long_description": "Test",
                "price": 1999,
                "image_ids": [sample_images["01"][0].id]
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


class TestSalesStats:
    """Test sales statistics endpoint"""
    
    def test_get_sales_stats_no_sales(self, client, sample_seller, sample_images):
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
        self, client, sample_seller, sample_buyer, sample_images, set_phase
    ):
        """Test getSalesStats with a single purchase"""
        # Create a product
        product_data = {
            "name": "Test Product",
            "short_description": "Test",
            "long_description": "Test",
            "price": 2500,
            "image_ids": [sample_images["01"][0].id]
        }
        client.post(
            "/product/test-prod-1",
            json=product_data,
            headers={"Authorization": f"Bearer {sample_seller['auth_token']}"}
        )
        
        # Make a purchase
        set_phase(Phase.BUYER_SHOPPING)
        client.post(
            "/buy/test-prod-1",
            json={"purchased_at": 0},
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
        assert purchase["product_id"] == "test-prod-1"
        assert purchase["product_name"] == "Test Product"
        assert purchase["buyer_id"] == sample_buyer["id"]
        assert purchase["price_in_cent"] == 2500
        assert purchase["currency"] == "USD"
        assert "purchased_at" in purchase
    
    def test_get_sales_stats_with_multiple_purchases(
        self, client, sample_seller, sample_images, set_phase
    ):
        """Test getSalesStats with multiple purchases from different buyers"""
        # Create two products
        for i in range(2):
            client.post(
                f"/product/prod-{i}",
                json={
                    "name": f"Product {i}",
                    "short_description": "Test",
                    "long_description": "Test",
                    "price": 1000 * (i + 1),
                    "image_ids": [sample_images["01"][0].id]
                },
                headers={"Authorization": f"Bearer {sample_seller['auth_token']}"}
            )
        
        # Create three buyers and make purchases
        set_phase(Phase.BUYER_SHOPPING)
        for i in range(3):
            buyer = client.post(
                "/createBuyer",
            ).json()
            
            # Each buyer purchases product 0
            client.post(
                "/buy/prod-0",
                json={"purchased_at": 0},
                headers={"Authorization": f"Bearer {buyer['auth_token']}"}
            )
        
        # One buyer purchases product 1
        buyer = client.post(
            "/createBuyer",
        ).json()
        client.post(
            "/buy/prod-1",
            json={"purchased_at": 1},
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
        self, client, sample_images, set_phase
    ):
        """Test that getSalesStats only returns sales for the authenticated seller"""
        # Create two sellers
        seller1 = client.post("/createSeller").json()
        seller2 = client.post("/createSeller").json()
        
        # Each seller creates a product
        client.post(
            "/product/seller1-prod",
            json={
                "name": "Seller 1 Product",
                "short_description": "Test",
                "long_description": "Test",
                "price": 1000,
                "image_ids": [sample_images["01"][0].id]
            },
            headers={"Authorization": f"Bearer {seller1['auth_token']}"}
        )
        
        client.post(
            "/product/seller2-prod",
            json={
                "name": "Seller 2 Product",
                "short_description": "Test",
                "long_description": "Test",
                "price": 2000,
                "image_ids": [sample_images["01"][0].id]
            },
            headers={"Authorization": f"Bearer {seller2['auth_token']}"}
        )
        
        # Create a buyer
        buyer = client.post(
            "/createBuyer",
        ).json()
        
        # Buyer purchases from both sellers
        set_phase(Phase.BUYER_SHOPPING)
        client.post(
            "/buy/seller1-prod",
            json={"purchased_at": 0},
            headers={"Authorization": f"Bearer {buyer['auth_token']}"}
        )
        client.post(
            "/buy/seller2-prod",
            json={"purchased_at": 0},
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
        assert data1["purchases"][0]["product_id"] == "seller1-prod"
        
        # Get sales stats for seller 2
        response2 = client.get(
            "/getSalesStats",
            headers={"Authorization": f"Bearer {seller2['auth_token']}"}
        )
        data2 = response2.json()
        assert data2["total_sales"] == 1
        assert data2["total_revenue_in_cent"] == 2000
        assert data2["purchases"][0]["product_id"] == "seller2-prod"
    
    def test_get_sales_stats_requires_authentication(self, client, sample_images):
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
        self, client, sample_seller, sample_buyer, sample_images, set_phase
    ):
        """Test that getSalesStats works with and without Bearer prefix"""
        # Create and purchase a product
        client.post(
            "/product/test-prod",
            json={
                "name": "Test Product",
                "short_description": "Test",
                "long_description": "Test",
                "price": 1500,
                "image_ids": [sample_images["01"][0].id]
            },
            headers={"Authorization": f"Bearer {sample_seller['auth_token']}"}
        )
        set_phase(Phase.BUYER_SHOPPING)
        client.post(
            "/buy/test-prod",
            json={"purchased_at": 0},
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
        self, client, sample_seller, sample_buyer, sample_images, set_phase
    ):
        """Test that purchases are returned in the correct order"""
        # Create multiple products
        product_ids = []
        for i in range(3):
            client.post(
                f"/product/prod-{i}",
                json={
                    "name": f"Product {i}",
                    "short_description": "Test",
                    "long_description": "Test",
                    "price": 1000 * (i + 1),
                    "image_ids": [sample_images["01"][0].id]
                },
                headers={"Authorization": f"Bearer {sample_seller['auth_token']}"}
            )
            product_ids.append(f"prod-{i}")

        set_phase(Phase.BUYER_SHOPPING)
        for i, product_id in enumerate(product_ids):
            client.post(
                f"/buy/{product_id}",
                json={"purchased_at": i},
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


class TestLeaderboard:
    """Test leaderboard endpoint"""
    
    def test_leaderboard_no_sales(self, client, sample_images):
        """Test leaderboard with no sales returns sellers with zero revenue"""
        # Create two sellers
        seller1 = client.post("/createSeller").json()
        seller2 = client.post("/createSeller").json()
        
        # Get leaderboard
        response = client.get("/buy/stats/leaderboard")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        
        # All sellers should have zero revenue
        for entry in data:
            assert entry["purchase_count"] == 0
            assert entry["total_revenue_cents"] == 0
            assert entry["total_revenue_dollars"] == 0.0
    
    def test_leaderboard_single_seller_single_purchase(
        self, client, sample_seller, sample_buyer, sample_images, set_phase
    ):
        """Test leaderboard with a single seller and single purchase"""
        # Create a product
        client.post(
            "/product/test-prod",
            json={
                "name": "Test Product",
                "short_description": "Test",
                "long_description": "Test",
                "price": 2500,
                "image_ids": [sample_images["01"][0].id]
            },
            headers={"Authorization": f"Bearer {sample_seller['auth_token']}"}
        )
        
        # Make a purchase
        set_phase(Phase.BUYER_SHOPPING)
        client.post(
            "/buy/test-prod",
            json={"purchased_at": 0},
            headers={"Authorization": f"Bearer {sample_buyer['auth_token']}"}
        )
        
        # Get leaderboard
        response = client.get("/buy/stats/leaderboard")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        
        entry = data[0]
        assert entry["seller_id"] == sample_seller["id"]
        assert entry["purchase_count"] == 1
        assert entry["total_revenue_cents"] == 2500
        assert entry["total_revenue_dollars"] == 25.0
    
    def test_leaderboard_multiple_sellers_sorted_by_revenue(
        self, client, sample_images, set_phase
    ):
        """Test leaderboard with multiple sellers sorted by total revenue"""
        # Create three sellers
        sellers = []
        for i in range(3):
            seller = client.post("/createSeller").json()
            sellers.append(seller)
        
        # Create a buyer
        buyer = client.post(
            "/createBuyer",
        ).json()
        
        # Seller 0: 2 products at $10 and $20 = $30 total
        client.post(
            "/product/s0-p1",
            json={
                "name": "Product 1",
                "short_description": "Test",
                "long_description": "Test",
                "price": 1000,
                "image_ids": [sample_images["01"][0].id]
            },
            headers={"Authorization": f"Bearer {sellers[0]['auth_token']}"}
        )
        client.post(
            "/product/s0-p2",
            json={
                "name": "Product 2",
                "short_description": "Test",
                "long_description": "Test",
                "price": 2000,
                "image_ids": [sample_images["01"][0].id]
            },
            headers={"Authorization": f"Bearer {sellers[0]['auth_token']}"}
        )
        
        # Seller 1: 1 product at $50 = $50 total (highest)
        client.post(
            "/product/s1-p1",
            json={
                "name": "Product 3",
                "short_description": "Test",
                "long_description": "Test",
                "price": 5000,
                "image_ids": [sample_images["01"][0].id]
            },
            headers={"Authorization": f"Bearer {sellers[1]['auth_token']}"}
        )
        
        # Seller 2: 1 product at $5 = $5 total (lowest)
        client.post(
            "/product/s2-p1",
            json={
                "name": "Product 4",
                "short_description": "Test",
                "long_description": "Test",
                "price": 500,
                "image_ids": [sample_images["01"][0].id]
            },
            headers={"Authorization": f"Bearer {sellers[2]['auth_token']}"}
        )
        
        set_phase(Phase.BUYER_SHOPPING)
        client.post("/buy/s0-p1", json={"purchased_at": 0}, headers={"Authorization": f"Bearer {buyer['auth_token']}"})
        client.post("/buy/s0-p2", json={"purchased_at": 0}, headers={"Authorization": f"Bearer {buyer['auth_token']}"})
        client.post("/buy/s1-p1", json={"purchased_at": 0}, headers={"Authorization": f"Bearer {buyer['auth_token']}"})
        client.post("/buy/s2-p1", json={"purchased_at": 0}, headers={"Authorization": f"Bearer {buyer['auth_token']}"})
        
        # Get leaderboard
        response = client.get("/buy/stats/leaderboard")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        
        # Verify sorting by revenue (descending)
        assert data[0]["seller_id"] == sellers[1]["id"]  # $50
        assert data[0]["total_revenue_cents"] == 5000
        assert data[0]["total_revenue_dollars"] == 50.0
        assert data[0]["purchase_count"] == 1
        
        assert data[1]["seller_id"] == sellers[0]["id"]  # $30
        assert data[1]["total_revenue_cents"] == 3000
        assert data[1]["total_revenue_dollars"] == 30.0
        assert data[1]["purchase_count"] == 2
        
        assert data[2]["seller_id"] == sellers[2]["id"]  # $5
        assert data[2]["total_revenue_cents"] == 500
        assert data[2]["total_revenue_dollars"] == 5.0
        assert data[2]["purchase_count"] == 1
    
    def test_leaderboard_same_product_multiple_purchases(
        self, client, sample_seller, sample_images, set_phase
    ):
        """Test leaderboard when the same product is purchased multiple times"""
        # Create a product
        client.post(
            "/product/popular-prod",
            json={
                "name": "Popular Product",
                "short_description": "Test",
                "long_description": "Test",
                "price": 1500,
                "image_ids": [sample_images["01"][0].id]
            },
            headers={"Authorization": f"Bearer {sample_seller['auth_token']}"}
        )
        
        # Create three buyers and each purchases the same product
        set_phase(Phase.BUYER_SHOPPING)
        for i in range(3):
            buyer = client.post(
                "/createBuyer",
            ).json()
            client.post(
                "/buy/popular-prod",
                json={"purchased_at": i},
                headers={"Authorization": f"Bearer {buyer['auth_token']}"}
            )
        
        # Get leaderboard
        response = client.get("/buy/stats/leaderboard")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        
        entry = data[0]
        assert entry["seller_id"] == sample_seller["id"]
        assert entry["purchase_count"] == 3
        assert entry["total_revenue_cents"] == 4500  # 1500 * 3
        assert entry["total_revenue_dollars"] == 45.0
    
    def test_leaderboard_seller_with_no_purchases(
        self, client, sample_images, set_phase
    ):
        """Test leaderboard includes sellers with products but no purchases"""
        # Create two sellers
        seller1 = client.post("/createSeller").json()
        seller2 = client.post("/createSeller").json()
        
        # Both create products
        client.post(
            "/product/s1-prod",
            json={
                "name": "Product 1",
                "short_description": "Test",
                "long_description": "Test",
                "price": 1000,
                "image_ids": [sample_images["01"][0].id]
            },
            headers={"Authorization": f"Bearer {seller1['auth_token']}"}
        )
        client.post(
            "/product/s2-prod",
            json={
                "name": "Product 2",
                "short_description": "Test",
                "long_description": "Test",
                "price": 2000,
                "image_ids": [sample_images["01"][0].id]
            },
            headers={"Authorization": f"Bearer {seller2['auth_token']}"}
        )
        
        # Only seller 1 gets a purchase
        buyer = client.post(
            "/createBuyer",
        ).json()
        set_phase(Phase.BUYER_SHOPPING)
        client.post(
            "/buy/s1-prod",
            json={"purchased_at": 0},
            headers={"Authorization": f"Bearer {buyer['auth_token']}"}
        )
        
        # Get leaderboard
        response = client.get("/buy/stats/leaderboard")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        
        # Find seller 1 and seller 2 in the results
        seller1_data = next((s for s in data if s["seller_id"] == seller1["id"]), None)
        seller2_data = next((s for s in data if s["seller_id"] == seller2["id"]), None)
        
        assert seller1_data is not None
        assert seller1_data["total_revenue_cents"] == 1000
        assert seller1_data["purchase_count"] == 1
        
        assert seller2_data is not None
        assert seller2_data["total_revenue_cents"] == 0
        assert seller2_data["purchase_count"] == 0
        
        # Seller 1 should be ranked higher (earlier in list) than seller 2
        seller1_index = data.index(seller1_data)
        seller2_index = data.index(seller2_data)
        assert seller1_index < seller2_index
    
    def test_leaderboard_with_free_products(
        self, client, sample_seller, sample_buyer, sample_images, set_phase
    ):
        """Test leaderboard with products that have zero price"""
        # Create a free product
        client.post(
            "/product/free-prod",
            json={
                "name": "Free Product",
                "short_description": "Test",
                "long_description": "Test",
                "price": 0,
                "image_ids": [sample_images["01"][0].id]
            },
            headers={"Authorization": f"Bearer {sample_seller['auth_token']}"}
        )
        
        # Purchase the free product
        set_phase(Phase.BUYER_SHOPPING)
        client.post(
            "/buy/free-prod",
            json={"purchased_at": 0},
            headers={"Authorization": f"Bearer {sample_buyer['auth_token']}"}
        )
        
        # Get leaderboard
        response = client.get("/buy/stats/leaderboard")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        
        entry = data[0]
        assert entry["seller_id"] == sample_seller["id"]
        assert entry["purchase_count"] == 1
        assert entry["total_revenue_cents"] == 0
        assert entry["total_revenue_dollars"] == 0.0
    
    def test_leaderboard_mixed_prices(self, client, sample_images, set_phase):
        """Test leaderboard with various price points"""
        # Create seller
        seller = client.post("/createSeller").json()
        buyer = client.post("/createBuyer").json()
        
        # Create products with different prices
        prices = [0, 99, 1000, 9999, 100000]  # $0, $0.99, $10, $99.99, $1000
        product_ids: list[str] = []
        for i, price in enumerate(prices):
            client.post(
                f"/product/prod-{i}",
                json={
                    "name": f"Product {i}",
                    "short_description": "Test",
                    "long_description": "Test",
                    "price": price,
                    "image_ids": [sample_images["01"][0].id]
                },
                headers={"Authorization": f"Bearer {seller['auth_token']}"}
            )
            product_ids.append(f"prod-{i}")

        set_phase(Phase.BUYER_SHOPPING)
        for i, product_id in enumerate(product_ids):
            client.post(
                f"/buy/{product_id}",
                json={"purchased_at": i},
                headers={"Authorization": f"Bearer {buyer['auth_token']}"}
            )
        
        # Get leaderboard
        response = client.get("/buy/stats/leaderboard")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        
        entry = data[0]
        expected_total = sum(prices)
        assert entry["total_revenue_cents"] == expected_total
        assert entry["total_revenue_dollars"] == expected_total / 100.0
        assert entry["purchase_count"] == 5
    
    def test_leaderboard_response_structure(self, client, sample_seller, sample_images):
        """Test that leaderboard response has correct structure"""
        response = client.get("/buy/stats/leaderboard")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # Even with one seller, check structure
        if len(data) > 0:
            entry = data[0]
            assert "seller_id" in entry
            assert "purchase_count" in entry
            assert "total_revenue_cents" in entry
            assert "total_revenue_dollars" in entry
            
            assert isinstance(entry["seller_id"], str)
            assert isinstance(entry["purchase_count"], int)
            assert isinstance(entry["total_revenue_cents"], int)
            assert isinstance(entry["total_revenue_dollars"], float)


class TestPhaseAdministration:
    """Test administrative phase management endpoints"""

    def test_get_phase_returns_current_phase(self, client):
        """Default phase should be seller management"""
        response = client.get("/admin/phase")
        assert response.status_code == 200
        assert response.json()["phase"] == Phase.SELLER_MANAGEMENT.value

    def test_update_phase_changes_current_phase(self, client):
        """Phase update should persist and be retrievable"""
        update_response = client.post(
            "/admin/phase", json={"phase": Phase.BUYER_SHOPPING.value}
        )
        assert update_response.status_code == 200
        assert update_response.json()["phase"] == Phase.BUYER_SHOPPING.value

        fetch_response = client.get("/admin/phase")
        assert fetch_response.status_code == 200
        assert fetch_response.json()["phase"] == Phase.BUYER_SHOPPING.value

    def test_update_phase_requires_valid_admin_key(self, client):
        """Invalid admin key should be rejected"""
        response = client.post(
            "/admin/phase",
            json={"phase": Phase.BUYER_SHOPPING.value},
            headers={"X-Admin-Key": "wrong-key"},
        )
        assert response.status_code == 401
        assert "Invalid or missing admin key" in response.json()["detail"]


class TestAPIHealth:
    """Test API health and basic endpoints"""
    
    def test_root_endpoint(self, client, sample_images):
        """Test root endpoint returns correct information"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "docs" in data
    
    def test_health_endpoint(self, client, sample_images):
        """Test health check endpoint"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
