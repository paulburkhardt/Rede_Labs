"""
AgentBeats Tools for Seller Agents

These tools allow seller agents to interact with the marketplace API.
"""

import os
import requests
import agentbeats as ab
from typing import Optional

# API configuration
API_URL = os.getenv("MARKETPLACE_API_URL", "http://localhost:8000")

# No longer need mock base64 images - we use image IDs from the database


def get_auth_header(auth_token: str) -> dict:
    """Helper to create authorization header"""
    return {"Authorization": f"Bearer {auth_token}"}


@ab.tool
def create_product(
    auth_token: str,
    product_id: str,
    name: str,
    short_description: str,
    long_description: str,
    price: int,
    image_ids: list[str]
):
    """
    Create a new product in the marketplace.
    
    Args:
        auth_token: Seller's authentication token
        product_id: Unique identifier for the product
        name: Product name
        short_description: Brief product description
        long_description: Detailed product description
        price: Price in cents (e.g., 2999 for $29.99)
        image_ids: List of image IDs from the database (must be from same product_number)
    
    Returns:
        dict: Response from the API containing product creation status
    
    Example:
        >>> create_product(
        ...     auth_token="abc123",
        ...     product_id="towel-001",
        ...     name="Premium Cotton Towel",
        ...     short_description="Soft and absorbent",
        ...     long_description="Made from 100% Egyptian cotton",
        ...     price=2999,
        ...     image_ids=["img-1", "img-2"]
        ... )
    """
    payload = {
        "name": name,
        "short_description": short_description,
        "long_description": long_description,
        "price": price,
        "image_ids": image_ids
    }
    
    response = requests.post(
        f"{API_URL}/product/{product_id}",
        json=payload,
        headers=get_auth_header(auth_token)
    )
    
    if response.status_code == 200:
        return {
            "success": True,
            "product_id": product_id,
            "message": "Product created successfully",
            "data": response.json()
        }
    else:
        return {
            "success": False,
            "product_id": product_id,
            "error": response.text,
            "status_code": response.status_code
        }


@ab.tool
def update_product(
    auth_token: str,
    product_id: str,
    name: Optional[str] = None,
    short_description: Optional[str] = None,
    long_description: Optional[str] = None,
    price: Optional[int] = None,
    image_ids: Optional[list[str]] = None
):
    """
    Update an existing product.
    
    Args:
        auth_token: Seller's authentication token
        product_id: ID of the product to update
        name: New product name (optional)
        short_description: New brief description (optional)
        long_description: New detailed description (optional)
        price: New price in cents (optional)
        image_ids: New list of image IDs (must be from same product_number, optional)
    
    Returns:
        dict: Response from the API containing update status
    
    Example:
        >>> update_product(
        ...     auth_token="abc123",
        ...     product_id="towel-001",
        ...     price=2499,  # Reduce price to $24.99
        ...     image_ids=["img-3", "img-4"]  # Change images
        ... )
    """
    payload = {}
    
    if name is not None:
        payload["name"] = name
    if short_description is not None:
        payload["short_description"] = short_description
    if long_description is not None:
        payload["long_description"] = long_description
    if price is not None:
        payload["price"] = price
    if image_ids is not None:
        payload["image_ids"] = image_ids
    
    response = requests.patch(
        f"{API_URL}/product/{product_id}",
        json=payload,
        headers=get_auth_header(auth_token)
    )
    
    if response.status_code == 200:
        return {
            "success": True,
            "product_id": product_id,
            "message": "Product updated successfully",
            "data": response.json()
        }
    else:
        return {
            "success": False,
            "product_id": product_id,
            "error": response.text,
            "status_code": response.status_code
        }


@ab.tool
def get_sales_stats(auth_token: str):
    """
    Get sales statistics for the seller's products.
    
    Args:
        auth_token: Seller's authentication token
    
    Returns:
        dict: Sales statistics including total sales, revenue, and purchase details
    
    Example:
        >>> get_sales_stats(auth_token="abc123")
    """
    response = requests.get(
        f"{API_URL}/getSalesStats",
        headers=get_auth_header(auth_token)
    )
    
    if response.status_code == 200:
        return {
            "success": True,
            "data": response.json()
        }
    else:
        return {
            "success": False,
            "error": response.text,
            "status_code": response.status_code
        }


@ab.tool
def get_product_details(product_id: str):
    """
    Get detailed information about a specific product.
    
    Args:
        product_id: ID of the product to retrieve
    
    Returns:
        dict: Product details including name, description, price, seller info, etc.
    
    Example:
        >>> get_product_details("towel-001")
    """
    response = requests.get(f"{API_URL}/product/{product_id}")
    
    if response.status_code == 200:
        return {
            "success": True,
            "data": response.json()
        }
    else:
        return {
            "success": False,
            "error": response.text,
            "status_code": response.status_code
        }


@ab.tool
def get_available_images():
    """
    Get all available images grouped by product_number.
    Returns image descriptions (not base64) organized by category.
    
    Returns:
        dict: Images grouped by product_number
    
    Example:
        >>> get_available_images()
        {
            "01": [
                {"id": "img-1", "image_description": "Front view", "product_number": "01"},
                {"id": "img-2", "image_description": "Side view", "product_number": "01"}
            ],
            "02": [...]
        }
    """
    response = requests.get(f"{API_URL}/images")
    
    if response.status_code == 200:
        return {
            "success": True,
            "data": response.json()
        }
    else:
        return {
            "success": False,
            "error": response.text,
            "status_code": response.status_code
        }


@ab.tool
def get_images_by_product_number(product_number: str):
    """
    Get all images for a specific product_number category.
    
    Args:
        product_number: The product number category (e.g., "01", "02")
    
    Returns:
        dict: List of image descriptions for that product number
    
    Example:
        >>> get_images_by_product_number("01")
    """
    response = requests.get(f"{API_URL}/images/product-number/{product_number}")
    
    if response.status_code == 200:
        return {
            "success": True,
            "images": response.json()
        }
    else:
        return {
            "success": False,
            "error": response.text,
            "status_code": response.status_code
        }


@ab.tool
def get_available_product_numbers():
    """
    Get list of all available product_numbers (categories) that have images.
    
    Returns:
        dict: List of product numbers
    
    Example:
        >>> get_available_product_numbers()
        {"success": True, "product_numbers": ["01", "02", "03"]}
    """
    response = requests.get(f"{API_URL}/images/product-numbers")
    
    if response.status_code == 200:
        return {
            "success": True,
            "product_numbers": response.json()
        }
    else:
        return {
            "success": False,
            "error": response.text,
            "status_code": response.status_code
        }


@ab.tool
def search_products(query: str = ""):
    """
    Search for products in the marketplace.
    
    Args:
        query: Search query string (empty string returns all products)
    
    Returns:
        dict: List of matching products
    
    Example:
        >>> search_products("towel")
    """
    response = requests.get(f"{API_URL}/search?q={query}")
    
    if response.status_code == 200:
        return {
            "success": True,
            "data": response.json()
        }
    else:
        return {
            "success": False,
            "error": response.text,
            "status_code": response.status_code
        }


# Export all tools
__all__ = [
    "create_product",
    "update_product",
    "get_sales_stats",
    "get_product_details",
    "search_products",
    "get_available_images",
    "get_images_by_product_number",
    "get_available_product_numbers",
]
