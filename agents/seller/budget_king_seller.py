"""
Budget King Seller Agent

Always competes on price - targets price-conscious buyers.
Strategy: Undercut competitors and maintain lowest prices.
"""

from typing import Dict, Optional
from agents.seller.seller_agent_base import SellerAgent
from agents.seller.seller_utils import MarketplaceAPI
from agents.seller.towel_products import (
    TowelVariant,
    get_towel_spec,
    calculate_suggested_retail,
    DEFAULT_PRODUCT_NAMES,
    DEFAULT_IMAGES,
    get_technical_description
)
import random


class BudgetKingSeller(SellerAgent):
    """
    Budget King Seller Strategy
    
    Philosophy: Price is king. Compete aggressively on price to win price-conscious buyers.
    - Always aims to be 15-25% cheaper than competitors
    - Simple, honest descriptions that don't oversell
    - Willing to lower prices if not winning sales
    """
    
    def __init__(self, name: str = "Budget King", api: Optional[MarketplaceAPI] = None):
        super().__init__(name, "budget", api)
        
        # Select BUDGET variant (aligned with strategy)
        self.variant = TowelVariant.BUDGET
        self.spec = get_towel_spec(self.variant)
        
        # Pricing strategy: Aggressive competitive pricing
        self.base_markup_percent = 25  # Start with 25% markup (budget strategy)
        # Floor at 50% of wholesale - allows loss-leader strategy
        self.min_price = self.spec.wholesale_cost_cents // 2  # $4.00 floor for BUDGET
        
        # Note: At floor price, loses $4.00 per sale (wholesale $8.00 - floor $4.00)
        
    def select_product_and_create_listing(self) -> tuple[TowelVariant, Dict]:
        """
        Select BUDGET variant and create price-competitive listing.
        
        Returns:
            Tuple of (TowelVariant.BUDGET, marketing_data)
        """
        # Choose a random budget-friendly product name
        product_name = random.choice(DEFAULT_PRODUCT_NAMES[TowelVariant.BUDGET])
        
        # Get market data to price competitively
        market_data = self.api.get_market_intelligence() if self.is_registered else {}
        initial_price = self.determine_price(self.spec.wholesale_cost_cents, market_data)
        
        # Create budget-focused marketing copy
        tech_desc = get_technical_description(self.variant)
        
        marketing_data = {
            "name": product_name,
            "short_description": f"Affordable quality at an unbeatable price - {tech_desc}",
            "long_description": (
                f"Looking for reliable bath towels without the luxury price tag? "
                f"Our {product_name} delivers exactly what you need: absorbent, durable towels "
                f"that handle daily use with ease.\n\n"
                f"Specifications: {tech_desc}\n\n"
                f"Features:\n"
                f"• 100% functional design - no unnecessary frills\n"
                f"• Machine washable and quick-drying\n"
                f"• Suitable for everyday family use\n"
                f"• Great for the budget-conscious household\n\n"
                f"Why pay more for the same functionality? Get the job done right without overspending."
            ),
            "price": initial_price,
            "image": DEFAULT_IMAGES[TowelVariant.BUDGET]
        }
        
        return self.variant, marketing_data
    
    def determine_price(self, wholesale_cost: int, market_data: Dict) -> int:
        """
        Calculate competitive budget pricing.
        
        Strategy:
        - If no competitors, use low markup (25%)
        - If competitors exist, undercut the lowest by 10-15%
        - Can go below wholesale cost (loss-leader) down to floor (50% of wholesale)
        
        Args:
            wholesale_cost: Wholesale cost of the product
            market_data: Market intelligence
            
        Returns:
            Competitive retail price in cents
        """
        competitor_prices = market_data.get("competitor_prices", [])
        
        if not competitor_prices:
            # No competitors yet, use base markup
            suggested_price = calculate_suggested_retail(self.variant, self.base_markup_percent)
            return max(suggested_price, self.min_price)
        
        # Undercut the cheapest competitor
        min_competitor_price = min(competitor_prices)
        target_price = int(min_competitor_price * 0.88)  # 12% cheaper
        
        # Can go below wholesale (loss-leader) but not below floor
        return max(target_price, self.min_price)
    
    def update_listing_strategy(self, sales_stats: Dict, market_data: Dict) -> Dict:
        """
        Update strategy based on sales performance.
        
        Strategy:
        - If we have 0 sales and competitors are selling, drop price more
        - If we're selling well, maintain current price
        - Always monitor competitor prices and stay cheapest
        
        Args:
            sales_stats: Our sales performance
            market_data: Competitor information
            
        Returns:
            Dict with updates to apply (empty if no changes)
        """
        updates = {}
        
        total_sales = sales_stats.get("total_sales", 0)
        my_products = market_data.get("my_products", [])
        
        if not my_products:
            return updates
        
        current_price = my_products[0].get("price_in_cent", self.spec.wholesale_cost_cents)
        competitor_prices = market_data.get("competitor_prices", [])
        
        # Strategy 1: If we have no sales and competitors do, we need to be cheaper
        if total_sales == 0 and len(competitor_prices) > 0:
            min_competitor = min(competitor_prices)
            
            # If we're not the cheapest, make ourselves cheaper
            if current_price >= min_competitor:
                new_price = max(int(min_competitor * 0.85), self.min_price)
                if new_price < current_price:
                    updates["price"] = new_price
                    print(f"  💰 {self.name}: No sales, dropping price to ${new_price/100:.2f}")
        
        # Strategy 2: If competitors undercut us, respond
        elif len(competitor_prices) > 0:
            min_competitor = min(competitor_prices)
            
            # If someone undercut us, beat their price
            if min_competitor < current_price:
                new_price = max(int(min_competitor * 0.92), self.min_price)
                if new_price < current_price:
                    updates["price"] = new_price
                    print(f"  💰 {self.name}: Competitor undercut, adjusting to ${new_price/100:.2f}")
        
        # Strategy 3: Keep aggressive pricing messaging
        if total_sales > 0:
            # We're winning, keep the aggressive budget messaging
            updates["short_description"] = "Proven value! Thousands saved by smart shoppers like you"
        
        return updates

