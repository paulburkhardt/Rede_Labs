"""
Seller Agent Base Class

Abstract base class for all seller agent strategies.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from agents.seller.seller_utils import MarketplaceAPI, generate_product_id
from agents.seller.towel_products import (
    TowelVariant, 
    get_towel_spec,
    get_minimum_price,
    validate_price,
    get_technical_description
)


class SellerAgent(ABC):
    """Base class for all seller agents"""
    
    def __init__(self, name: str, strategy_type: str, api: Optional[MarketplaceAPI] = None):
        """
        Initialize a seller agent.
        
        Args:
            name: Display name for this seller
            strategy_type: Type of strategy ("budget", "premium", "dynamic")
            api: MarketplaceAPI instance (creates new one if not provided)
        """
        self.name = name
        self.strategy_type = strategy_type
        self.api = api or MarketplaceAPI()
        self.products: List[str] = []
        self.is_registered = False
        
    def register(self) -> Dict:
        """
        Register with the marketplace and get authentication.
        
        Returns:
            Registration data with id and auth_token
        """
        if self.is_registered:
            return {
                "id": self.api.seller_id,
                "auth_token": self.api.auth_token
            }
        
        registration_data = self.api.register_seller()
        self.is_registered = True
        
        print(f"✓ {self.name} registered with ID: {registration_data['id']}")
        return registration_data
    
    def create_listing(self) -> Dict:
        """
        Create the initial product listing.
        
        Returns:
            Response from product creation
        """
        if not self.is_registered:
            raise ValueError("Must register before creating listings")
        
        # Get variant selection and marketing from strategy
        variant, marketing_data = self.select_product_and_create_listing()
        
        # Get the technical specifications from environment
        spec = get_towel_spec(variant)
        
        # Validate price is above wholesale cost
        is_valid, error_msg = validate_price(variant, marketing_data['price'])
        if not is_valid:
            raise ValueError(f"Invalid price for {variant.value}: {error_msg}")
        
        # Build complete product data
        product_data = {
            "name": marketing_data['name'],
            "short_description": marketing_data['short_description'],
            "long_description": marketing_data['long_description'],
            "price": marketing_data['price'],
            "image": marketing_data['image']
        }
        
        # Generate unique product ID
        product_id = generate_product_id(self.name)
        
        # Create the product
        response = self.api.create_product(product_id, product_data)
        self.products.append(product_id)
        
        wholesale = spec.wholesale_cost_cents
        markup_pct = ((marketing_data['price'] - wholesale) / wholesale) * 100
        
        print(f"✓ {self.name} created {variant.value} towel: {product_data['name']}")
        print(f"  Price: ${product_data['price']/100:.2f} (Wholesale: ${wholesale/100:.2f}, Markup: {markup_pct:.0f}%)")
        return response
    
    def update_listing(self) -> Optional[Dict]:
        """
        Update existing product listing based on market conditions.
        
        Returns:
            Response from product update, or None if no update needed
        """
        if not self.products:
            print(f"⚠ {self.name} has no products to update")
            return None
        
        # Get market intelligence
        market_data = self.api.get_market_intelligence()
        
        # Get our sales stats
        try:
            sales_stats = self.api.get_sales_stats()
        except Exception as e:
            print(f"⚠ {self.name} couldn't get sales stats: {e}")
            sales_stats = {"total_sales": 0, "total_revenue_in_cent": 0, "purchases": []}
        
        # Determine updates based on strategy
        updates = self.update_listing_strategy(sales_stats, market_data)
        
        if not updates:
            print(f"• {self.name} decided no updates needed")
            return None
        
        # Apply updates to first product (main product)
        product_id = self.products[0]
        response = self.api.update_product(product_id, updates)
        
        # Log what was updated
        update_desc = []
        if "price" in updates:
            update_desc.append(f"price → ${updates['price']/100:.2f}")
        if "name" in updates:
            update_desc.append("name")
        if "short_description" in updates:
            update_desc.append("description")
        
        print(f"✓ {self.name} updated: {', '.join(update_desc)}")
        return response
    
    def get_performance_summary(self) -> Dict:
        """
        Get a summary of this seller's performance.
        
        Returns:
            Dict with performance metrics
        """
        try:
            sales_stats = self.api.get_sales_stats()
            market_data = self.api.get_market_intelligence()
            
            return {
                "seller_name": self.name,
                "strategy": self.strategy_type,
                "total_sales": sales_stats.get("total_sales", 0),
                "total_revenue_cents": sales_stats.get("total_revenue_in_cent", 0),
                "total_revenue_dollars": sales_stats.get("total_revenue_in_cent", 0) / 100,
                "products_created": len(self.products),
                "market_position": self._calculate_market_position(sales_stats, market_data)
            }
        except Exception as e:
            print(f"⚠ Error getting performance summary for {self.name}: {e}")
            return {
                "seller_name": self.name,
                "strategy": self.strategy_type,
                "error": str(e)
            }
    
    def _calculate_market_position(self, sales_stats: Dict, market_data: Dict) -> str:
        """Calculate relative market position"""
        my_revenue = sales_stats.get("total_revenue_in_cent", 0)
        my_sales = sales_stats.get("total_sales", 0)
        
        if my_sales == 0:
            return "No sales yet"
        elif my_revenue > market_data.get("avg_price_cents", 0) * my_sales:
            return "Above average"
        else:
            return "Below average"
    
    @abstractmethod
    def select_product_and_create_listing(self) -> tuple[TowelVariant, Dict]:
        """
        Select which towel variant to sell and create marketing copy.
        
        The seller must:
        1. Choose a TowelVariant (BUDGET, MID_TIER, or PREMIUM)
        2. Create marketing materials (name, descriptions)
        3. Set a retail price (must be >= wholesale cost)
        4. Choose product image
        
        Returns:
            Tuple of (TowelVariant, marketing_dict) where marketing_dict contains:
            - name: Product name (your marketing)
            - short_description: Short description (your marketing)
            - long_description: Long description (your marketing, should mention specs)
            - price: Retail price in cents (must be >= wholesale cost)
            - image: Dict with 'url' and 'alternative_text'
        """
        pass
    
    @abstractmethod
    def update_listing_strategy(self, sales_stats: Dict, market_data: Dict) -> Dict:
        """
        Decide how to update listing based on performance.
        
        Args:
            sales_stats: Sales statistics for this seller
            market_data: Market intelligence (competitor prices, etc.)
            
        Returns:
            Dict with fields to update (empty dict = no updates)
        """
        pass
    
    @abstractmethod
    def determine_price(self, base_price: int, market_data: Dict) -> int:
        """
        Calculate pricing strategy based on market conditions.
        
        Args:
            base_price: Base price for this product type
            market_data: Market intelligence
            
        Returns:
            Price in cents
        """
        pass

