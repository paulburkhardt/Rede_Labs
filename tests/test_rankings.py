import pytest
import time
from app.services.phase_manager import Phase


@pytest.fixture
def sample_products(client, sample_seller, sample_images):
    """Create multiple sample products for testing"""
    products = []
    product_names = ["Towel A", "Towel B", "Towel C"]
    
    for name in product_names:
        response = client.post(
            f"/product/{name.lower().replace(' ', '-')}",
            json={
                "name": name,
                "short_description": f"{name} description",
                "long_description": f"{name} long description",
                "price": 1999,
                "image_ids": [sample_images["01"][0].id],
                "towel_variant": "budget"
            },
            headers={"Authorization": f"Bearer {sample_seller['auth_token']}"}
        )
        assert response.status_code == 200
        products.append(response.json())
    
    return products


class TestRankingInitialization:
    def test_initialize_rankings_success(self, client, sample_products):
        """Test that rankings can be initialized randomly"""
        response = client.post("/rankings/initialize")
        
        assert response.status_code == 200
        result = response.json()
        assert result["updated_count"] == 3
        assert "Initialized" in result["message"]
        
        # Verify rankings were set
        search_response = client.get("/search?q=")
        products = search_response.json()
        
        # All products should have rankings
        rankings = [p["ranking"] for p in products]
        assert None not in rankings
        assert len(set(rankings)) == 3  # All rankings should be unique
        assert set(rankings) == {1, 2, 3}  # Should be ranks 1, 2, 3
    
    def test_initialize_rankings_no_products(self, client):
        """Test initialization when no products exist"""
        response = client.post("/rankings/initialize")
        
        assert response.status_code == 200
        result = response.json()
        assert result["updated_count"] == 0
        assert "No products" in result["message"]
    
    def test_initialize_rankings_multiple_times(self, client, sample_products):
        """Test that re-initialization changes rankings"""
        # First initialization
        response1 = client.post("/rankings/initialize")
        assert response1.status_code == 200
        
        search1 = client.get("/search?q=")
        products1 = search1.json()
        rankings1 = {p["id"]: p["ranking"] for p in products1}
        
        # Second initialization
        response2 = client.post("/rankings/initialize")
        assert response2.status_code == 200
        
        search2 = client.get("/search?q=")
        products2 = search2.json()
        rankings2 = {p["id"]: p["ranking"] for p in products2}
        
        # Rankings should potentially be different (though could be same by chance)
        # At minimum, verify they're all still valid
        assert len(rankings2) == 3
        assert set(rankings2.values()) == {1, 2, 3}


class TestRankingUpdateBySales:
    def test_update_rankings_by_sales_no_purchases(self, client, sample_products):
        """Test ranking update when no purchases have been made"""
        response = client.post("/rankings/update-by-sales")
        
        assert response.status_code == 200
        result = response.json()
        assert result["updated_count"] == 3
        assert "based on sales" in result["message"]
        
        # All products should have 0 sales, so ranking order is arbitrary but valid
        search_response = client.get("/search?q=")
        products = search_response.json()
        rankings = [p["ranking"] for p in products]
        assert set(rankings) == {1, 2, 3}
    
    def test_update_rankings_by_sales_with_purchases(
        self, client, sample_seller, sample_buyer, sample_products, sample_images, set_phase
    ):
        """Test that rankings are updated based on actual sales"""
        # Create three products
        product_ids = [p["product_id"] for p in sample_products]
        
        # Set phase to allow purchases
        set_phase(Phase.BUYER_SHOPPING)
        
        # Make purchases: product 0 gets 3 sales, product 1 gets 1 sale, product 2 gets 0 sales
        for _ in range(3):
            purchase_response = client.post(
                f"/buy/{product_ids[0]}",
                headers={"Authorization": f"Bearer {sample_buyer['auth_token']}"}
            )
            assert purchase_response.status_code == 200, f"Purchase failed: {purchase_response.text}"
        
        purchase_response = client.post(
            f"/buy/{product_ids[1]}",
            headers={"Authorization": f"Bearer {sample_buyer['auth_token']}"}
        )
        assert purchase_response.status_code == 200, f"Purchase failed: {purchase_response.text}"
        
        # Update rankings
        response = client.post("/rankings/update-by-sales")
        assert response.status_code == 200
        result = response.json()
        
        # Check top products info
        assert "top_products" in result
        top_products = result["top_products"]
        
        # Product 0 should be rank 1 (most sales)
        assert top_products[0]["ranking"] == 1
        assert top_products[0]["sales_count"] == 3
        
        # Product 1 should be rank 2
        assert top_products[1]["ranking"] == 2
        assert top_products[1]["sales_count"] == 1
        
        # Product 2 should be rank 3 (no sales)
        assert top_products[2]["ranking"] == 3
        assert top_products[2]["sales_count"] == 0
        
        # Verify rankings in search results
        search_response = client.get("/search?q=")
        products = search_response.json()
        
        # Products should be ordered by ranking (1, 2, 3)
        assert products[0]["ranking"] == 1
        assert products[1]["ranking"] == 2
        assert products[2]["ranking"] == 3
    
    def test_update_rankings_reflects_in_search_order(
        self, client, sample_seller, sample_buyer, sample_products, set_phase
    ):
        """Test that updated rankings affect search result ordering"""
        product_ids = [p["product_id"] for p in sample_products]
        
        # Set phase to allow purchases
        set_phase(Phase.BUYER_SHOPPING)
        
        # Make product 2 the best seller
        for _ in range(5):
            client.post(
                f"/buy/{product_ids[2]}",
                headers={"Authorization": f"Bearer {sample_buyer['auth_token']}"}
            )
        
        # Update rankings
        client.post("/rankings/update-by-sales")
        
        # Search should return product 2 first
        search_response = client.get("/search?q=towel")
        products = search_response.json()
        
        assert len(products) == 3
        assert products[0]["id"] == product_ids[2]
        assert products[0]["ranking"] == 1
    
    def test_update_rankings_no_products(self, client):
        """Test update when no products exist"""
        response = client.post("/rankings/update-by-sales")
        
        assert response.status_code == 200
        result = response.json()
        assert result["updated_count"] == 0
        assert "No products" in result["message"]


class TestRankingWorkflow:
    def test_complete_ranking_workflow(
        self, client, sample_seller, sample_buyer, sample_products, set_phase
    ):
        """Test the complete workflow: initialize -> purchases -> update"""
        # Step 1: Initialize rankings randomly
        init_response = client.post("/rankings/initialize")
        assert init_response.status_code == 200
        
        # Step 2: Set phase to allow purchases
        set_phase(Phase.BUYER_SHOPPING)
        
        # Step 3: Make some purchases
        product_ids = [p["product_id"] for p in sample_products]
        client.post(
            f"/buy/{product_ids[1]}",
            headers={"Authorization": f"Bearer {sample_buyer['auth_token']}"}
        )
        client.post(
            f"/buy/{product_ids[1]}",
            headers={"Authorization": f"Bearer {sample_buyer['auth_token']}"}
        )
        
        # Step 4: Update rankings based on sales
        update_response = client.post("/rankings/update-by-sales")
        assert update_response.status_code == 200
        
        # Step 5: Verify product 1 is now rank 1
        search_response = client.get("/search?q=")
        products = search_response.json()
        
        best_product = products[0]
        assert best_product["id"] == product_ids[1]
        assert best_product["ranking"] == 1
