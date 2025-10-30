"""
AgentBeats Tools for Buyer Agents

These tools allow buyer agents to interact with the marketplace API.
"""

import os
import requests
import agentbeats as ab
from typing import Optional

# API configuration
API_URL = os.getenv("MARKETPLACE_API_URL", "http://localhost:8000")


def get_auth_header(auth_token: str) -> dict:
    """Helper to create authorization header"""
    return {"Authorization": f"Bearer {auth_token}"}


@ab.tool
def search_products(query: str = "", auth_token: Optional[str] = None):
    """
    Search for products in the marketplace.
    
    Args:
        query: Search query string (empty string returns all products)
        auth_token: Optional buyer authentication token
    
    Returns:
        dict: List of matching products with details
    
    Example:
        >>> search_products("towel")
        >>> search_products("")  # Get all products
    """
    headers = get_auth_header(auth_token) if auth_token else {}
    response = requests.get(f"{API_URL}/search?q={query}", headers=headers)
    
    if response.status_code == 200:
        products = response.json()
        return {
            "success": True,
            "count": len(products),
            "products": products
        }
    else:
        return {
            "success": False,
            "error": response.text,
            "status_code": response.status_code
        }


@ab.tool
def get_product_details(product_id: str, auth_token: Optional[str] = None):
    """
    Get detailed information about a specific product.
    
    Args:
        product_id: ID of the product to retrieve
        auth_token: Optional buyer authentication token
    
    Returns:
        dict: Product details including name, description, price, seller info, image, etc.
    
    Example:
        >>> get_product_details("towel-001")
    """
    headers = get_auth_header(auth_token) if auth_token else {}
    response = requests.get(f"{API_URL}/product/{product_id}", headers=headers)
    
    if response.status_code == 200:
        return {
            "success": True,
            "product": response.json()
        }
    else:
        return {
            "success": False,
            "error": response.text,
            "status_code": response.status_code
        }


@ab.tool
def purchase_product(
    auth_token: str,
    product_id: str,
    purchased_at: Optional[int] = None
):
    """
    Purchase a product from the marketplace.
    
    Args:
        auth_token: Buyer's authentication token
        product_id: ID of the product to purchase
        purchased_at: Optional timestamp (defaults to current time if not provided)
    
    Returns:
        dict: Purchase confirmation with details
    
    Example:
        >>> purchase_product(
        ...     auth_token="xyz789",
        ...     product_id="towel-001"
        ... )
    """
    payload = {}
    if purchased_at is not None:
        payload["purchased_at"] = purchased_at
    else:
        import time
        payload["purchased_at"] = int(time.time())
    
    response = requests.post(
        f"{API_URL}/buy/{product_id}",
        json=payload,
        headers=get_auth_header(auth_token)
    )
    
    if response.status_code == 200:
        return {
            "success": True,
            "product_id": product_id,
            "message": "Product purchased successfully",
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
def compare_products(product_ids: list[str], auth_token: Optional[str] = None):
    """
    Compare multiple products side by side.
    
    Args:
        product_ids: List of product IDs to compare
        auth_token: Optional buyer authentication token
    
    Returns:
        dict: Comparison data for all requested products
    
    Example:
        >>> compare_products(["towel-001", "towel-002", "soap-001"])
    """
    products = []
    errors = []
    
    for product_id in product_ids:
        result = get_product_details(product_id, auth_token)
        if result["success"]:
            products.append(result["product"])
        else:
            errors.append({
                "product_id": product_id,
                "error": result.get("error", "Unknown error")
            })
    
    return {
        "success": len(products) > 0,
        "products": products,
        "errors": errors if errors else None,
        "comparison": {
            "count": len(products),
            "price_range": {
                "min": min(p["price_in_cent"] for p in products) if products else 0,
                "max": max(p["price_in_cent"] for p in products) if products else 0,
            } if products else None
        }
    }


# Export all tools
__all__ = [
    "search_products",
    "get_product_details",
    "purchase_product",
    "compare_products",
]
