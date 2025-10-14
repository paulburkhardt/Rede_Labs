# -*- coding: utf-8 -*-
"""
Shared tools for all customer agents
"""

import agentbeats as ab
import requests

MARKETPLACE_URL = "http://localhost:8100"


@ab.tool
def browse_products(query: str = "towel") -> str:
    """Search for products on marketplace"""
    try:
        response = requests.get(f"{MARKETPLACE_URL}/search", params={"q": query})
        response.raise_for_status()
        products = response.json()
        
        if not products:
            return "No products found."
        
        result = f"Found {len(products)} products:\n\n"
        for i, product in enumerate(products, 1):
            price = product['priceInCent'] / 100
            bestseller = " ⭐ BESTSELLER" if product['bestseller'] else ""
            result += f"{i}. {product['name']}{bestseller}\n"
            result += f"   Price: ${price:.2f}\n"
            result += f"   Seller: {product['company']['name']}\n"
            result += f"   Description: {product['shortDescription']}\n"
            result += f"   Product ID: {product['id']}\n\n"
        
        return result
    except Exception as e:
        return f"Error browsing: {str(e)}"


@ab.tool
def view_product(product_id: str) -> str:
    """Get detailed product information"""
    try:
        response = requests.get(f"{MARKETPLACE_URL}/product/{product_id}")
        response.raise_for_status()
        product = response.json()
        
        price = product['priceInCent'] / 100
        bestseller = " ⭐ BESTSELLER" if product['bestseller'] else ""
        
        result = f"Product Details:\n\n"
        result += f"Name: {product['name']}{bestseller}\n"
        result += f"Price: ${price:.2f}\n"
        result += f"Seller: {product['company']['name']}\n"
        result += f"Short: {product['shortDescription']}\n\n"
        result += f"Full Description:\n{product['longDescription']}\n"
        
        return result
    except Exception as e:
        return f"Error viewing product: {str(e)}"


@ab.tool
def purchase_product(product_id: str) -> str:
    """Purchase a product"""
    try:
        response = requests.post(f"{MARKETPLACE_URL}/buy/{product_id}")
        response.raise_for_status()
        result = response.json()
        
        price = result.get('price', 0) / 100
        return f"✅ Purchase successful! Paid ${price:.2f}"
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            return "❌ Not in buy phase. Wait for green agent signal."
        return f"❌ Purchase failed: {str(e)}"
    except Exception as e:
        return f"❌ Error: {str(e)}"
