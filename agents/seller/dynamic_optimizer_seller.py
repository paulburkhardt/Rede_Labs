"""
Dynamic Optimizer Seller Agent

Adaptive strategy that responds to market conditions and sales data.
Strategy: Analyze market, adjust pricing dynamically, optimize messaging based on performance.
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


class DynamicOptimizerSeller(SellerAgent):
    """
    Dynamic Optimizer Seller Strategy
    
    Philosophy: Adapt to market conditions and optimize based on data.
    - Starts at mid-market price point
    - Analyzes competitor pricing and adjusts dynamically
    - A/B tests messaging variations
    - Responds to sales velocity and market position
    - Targets all buyer segments with adaptive approach
    """
    
    def __init__(self, name: str = "Dynamic Optimizer", api: Optional[MarketplaceAPI] = None):
        super().__init__(name, "dynamic", api)
        
        # Select MID_TIER variant (balanced quality and price)
        self.variant = TowelVariant.MID_TIER
        self.spec = get_towel_spec(self.variant)
        
        # Pricing strategy: Adaptive mid-range pricing
        self.base_markup_percent = 75  # Start with 75% markup (balanced)
        self.max_markup_percent = 150  # Cap at 150% markup
        
        # Dynamic strategy: Can use loss-leader if needed
        # Floor at 50% of wholesale (allows aggressive loss-leader)
        self.min_price = self.spec.wholesale_cost_cents // 2  # $6.00 floor for MID_TIER
        
        # Preferred minimum to maintain some profit
        self.preferred_min_markup = 20  # Prefers 20% margin when possible
        self.preferred_min = int(self.spec.wholesale_cost_cents * (1 + self.preferred_min_markup / 100))
        
        # Tracking
        self.price_adjustment_history = []
        self.update_count = 0
        self.initial_price = None
        
    def select_product_and_create_listing(self) -> tuple[TowelVariant, Dict]:
        """
        Select MID_TIER variant and create adaptively positioned listing.
        
        Returns:
            Tuple of (TowelVariant.MID_TIER, marketing_data)
        """
        # Choose a random mid-tier product name
        product_name = random.choice(DEFAULT_PRODUCT_NAMES[TowelVariant.MID_TIER])
        
        # Get market data to position intelligently
        market_data = self.api.get_market_intelligence() if self.is_registered else {}
        initial_price = self.determine_price(self.spec.wholesale_cost_cents, market_data)
        self.initial_price = initial_price
        
        # Create balanced marketing copy
        tech_desc = get_technical_description(self.variant)
        
        marketing_data = {
            "name": product_name,
            "short_description": f"Premium quality meets smart pricing - {tech_desc}",
            "long_description": (
                f"Our {product_name} strikes the perfect balance between quality and value. "
                f"Designed with input from hospitality professionals, these towels deliver "
                f"professional-grade performance at a price that makes sense.\n\n"
                f"Specifications: {tech_desc}\n\n"
                f"Quality Features:\n"
                f"• Premium cotton for superior absorbency\n"
                f"• 600 GSM weight provides excellent plushness\n"
                f"• Reinforced edges for extended lifespan\n"
                f"• Quick-drying design saves energy\n"
                f"• Professional hospitality grade quality\n\n"
                f"Whether you're upgrading your bathroom or replacing worn-out towels, "
                f"this collection offers the reliability and comfort you need. "
                f"Not too basic, not overpriced - just smart, quality towels that perform."
            ),
            "price": initial_price,
            "image": DEFAULT_IMAGES[TowelVariant.MID_TIER]
        }
        
        return self.variant, marketing_data
    
    def determine_price(self, wholesale_cost: int, market_data: Dict) -> int:
        """
        Calculate adaptive pricing based on market analysis.
        
        Strategy:
        - Analyze market gaps and position strategically
        - If no competitors, use balanced markup (75%)
        - If competitors exist, find optimal position between budget and premium
        
        Args:
            wholesale_cost: Wholesale cost of the product
            market_data: Market intelligence
            
        Returns:
            Optimized price in cents
        """
        competitor_prices = market_data.get("competitor_prices", [])
        
        if not competitor_prices:
            # No competitors, use base markup
            return calculate_suggested_retail(self.variant, self.base_markup_percent)
        
        avg_price = market_data.get("avg_price_cents", 0)
        min_price_market = market_data.get("min_price_cents", 0)
        max_price_market = market_data.get("max_price_cents", 0)
        
        # Strategy: Find the sweet spot
        # If market is polarized (big gap between min and max), position in the middle
        if max_price_market - min_price_market > 2000:  # Gap > $20
            # Position at 60% between min and max (slightly above middle)
            target_price = int(min_price_market + (max_price_market - min_price_market) * 0.6)
        elif avg_price > 0:
            # Market is competitive, price slightly below average to be attractive
            target_price = int(avg_price * 0.95)
        else:
            target_price = calculate_suggested_retail(self.variant, self.base_markup_percent)
        
        # Ensure we maintain minimum margin
        return max(target_price, self.min_price)
    
    def update_listing_strategy(self, sales_stats: Dict, market_data: Dict) -> Dict:
        """
        Update strategy using data-driven optimization.
        
        Strategy:
        - Analyze sales velocity and market position
        - Implement dynamic pricing based on performance
        - Test different messaging approaches
        - Respond to competitive moves
        
        Args:
            sales_stats: Our sales performance
            market_data: Competitor information
            
        Returns:
            Dict with optimized updates
        """
        updates = {}
        self.update_count += 1
        
        total_sales = sales_stats.get("total_sales", 0)
        my_products = market_data.get("my_products", [])
        
        if not my_products:
            return updates
        
        current_price = my_products[0].get("price_in_cent", self.spec.wholesale_cost_cents)
        competitor_prices = market_data.get("competitor_prices", [])
        avg_price = market_data.get("avg_price_cents", current_price)
        
        # Analyze our market position
        position = self._analyze_market_position(current_price, competitor_prices, avg_price)
        
        print(f"  🎯 {self.name}: Sales={total_sales}, Position={position}, Price=${current_price/100:.2f}")
        
        # Decision tree based on performance and position
        if total_sales == 0:
            # No sales yet - need to optimize
            updates = self._optimize_for_zero_sales(current_price, position, competitor_prices, avg_price)
        elif total_sales == 1:
            # Got our first sale - stay course but optimize messaging
            updates = self._optimize_for_low_sales(current_price, position)
        else:
            # Multiple sales - we're doing something right
            updates = self._optimize_for_good_sales(current_price, position, total_sales)
        
        return updates
    
    def _analyze_market_position(self, my_price: int, competitor_prices: list, avg_price: int) -> str:
        """
        Analyze our position in the market.
        
        Returns:
            Position category: "cheapest", "competitive", "premium", or "expensive"
        """
        if not competitor_prices:
            return "alone"
        
        min_competitor = min(competitor_prices)
        max_competitor = max(competitor_prices)
        
        if my_price < min_competitor:
            return "cheapest"
        elif my_price <= avg_price:
            return "competitive"
        elif my_price <= max_competitor:
            return "premium"
        else:
            return "expensive"
    
    def _optimize_for_zero_sales(self, current_price: int, position: str, 
                                  competitor_prices: list, avg_price: int) -> Dict:
        """Optimization strategy when we have no sales - can use loss-leader"""
        updates = {}
        wholesale = self.spec.wholesale_cost_cents
        
        if position == "expensive":
            # We're too expensive - aggressive price drop
            # Willing to go below cost if necessary (loss-leader strategy)
            if current_price > wholesale * 1.5:
                # Very expensive - drop to below wholesale to grab market share
                target_price = int(wholesale * 0.85)  # 15% below wholesale
                target_price = max(target_price, self.min_price)
                updates["price"] = target_price
                if target_price < wholesale:
                    print(f"    → LOSS-LEADER: Dropping to ${target_price/100:.2f} (below cost) to gain market share")
                    updates["short_description"] = "🔥 LIMITED TIME: Premium quality at unbeatable introductory price"
                else:
                    updates["short_description"] = "Premium quality at a competitive price - exceptional value"
                    print(f"    → Too expensive, dropping to ${target_price/100:.2f}")
            else:
                # Moderately expensive - drop to competitive
                target_price = int(avg_price * 0.95)  # 5% below average
                target_price = max(target_price, self.min_price)
                updates["price"] = target_price
                updates["short_description"] = "Premium quality at a competitive price - exceptional value"
                print(f"    → Dropping to ${target_price/100:.2f}")
            
        elif position == "cheapest":
            # We're cheapest but not selling - might be quality concerns
            # Raise price slightly and improve messaging
            target_price = int(current_price * 1.15)  # 15% increase
            updates["price"] = min(target_price, avg_price)
            updates["short_description"] = "Professional-grade quality you can trust - backed by satisfaction guarantee"
            print(f"    → Improving perceived quality, raising to ${updates['price']/100:.2f}")
            
        else:  # competitive or premium
            # Price is reasonable - must be messaging issue
            # A/B test new description
            tech_desc = get_technical_description(self.variant)
            descriptions = [
                f"Premium quality meets smart pricing - {tech_desc}",
                f"Professional-grade quality you can trust - {tech_desc}",
                f"Superior comfort without the premium price tag - {tech_desc}",
            ]
            updates["short_description"] = random.choice(descriptions)
            print(f"    → A/B testing new messaging")
        
        return updates
    
    def _optimize_for_low_sales(self, current_price: int, position: str) -> Dict:
        """Optimization strategy when we have 1 sale"""
        updates = {}
        
        # We're starting to convert - enhance messaging with social proof
        updates["short_description"] = "Proven quality - trusted by smart shoppers who demand both value and performance"
        
        # Small price optimization based on position
        if position == "cheapest":
            # Can afford to raise price slightly
            new_price = int(current_price * 1.08)
            updates["price"] = new_price
            print(f"    → Raising price to ${new_price/100:.2f} while maintaining momentum")
        
        return updates
    
    def _optimize_for_good_sales(self, current_price: int, position: str, sales_count: int) -> Dict:
        """Optimization strategy when we have multiple sales"""
        updates = {}
        
        # We're winning - optimize for profit
        if position == "cheapest" or position == "competitive":
            # We can raise prices
            new_price = int(current_price * 1.12)  # 12% increase
            updates["price"] = new_price
            updates["short_description"] = (
                f"Bestseller! Chosen by {sales_count}+ customers - "
                "experience the quality that's winning rave reviews"
            )
            print(f"    → Bestseller pricing: raising to ${new_price/100:.2f}")
        else:
            # Already premium priced - just enhance messaging
            updates["short_description"] = (
                f"★★★★★ Trusted by {sales_count}+ discerning buyers - "
                "discover why customers choose us again and again"
            )
            print(f"    → Reinforcing premium position with social proof")
        
        return updates

