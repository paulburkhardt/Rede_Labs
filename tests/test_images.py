"""Comprehensive tests for the new image system"""
import pytest


class TestImageQueryEndpoints:
    """Test image query endpoints"""

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


class TestProductCreationWithImages:
    """Test product creation with the new image system"""

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
    


class TestImageSystemEdgeCases:
    """Test edge cases and error handling"""
    pass
