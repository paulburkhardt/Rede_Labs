"""
Seller Agent Utilities

Provides API wrapper functions for interacting with the marketplace API.
"""

import requests
from typing import Dict, List, Optional
from datetime import datetime


class MarketplaceAPI:
    """Utility class for marketplace API calls"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize the marketplace API wrapper.
        
        Args:
            base_url: Base URL of the marketplace API
        """
        self.base_url = base_url
        self.auth_token: Optional[str] = None
        self.seller_id: Optional[str] = None
        self.product_ids: List[str] = []
    
    def _get_headers(self) -> Dict[str, str]:
        """Get authentication headers"""
        if not self.auth_token:
            raise ValueError("Not authenticated. Call register_seller() first.")
        return {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
    
    def register_seller(self) -> Dict:
        """
        Register as a seller and get auth token.
        
        Returns:
            Dict with 'id' and 'auth_token'
        """
        response = requests.post(f"{self.base_url}/createSeller")
        response.raise_for_status()
        
        data = response.json()
        self.seller_id = data["id"]
        self.auth_token = data["auth_token"]
        
        return data
    
    def create_product(self, product_id: str, product_data: Dict) -> Dict:
        """
        Create a product listing.
        
        Args:
            product_id: Unique product identifier
            product_data: Product information (name, descriptions, price, image)
            
        Returns:
            Response from the API
        """
        response = requests.post(
            f"{self.base_url}/product/{product_id}",
            json=product_data,
            headers=self._get_headers()
        )
        response.raise_for_status()
        
        self.product_ids.append(product_id)
        return response.json()
    
    def update_product(self, product_id: str, updates: Dict) -> Dict:
        """
        Update an existing product.
        
        Args:
            product_id: Product ID to update
            updates: Dictionary of fields to update
            
        Returns:
            Response from the API
        """
        response = requests.patch(
            f"{self.base_url}/product/{product_id}",
            json=updates,
            headers=self._get_headers()
        )
        response.raise_for_status()
        
        return response.json()
    
    def get_product_details(self, product_id: str) -> Dict:
        """
        Get detailed information about a product.
        
        Args:
            product_id: Product ID
            
        Returns:
            Product details
        """
        response = requests.get(f"{self.base_url}/product/{product_id}")
        response.raise_for_status()
        
        return response.json()
    
    def get_sales_stats(self) -> Dict:
        """
        Get sales statistics for this seller.
        
        Returns:
            Dict with sales stats including purchases, revenue, etc.
        """
        response = requests.get(
            f"{self.base_url}/getSalesStats",
            headers=self._get_headers()
        )
        response.raise_for_status()
        
        return response.json()
    
    def search_products(self, query: str = "") -> List[Dict]:
        """
        Search marketplace products (for competitor analysis).
        
        Args:
            query: Search query (empty string returns all products)
            
        Returns:
            List of product search results
        """
        response = requests.get(
            f"{self.base_url}/search",
            params={"q": query}
        )
        response.raise_for_status()
        
        return response.json()
    
    def get_market_intelligence(self) -> Dict:
        """
        Analyze the market to get competitive intelligence.
        
        Returns:
            Dict with market analysis (avg price, competitor count, etc.)
        """
        all_products = self.search_products("")
        
        if not all_products:
            return {
                "total_products": 0,
                "avg_price_cents": 0,
                "min_price_cents": 0,
                "max_price_cents": 0,
                "competitor_count": 0,
                "competitor_prices": []
            }
        
        # Filter out our own products for competitor analysis
        competitor_products = [
            p for p in all_products 
            if p.get("seller_id") != self.seller_id
        ]
        
        prices = [p["price_in_cent"] for p in all_products]
        competitor_prices = [p["price_in_cent"] for p in competitor_products]
        
        return {
            "total_products": len(all_products),
            "avg_price_cents": sum(prices) // len(prices) if prices else 0,
            "min_price_cents": min(prices) if prices else 0,
            "max_price_cents": max(prices) if prices else 0,
            "competitor_count": len(competitor_products),
            "competitor_prices": competitor_prices,
            "my_products": [p for p in all_products if p.get("seller_id") == self.seller_id],
            "competitor_products": competitor_products
        }


def generate_product_id(seller_name: str, product_type: str = "towel") -> str:
    """
    Generate a unique product ID.
    
    Args:
        seller_name: Name of the seller
        product_type: Type of product
        
    Returns:
        Unique product ID
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{seller_name.lower().replace(' ', '_')}_{product_type}_{timestamp}"

