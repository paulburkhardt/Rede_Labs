"""Comprehensive tests for the new image system"""
import pytest


class TestImageQueryEndpoints:
    """Test image query endpoints"""
    
    def test_get_all_images_grouped_by_product_number(self, client, battle_id, sample_images):
        """Test getting all images grouped by product_number"""
        response = client.get("/images")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have 3 product numbers
        assert "01" in data
        assert "02" in data
        assert "03" in data
        
        # Check counts
        assert len(data["01"]) == 3
        assert len(data["02"]) == 2
        assert len(data["03"]) == 4
        
        # Verify structure of first image
        first_image = data["01"][0]
        assert "id" in first_image
        assert "image_description" in first_image
        assert "product_number" in first_image
        assert first_image["product_number"] == "01"
        
        # Verify no base64 in response
        assert "base64" not in first_image
    
    def test_get_images_by_product_number(self, client, battle_id, sample_images):
        """Test getting images for a specific product_number"""
        response = client.get("/images/product-number/01")
        
        assert response.status_code == 200
        images = response.json()
        
        assert len(images) == 3
        for img in images:
            assert img["product_number"] == "01"
            assert "id" in img
            assert "image_description" in img
            assert "base64" not in img
    
    def test_get_images_by_nonexistent_product_number(self, client, battle_id, sample_images):
        """Test getting images for a product_number that doesn't exist"""
        response = client.get("/images/product-number/99")
        
        assert response.status_code == 404
        assert "No images found" in response.json()["detail"]
    
    def test_get_available_product_numbers(self, client, battle_id, sample_images):
        """Test getting list of available product_numbers"""
        response = client.get("/images/product-numbers")
        
        assert response.status_code == 200
        product_numbers = response.json()
        
        assert isinstance(product_numbers, list)
        assert "01" in product_numbers
        assert "02" in product_numbers
        assert "03" in product_numbers
        assert len(product_numbers) == 3  # Uncategorized not included


class TestProductCreationWithImages:
    """Test product creation with the new image system"""
    
    def test_create_product_with_valid_images(self, client, battle_id, sample_seller, sample_images):
        """Test creating a product with valid image IDs from same product_number"""
        image_ids = [img.id for img in sample_images["01"][:2]]
        
        product_data = {
            "name": "Test Towel",
            "short_description": "Soft towel",
            "long_description": "Very soft towel",
            "price": 2999,
            "image_ids": image_ids,
        "towel_variant": "budget"
        }
        
        response = client.post(
            "/product/towel-001",
            json=product_data,
            headers={"Authorization": f"Bearer {sample_seller['auth_token']}"}
        )
        
        assert response.status_code == 200
        assert response.json()["product_id"] == "towel-001"
    
    def test_create_product_with_single_image(self, client, battle_id, sample_seller, sample_images):
        """Test creating a product with a single image"""
        image_ids = [sample_images["02"][0].id]
        
        product_data = {
            "name": "Single Image Product",
            "short_description": "Test",
            "long_description": "Test",
            "price": 1999,
            "image_ids": image_ids,
        "towel_variant": "mid_tier"  # Category 02 = mid_tier
        }
        
        response = client.post(
            "/product/single-img-prod",
            json=product_data,
            headers={"Authorization": f"Bearer {sample_seller['auth_token']}"}
        )
        
        assert response.status_code == 200
    
    def test_create_product_with_all_images_from_category(self, client, battle_id, sample_seller, sample_images):
        """Test creating a product with all images from a category"""
        image_ids = [img.id for img in sample_images["03"]]  # All 4 images
        
        product_data = {
            "name": "Multi Image Product",
            "short_description": "Test",
            "long_description": "Test",
            "price": 1999,
            "image_ids": image_ids,
        "towel_variant": "premium"  # Category 03 = premium
        }
        
        response = client.post(
            "/product/multi-img-prod",
            json=product_data,
            headers={"Authorization": f"Bearer {sample_seller['auth_token']}"}
        )
        
        assert response.status_code == 200
    
    def test_create_product_without_images(self, client, battle_id, sample_seller):
        """Test that creating a product without images fails"""
        product_data = {
            "name": "No Image Product",
            "short_description": "Test",
            "long_description": "Test",
            "price": 1999,
            "image_ids": [],
            "towel_variant": "budget",
        }
        
        response = client.post(
            "/product/no-img-prod",
            json=product_data,
            headers={"Authorization": f"Bearer {sample_seller['auth_token']}"}
        )
        
        assert response.status_code == 422  # Pydantic validation error
        response_data = response.json()
        # Check that the validation error mentions images are required
        assert "image_ids" in str(response_data).lower()
        assert "required" in str(response_data).lower() or "at least one" in str(response_data).lower()
    
    def test_create_product_with_nonexistent_image_ids(self, client, battle_id, sample_seller):
        """Test that using non-existent image IDs fails"""
        product_data = {
            "name": "Bad Image Product",
            "short_description": "Test",
            "long_description": "Test",
            "price": 1999,
            "image_ids": ["fake-id-1", "fake-id-2"],
            "towel_variant": "budget",
        }
        
        response = client.post(
            "/product/bad-img-prod",
            json=product_data,
            headers={"Authorization": f"Bearer {sample_seller['auth_token']}"}
        )
        
        assert response.status_code == 404
        assert "Images not found" in response.json()["detail"]
    
    def test_create_product_with_mixed_product_numbers(self, client, battle_id, sample_seller, sample_images):
        """Test that mixing images from different product_numbers fails"""
        # Mix images from product_number 01 and 02
        image_ids = [
            sample_images["01"][0].id,
            sample_images["02"][0].id
        ]
        
        product_data = {
            "name": "Mixed Images Product",
            "short_description": "Test",
            "long_description": "Test",
            "price": 1999,
            "image_ids": image_ids,
            "towel_variant": "budget",
        }
        
        response = client.post(
            "/product/mixed-img-prod",
            json=product_data,
            headers={"Authorization": f"Bearer {sample_seller['auth_token']}"}
        )
        
        assert response.status_code == 400
        assert "same product_number" in response.json()["detail"]
        assert "01" in response.json()["detail"]
        assert "02" in response.json()["detail"]
    
    def test_create_product_with_uncategorized_image(self, client, battle_id, sample_seller, sample_images):
        """Test that using images without product_number fails"""
        image_ids = [sample_images["uncategorized"].id]
        
        product_data = {
            "name": "Uncategorized Image Product",
            "short_description": "Test",
            "long_description": "Test",
            "price": 1999,
            "image_ids": image_ids,
            "towel_variant": "budget",
        }
        
        response = client.post(
            "/product/uncat-img-prod",
            json=product_data,
            headers={"Authorization": f"Bearer {sample_seller['auth_token']}"}
        )
        
        assert response.status_code == 400
        assert "product_number assigned" in response.json()["detail"]
    
    def test_create_product_with_partial_nonexistent_images(self, client, battle_id, sample_seller, sample_images):
        """Test that mixing valid and invalid image IDs fails"""
        image_ids = [
            sample_images["01"][0].id,
            "fake-id-999"
        ]
        
        product_data = {
            "name": "Partial Bad Images",
            "short_description": "Test",
            "long_description": "Test",
            "price": 1999,
            "image_ids": image_ids,
            "towel_variant": "budget",
        }
        
        response = client.post(
            "/product/partial-bad-prod",
            json=product_data,
            headers={"Authorization": f"Bearer {sample_seller['auth_token']}"}
        )
        
        assert response.status_code == 404
        assert "fake-id-999" in response.json()["detail"]


class TestProductUpdateWithImages:
    """Test product update with the new image system"""
    
    def test_update_product_images(self, client, battle_id, sample_product, sample_images):
        """Test updating product images to different ones from same category"""
        # Original product uses all 3 images from category 01
        # Update to use only 2 different images from category 01
        new_image_ids = [sample_images["01"][1].id, sample_images["01"][2].id]
        
        update_data = {
            "image_ids": new_image_ids,
            "towel_variant": "budget",
        }
        
        response = client.patch(
            f"/product/{sample_product['id']}",
            json=update_data,
            headers={"Authorization": f"Bearer {sample_product['seller']['auth_token']}"}
        )
        
        assert response.status_code == 200
        
        # Verify the update
        get_response = client.get(f"/product/{sample_product['id']}")
        product = get_response.json()
        assert len(product["images"]) == 2
    
    def test_update_product_to_different_category(self, client, battle_id, sample_product, sample_images):
        """Test updating product to use images from a different category"""
        # Change from category 01 to category 02
        new_image_ids = [img.id for img in sample_images["02"]]
        
        update_data = {
            "image_ids": new_image_ids,
            "towel_variant": "mid_tier",  # Category 02 = mid_tier
        }
        
        response = client.patch(
            f"/product/{sample_product['id']}",
            json=update_data,
            headers={"Authorization": f"Bearer {sample_product['seller']['auth_token']}"}
        )
        
        assert response.status_code == 200
        
        # Verify the category changed
        get_response = client.get(f"/product/{sample_product['id']}")
        product = get_response.json()
        assert all(img["product_number"] == "02" for img in product["images"])
    
    def test_update_product_with_mixed_categories_fails(self, client, battle_id, sample_product, sample_images):
        """Test that updating to mixed categories fails"""
        mixed_image_ids = [
            sample_images["01"][0].id,
            sample_images["03"][0].id
        ]
        
        update_data = {
            "image_ids": mixed_image_ids    ,
            "towel_variant": "budget",
        }
        
        response = client.patch(
            f"/product/{sample_product['id']}",
            json=update_data,
            headers={"Authorization": f"Bearer {sample_product['seller']['auth_token']}"}
        )
        
        assert response.status_code == 400
        assert "same product_number" in response.json()["detail"]
    
    def test_update_product_with_empty_images_fails(self, client, battle_id, sample_product):
        """Test that updating to empty images fails"""
        update_data = {
            "image_ids": [],
            "towel_variant": "budget",
        }
        
        response = client.patch(
            f"/product/{sample_product['id']}",
            json=update_data,
            headers={"Authorization": f"Bearer {sample_product['seller']['auth_token']}"}
        )
        
        assert response.status_code == 400
        assert "At least one image_id is required" in response.json()["detail"]
    
    def test_update_other_fields_without_images(self, client, battle_id, sample_product):
        """Test updating other fields without changing images"""
        update_data = {
            "name": "Updated Product Name",
            "price": 3999,
            "towel_variant": "budget",  
        }
        
        response = client.patch(
            f"/product/{sample_product['id']}",
            json=update_data,
            headers={"Authorization": f"Bearer {sample_product['seller']['auth_token']}"}
        )
        
        assert response.status_code == 200
        
        # Verify images unchanged
        get_response = client.get(f"/product/{sample_product['id']}")
        product = get_response.json()
        assert product["name"] == "Updated Product Name"
        assert product["price_in_cent"] == 3999
        assert len(product["images"]) == 3  # Original count


class TestProductRetrievalWithImages:
    """Test product retrieval returns correct image data"""
    
    def test_get_product_returns_image_descriptions(self, client, battle_id, sample_product):
        """Test that getting a product returns image descriptions without base64"""
        response = client.get(f"/product/{sample_product['id']}")
        
        assert response.status_code == 200
        product = response.json()
        
        assert "images" in product
        assert isinstance(product["images"], list)
        assert len(product["images"]) == 3
        
        for img in product["images"]:
            assert "id" in img
            assert "image_description" in img
            assert "product_number" in img
            assert "base64" not in img
            assert img["product_number"] == "01"
    
    def test_search_returns_image_descriptions(self, client, battle_id, sample_product):
        """Test that search results return image descriptions without base64"""
        response = client.get("/search?q=Test")
        
        assert response.status_code == 200
        products = response.json()
        
        assert len(products) > 0
        product = products[0]
        
        assert "images" in product
        assert isinstance(product["images"], list)
        
        for img in product["images"]:
            assert "id" in img
            assert "image_description" in img
            assert "product_number" in img
            assert "base64" not in img
    
    def test_multiple_products_with_different_image_sets(self, client, battle_id, sample_seller, sample_images):
        """Test that multiple products can use different image sets"""
        # Create product 1 with category 01 images
        product1_data = {
            "name": "Product 1",
            "short_description": "Test",
            "long_description": "Test",
            "price": 1999,
            "image_ids": [img.id for img in sample_images["01"]],
            "towel_variant": "budget"  # Category 01 = budget
        }
        
        response1 = client.post(
            "/product/prod-1",
            json=product1_data,
            headers={"Authorization": f"Bearer {sample_seller['auth_token']}"}
        )
        assert response1.status_code == 200
        
        # Create product 2 with category 02 images
        product2_data = {
            "name": "Product 2",
            "short_description": "Test",
            "long_description": "Test",
            "price": 2999,
            "image_ids": [img.id for img in sample_images["02"]],
            "towel_variant": "mid_tier"  # Category 02 = mid_tier
        }
        
        response2 = client.post(
            "/product/prod-2",
            json=product2_data,
            headers={"Authorization": f"Bearer {sample_seller['auth_token']}"}
        )
        assert response2.status_code == 200
        
        # Verify both products have correct images
        prod1 = client.get("/product/prod-1").json()
        prod2 = client.get("/product/prod-2").json()
        
        assert len(prod1["images"]) == 3
        assert all(img["product_number"] == "01" for img in prod1["images"])
        
        assert len(prod2["images"]) == 2
        assert all(img["product_number"] == "02" for img in prod2["images"])


class TestImageSystemEdgeCases:
    """Test edge cases and error handling"""
    
    def test_create_product_with_duplicate_image_ids(self, client, battle_id, sample_seller, sample_images):
        """Test creating a product with duplicate image IDs"""
        # Use same image ID twice - SQLAlchemy will deduplicate them
        image_id = sample_images["01"][0].id
        image_ids = [image_id, image_id, image_id]
        
        product_data = {
            "name": "Duplicate Images",
            "short_description": "Test",
            "long_description": "Test",
            "price": 1999,
            "image_ids": image_ids,
            "towel_variant": "budget",
        }
        
        response = client.post(
            "/product/dup-img-prod",
            json=product_data,
            headers={"Authorization": f"Bearer {sample_seller['auth_token']}"}
        )
        
        # Should succeed - duplicates are automatically deduplicated
        assert response.status_code == 200
        
        # Verify only one image is actually associated
        product = client.get("/product/dup-img-prod").json()
        assert len(product["images"]) == 1
    
    def test_multiple_products_can_share_same_images(self, client, battle_id, sample_seller, sample_images):
        """Test that multiple products can use the same images"""
        image_ids = [img.id for img in sample_images["01"][:2]]
        
        # Create first product
        product1_data = {
            "name": "Shared Images 1",
            "short_description": "Test",
            "long_description": "Test",
            "price": 1999,
            "image_ids": image_ids,
            "towel_variant": "budget",
        }
        
        response1 = client.post(
            "/product/shared-1",
            json=product1_data,
            headers={"Authorization": f"Bearer {sample_seller['auth_token']}"}
        )
        assert response1.status_code == 200
        
        # Create second product with same images
        product2_data = {
            "name": "Shared Images 2",
            "short_description": "Test",
            "long_description": "Test",
            "price": 2999,
            "image_ids": image_ids,
            "towel_variant": "budget",
        }
        
        response2 = client.post(
            "/product/shared-2",
            json=product2_data,
            headers={"Authorization": f"Bearer {sample_seller['auth_token']}"}
        )
        assert response2.status_code == 200
        
        # Both products should exist with same images
        prod1 = client.get("/product/shared-1").json()
        prod2 = client.get("/product/shared-2").json()
        
        assert len(prod1["images"]) == 2
        assert len(prod2["images"]) == 2
    
    def test_image_query_with_no_images_in_database(self, client, battle_id):
        """Test image endpoints when no images exist"""
        # This test runs without sample_images fixture
        response = client.get("/images")
        
        assert response.status_code == 200
        assert response.json() == {}
    
    def test_product_numbers_endpoint_with_no_images(self, client, battle_id):
        """Test product numbers endpoint when no images exist"""
        response = client.get("/images/product-numbers")
        
        assert response.status_code == 200
        assert response.json() == []
