"""
AgentBeats Tools for Seller Agents

These tools allow seller agents to interact with the marketplace API.
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

# No longer need mock base64 images - we use image IDs from the database


# Initialize battle context from database metadata
# This allows seller agents to retrieve battle context stored by the green agent
_seller_counter = 0
_battle_context_initialized = False

def _get_battle_context_from_db():
    """Retrieve battle context from database metadata and initialize if found."""
    global _seller_counter, _battle_context_initialized
    
    # Only initialize once per agent process
    if _battle_context_initialized:
        return True
    
    try:
        # Retrieve battle metadata from the API
        response = requests.get(f"{API_URL}/admin/metadata")
        if response.status_code == 200:
            metadata = response.json()
            battle_id = metadata.get("battle_id")
            backend_url = metadata.get("backend_url")
            
            if battle_id and backend_url:
                _seller_counter += 1
                agent_name = f"seller{_seller_counter}"
                context = BattleContext(
                    battle_id=battle_id,
                    backend_url=backend_url,
                    agent_name=agent_name
                )
                battle_logger.set_battle_context(context)
                _battle_context_initialized = True
                print(f"✅ Seller agent '{agent_name}': Battle context initialized from database")
                print(f"   battle_id={battle_id}, backend_url={backend_url}")
                return True
            else:
                print(f"⚠️  Seller agent: Metadata retrieved but missing values - battle_id={battle_id}, backend_url={backend_url}")
        else:
            print(f"⚠️  Seller agent: Failed to retrieve metadata - Status {response.status_code}")
    except Exception as e:
        print(f"⚠️  Seller agent: Exception retrieving battle context: {e}")
    
    return False

# Try to initialize on module load
_get_battle_context_from_db()


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
    image_ids: list[str],
    towel_variant: str
):
    """
    Create a new product in the marketplace.
    
    IMPORTANT: 
    - Products MUST have at least one image. The image_ids parameter is REQUIRED.
    - Products MUST specify a towel_variant. The towel_variant parameter is REQUIRED.
    
    TOWEL VARIANTS AVAILABLE (REQUIRED - choose one):
    - "budget": 500 GSM, 27x54 inches, Standard Cotton, $8.00 wholesale cost
    - "mid_tier": 550 GSM, 27x54 inches, Premium Cotton, $12.00 wholesale cost
    - "premium": 600 GSM, 27x59 inches, Premium Cotton, $15.00 wholesale cost
    
    IMAGE CATEGORY VALIDATION (CRITICAL):
    - Images MUST match the towel_variant category:
      * Budget variant ("budget") → MUST use images from category "01"
      * Mid-tier variant ("mid_tier") → MUST use images from category "02"
      * Premium variant ("premium") → MUST use images from category "03"
    - The API will reject your request if images don't match the variant category.
    - Use get_images_by_product_number() to get images for the correct category.
    
    When you specify a towel_variant, the system automatically sets the GSM, dimensions, and material.
    The product details endpoint will return these specifications (GSM, dimensions, material) but NOT the wholesale cost.
    
    Args:
        auth_token: Seller's authentication token
        product_id: Unique identifier for the product
        name: Product name
        short_description: Brief product description
        long_description: Detailed product description
        price: Price in cents (e.g., 2999 for $29.99)
        image_ids: List of image IDs from the database (REQUIRED - at least one image, must match towel_variant: budget='01', mid_tier='02', premium='03')
        towel_variant: REQUIRED towel variant ("budget", "mid_tier", or "premium"). Automatically sets GSM, dimensions, material, and wholesale cost. Images must match this category.
    
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
        ...     image_ids=["img-1", "img-2"],  # REQUIRED: Must provide at least one image
        ...     towel_variant="premium"  # REQUIRED: Must specify towel variant
        ... )
    """
    # Lazy initialization - try to get battle context if not already initialized
    _get_battle_context_from_db()
    
    log_tool_request("create_product", product_id=product_id, name=name, price=price, 
                     towel_variant=towel_variant, image_count=len(image_ids), auth_token=auth_token)
    
    payload = {
        "name": name,
        "short_description": short_description,
        "long_description": long_description,
        "price": price,
        "image_ids": image_ids,
        "towel_variant": towel_variant
    }
    
    response = requests.post(
        f"{API_URL}/product/{product_id}",
        json=payload,
        headers=get_auth_header(auth_token)
    )
    
    if response.status_code == 200:
        log_tool_response("create_product", True, f"Created '{name}' at ${price/100:.2f} ({towel_variant})")
        return {
            "success": True,
            "product_id": product_id,
            "message": "Product created successfully",
            "data": response.json()
        }
    else:
        log_tool_response("create_product", False, f"Error: {response.status_code}")
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
    image_ids: Optional[list[str]] = None,
    towel_variant: Optional[str] = None
):
    """
    Update an existing product.
    
    NOTE: If updating image_ids, you must provide at least one image. Products cannot have zero images.
    
    TOWEL VARIANTS AVAILABLE:
    - "budget": 500 GSM, 27x54 inches, Standard Cotton, $8.00 wholesale cost
    - "mid_tier": 550 GSM, 27x54 inches, Premium Cotton, $12.00 wholesale cost
    - "premium": 600 GSM, 27x59 inches, Premium Cotton, $15.00 wholesale cost
    
    IMAGE CATEGORY VALIDATION (CRITICAL):
    - When updating images, they MUST match the product's towel_variant:
      * Budget variant → images from category "01"
      * Mid-tier variant → images from category "02"
      * Premium variant → images from category "03"
    - When changing towel_variant, existing images must match the new variant OR you must also update images.
    - The API will reject mismatched combinations.
    
    Args:
        auth_token: Seller's authentication token
        product_id: ID of the product to update
        name: New product name (optional)
        short_description: New brief description (optional)
        long_description: New detailed description (optional)
        price: New price in cents (optional)
        image_ids: New list of image IDs (if provided, must include at least one image matching the towel_variant category, optional)
        towel_variant: Optional towel variant ("budget", "mid_tier", or "premium"). When specified, automatically updates GSM, dimensions, material, and wholesale cost. If changing variant, images must match new category.
    
    Returns:
        dict: Response from the API containing update status
    
    Example:
        >>> update_product(
        ...     auth_token="abc123",
        ...     product_id="towel-001",
        ...     price=2499,  # Reduce price to $24.99
        ...     image_ids=["img-3", "img-4"],  # Change images (must have at least one)
        ...     towel_variant="mid_tier"  # Optional: Change to mid-tier variant
        ... )
    """
    # Build update summary for logging
    updates = []
    if name is not None:
        updates.append(f"name='{name}'")
    if price is not None:
        updates.append(f"price=${price/100:.2f}")
    if towel_variant is not None:
        updates.append(f"variant={towel_variant}")
    if image_ids is not None:
        updates.append(f"images={len(image_ids)}")
    
    log_tool_request("update_product", product_id=product_id, updates=", ".join(updates), auth_token=auth_token)
    
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
    if towel_variant is not None:
        payload["towel_variant"] = towel_variant
    
    response = requests.patch(
        f"{API_URL}/product/{product_id}",
        json=payload,
        headers=get_auth_header(auth_token)
    )
    
    if response.status_code == 200:
        log_tool_response("update_product", True, f"Updated {product_id}: {', '.join(updates)}")
        return {
            "success": True,
            "product_id": product_id,
            "message": "Product updated successfully",
            "data": response.json()
        }
    else:
        log_tool_response("update_product", False, f"Error: {response.status_code}")
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
    log_tool_request("get_sales_stats", auth_token=auth_token)
    
    response = requests.get(
        f"{API_URL}/getSalesStats",
        headers=get_auth_header(auth_token)
    )
    
    if response.status_code == 200:
        data = response.json()
        total_sales = data.get("total_sales", 0)
        total_revenue = data.get("total_revenue_cents", 0) / 100
        log_tool_response("get_sales_stats", True, f"{total_sales} sales, ${total_revenue:.2f} revenue")
        return {
            "success": True,
            "data": data
        }
    else:
        log_tool_response("get_sales_stats", False, f"Error: {response.status_code}")
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
    
    IMPORTANT: 
    - You must select at least one image when creating a product. Products cannot be created without images.
    - Images are organized by category code:
      * "01" = Budget category (use with towel_variant="budget")
      * "02" = Mid-tier category (use with towel_variant="mid_tier")
      * "03" = Premium category (use with towel_variant="premium")
    - Always match image category to your towel_variant or the API will reject your request.
    
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
    
    Use this to select images for your product. Remember: 
    - Products MUST have at least one image.
    - Image category MUST match towel_variant: "01"=budget, "02"=mid_tier, "03"=premium.
    
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
