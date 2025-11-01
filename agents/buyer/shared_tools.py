"""
AgentBeats Tools for Buyer Agents

These tools allow buyer agents to interact with the marketplace API.
"""

import os
import sys
from pathlib import Path

# Add agents directory to sys.path to enable shared battle_logger import
agents_dir = Path(__file__).parent.parent
if str(agents_dir) not in sys.path:
    sys.path.insert(0, str(agents_dir))

import requests
import agentbeats as ab
from typing import Optional

# Import battle logger - this will be cached by Python's import system
# ensuring all modules share the same instance
import battle_logger
from agentbeats.logging import BattleContext
log_tool_request = battle_logger.log_tool_request
log_tool_response = battle_logger.log_tool_response

# API configuration
API_URL = os.getenv("MARKETPLACE_API_URL", "http://localhost:8000")


# Initialize battle context from database metadata
# This allows buyer agents to retrieve battle context stored by the green agent
_buyer_counter = 0
_last_battle_id = None

def _get_battle_context_from_db():
    """Retrieve battle context from database metadata and update if battle_id changed."""
    global _buyer_counter, _last_battle_id
    
    try:
        # Retrieve battle metadata from the API
        response = requests.get(f"{API_URL}/admin/metadata")
        if response.status_code == 200:
            metadata = response.json()
            battle_id = metadata.get("battle_id")
            backend_url = metadata.get("backend_url")
            
            if battle_id and backend_url:
                # Check if this is a new battle
                if battle_id != _last_battle_id:
                    _buyer_counter += 1
                    agent_name = f"buyer{_buyer_counter}"
                    context = BattleContext(
                        battle_id=battle_id,
                        backend_url=backend_url,
                        agent_name=agent_name
                    )
                    battle_logger.set_battle_context(context)
                    _last_battle_id = battle_id
                    print(f"✅ Buyer agent '{agent_name}': Battle context initialized from database")
                    print(f"   battle_id={battle_id}, backend_url={backend_url}")
                return True
            else:
                print(f"⚠️  Buyer agent: Metadata retrieved but missing values - battle_id={battle_id}, backend_url={backend_url}")
        else:
            print(f"⚠️  Buyer agent: Failed to retrieve metadata - Status {response.status_code}")
    except Exception as e:
        print(f"⚠️  Buyer agent: Exception retrieving battle context: {e}")
    
    return False

# Try to initialize on module load
_get_battle_context_from_db()


def get_auth_header(auth_token: str) -> dict:
    """Helper to create authorization header"""
    return {"Authorization": f"Bearer {auth_token}"}


@ab.tool
def search_products(query: str = "", auth_token: Optional[str] = None):
    """
    Search for products in the marketplace.
    
    Args:
        query: Optional search query to filter products
        auth_token: Authentication token for the buyer
        
    Returns:
        List of products matching the search criteria
    """
    # Lazy initialization - try to get battle context if not already initialized
    _get_battle_context_from_db()
    
    log_tool_request("search_products", query=query, auth_token=auth_token)
    
    headers = get_auth_header(auth_token) if auth_token else {}
    response = requests.get(f"{API_URL}/search?q={query}", headers=headers)

    
    if response.status_code == 200:
        products = response.json()
        log_tool_response("search_products", True, f"Found {len(products)} products")
        return {
            "success": True,
            "count": len(products),
            "products": products
        }
    else:
        log_tool_response("search_products", False, f"Error: {response.status_code}")
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
    log_tool_request("get_product_details", product_id=product_id, auth_token=auth_token)
    
    headers = get_auth_header(auth_token) if auth_token else {}
    response = requests.get(f"{API_URL}/product/{product_id}", headers=headers)
    
    if response.status_code == 200:
        product = response.json()
        log_tool_response("get_product_details", True, f"Retrieved {product.get('name', product_id)}")
        return {
            "success": True,
            "product": product
        }
    else:
        log_tool_response("get_product_details", False, f"Error: {response.status_code}")
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
    log_tool_request("purchase_product", product_id=product_id, purchased_at=purchased_at, auth_token=auth_token)
    
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
        data = response.json()
        price = data.get("price_in_cent", 0) / 100
        log_tool_response("purchase_product", True, f"Purchased {product_id} for ${price:.2f}")
        return {
            "success": True,
            "product_id": product_id,
            "message": "Product purchased successfully",
            "data": data
        }
    else:
        log_tool_response("purchase_product", False, f"Error: {response.status_code}")
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
    log_tool_request("compare_products", product_ids=product_ids, auth_token=auth_token)
    
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
    
    if products:
        min_price = min(p["price_in_cent"] for p in products) / 100
        max_price = max(p["price_in_cent"] for p in products) / 100
        log_tool_response("compare_products", True, f"Compared {len(products)} products (${min_price:.2f}-${max_price:.2f})")
    else:
        log_tool_response("compare_products", False, "No products found")
    
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
