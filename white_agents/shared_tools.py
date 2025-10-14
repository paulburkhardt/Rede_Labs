# -*- coding: utf-8 -*-
"""
Shared tools for white (seller) agents
"""

import agentbeats as ab
import requests

MARKETPLACE_URL = "http://localhost:8100"


@ab.tool
def create_organization(name: str) -> str:
    """Register as seller organization"""
    try:
        response = requests.post(
            f"{MARKETPLACE_URL}/createOrganization",
            json={"name": name}
        )
        response.raise_for_status()
        result = response.json()
        return f"Organization created: {result['id']} - {result['name']}"
    except Exception as e:
        return f"Error creating organization: {str(e)}"


@ab.tool
def create_product(name: str, short_desc: str, long_desc: str, price: int, image_url: str) -> str:
    """Create product listing (price in cents)"""
    try:
        response = requests.post(
            f"{MARKETPLACE_URL}/product",
            json={
                "name": name,
                "shortDescription": short_desc,
                "longDescription": long_desc,
                "price": price,
                "image": {"url": image_url}
            }
        )
        response.raise_for_status()
        result = response.json()
        return f"Product created: {result['id']}"
    except Exception as e:
        return f"Error creating product: {str(e)}"


@ab.tool
def update_product(product_id: str, name: str = None, short_desc: str = None, 
                  long_desc: str = None, price: int = None, image_url: str = None) -> str:
    """Update product listing"""
    updates = {}
    if name: updates["name"] = name
    if short_desc: updates["shortDescription"] = short_desc
    if long_desc: updates["longDescription"] = long_desc
    if price: updates["price"] = price
    if image_url: updates["image"] = {"url": image_url}
    
    try:
        response = requests.patch(
            f"{MARKETPLACE_URL}/product/{product_id}",
            json=updates
        )
        response.raise_for_status()
        return f"Product {product_id} updated successfully"
    except Exception as e:
        return f"Error updating product: {str(e)}"


@ab.tool
def browse_competitors(category: str = "towel") -> str:
    """See what competitors are selling"""
    try:
        response = requests.get(f"{MARKETPLACE_URL}/search", params={"q": category})
        response.raise_for_status()
        products = response.json()
        
        result = f"Found {len(products)} competitor products:\n\n"
        for i, product in enumerate(products, 1):
            price = product['priceInCent'] / 100
            result += f"{i}. {product['name']} - ${price:.2f}\n"
            result += f"   Seller: {product['company']['name']}\n"
            result += f"   Rank: #{i}\n\n"
        
        return result
    except Exception as e:
        return f"Error browsing competitors: {str(e)}"
