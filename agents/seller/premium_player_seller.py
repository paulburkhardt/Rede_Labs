"""
Premium Player Seller Agent

Competes on quality and luxury positioning - targets quality-seekers and brand-conscious buyers.
Strategy: Maintain premium pricing and emphasize luxury, quality, and exclusivity.
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


class PremiumPlayerSeller(SellerAgent):
    """
    Premium Player Seller Strategy
    
    Philosophy: Quality and luxury justify premium pricing.
    - Prices 15-30% above market average
    - Rich, detailed descriptions emphasizing craftsmanship and exclusivity
    - Maintains premium positioning even with low initial sales
    - Targets quality-seekers and brand-conscious buyers
    """
    
    def __init__(self, name: str = "Premium Player", api: Optional[MarketplaceAPI] = None):
        super().__init__(name, "premium", api)
        
        # Select PREMIUM variant (aligned with luxury strategy)
        self.variant = TowelVariant.PREMIUM
        self.spec = get_towel_spec(self.variant)
        
        # Pricing strategy: High markup luxury pricing
        self.base_markup_percent = 150  # Start with 150% markup (premium strategy)
        self.min_markup_percent = 80  # Prefer 80% profit margin minimum
        self.preferred_min = int(self.spec.wholesale_cost_cents * (1 + self.min_markup_percent / 100))
        
        # Absolute floor at 50% of wholesale - will avoid this if possible
        self.min_price = self.spec.wholesale_cost_cents // 2  # $7.50 floor for PREMIUM
        
        # Premium strategy: Rarely goes below wholesale, focuses on maintaining premium positioning
        
    def select_product_and_create_listing(self) -> tuple[TowelVariant, Dict]:
        """
        Select PREMIUM variant and create luxury-focused listing.
        
        Returns:
            Tuple of (TowelVariant.PREMIUM, marketing_data)
        """
        # Choose a random premium product name
        product_name = random.choice(DEFAULT_PRODUCT_NAMES[TowelVariant.PREMIUM])
        
        # Get market data to position above competitors
        market_data = self.api.get_market_intelligence() if self.is_registered else {}
        initial_price = self.determine_price(self.spec.wholesale_cost_cents, market_data)
        
        # Create luxury-focused marketing copy
        tech_desc = get_technical_description(self.variant)
        
        marketing_data = {
            "name": product_name,
            "short_description": f"Experience hotel-spa luxury with our premium {tech_desc} towel",
            "long_description": (
                f"Indulge in the ultimate bath experience with our {product_name}. "
                f"Crafted from the finest materials and designed for those who demand excellence.\n\n"
                f"Premium Specifications: {tech_desc}\n\n"
                f"Luxury Features:\n"
                f"• Extra large dimensions for maximum coverage and comfort\n"
                f"• Premium 600 GSM fabric for exceptional plushness\n"
                f"• Superior absorbency that only improves with time\n"
                f"• Oversized design for true luxury experience\n"
                f"• Hotel and spa quality construction\n\n"
                f"This isn't just a towel - it's an investment in daily luxury. "
                f"The exceptional density and careful craftsmanship create an experience "
                f"that's remarkably absorbent yet surprisingly lightweight.\n\n"
                f"Recommended by interior designers and preferred by discerning homeowners "
                f"who understand that true quality is worth the investment."
            ),
            "price": initial_price,
            "image": DEFAULT_IMAGES[TowelVariant.PREMIUM]
        }
        
        return self.variant, marketing_data
    
    def determine_price(self, wholesale_cost: int, market_data: Dict) -> int:
        """
        Calculate premium pricing strategy.
        
        Strategy:
        - Start with high markup (150%)
        - If market average exists, price 25-30% above it
        - Prefers minimum 80% profit margin (rarely uses loss-leader)
        - Can drop to floor in extreme cases but avoids it
        
        Args:
            wholesale_cost: Wholesale cost of the product
            market_data: Market intelligence
            
        Returns:
            Premium price in cents
        """
        avg_price = market_data.get("avg_price_cents", 0)
        
        if avg_price == 0:
            # No market data, use our premium markup
            return calculate_suggested_retail(self.variant, self.base_markup_percent)
        
        # Price 25% above market average
        target_price = int(avg_price * 1.25)
        
        # Prefer to stay above preferred minimum (80% margin)
        # But can go to absolute floor if needed
        return max(target_price, self.preferred_min)
    
    def update_listing_strategy(self, sales_stats: Dict, market_data: Dict) -> Dict:
        """
        Update strategy based on sales performance.
        
        Strategy:
        - Never compete on price - maintain premium positioning
        - If sales are slow, enhance quality messaging instead of lowering price
        - If sales are good, emphasize exclusivity and social proof
        - May make modest price adjustments (10% max) if completely shut out
        
        Args:
            sales_stats: Our sales performance
            market_data: Competitor information
            
        Returns:
            Dict with updates to apply
        """
        updates = {}
        
        total_sales = sales_stats.get("total_sales", 0)
        my_products = market_data.get("my_products", [])
        
        if not my_products:
            return updates
        
        current_price = my_products[0].get("price_in_cent", self.spec.wholesale_cost_cents)
        avg_price = market_data.get("avg_price_cents", current_price)
        
        # Strategy 1: If we have good sales, emphasize exclusivity
        if total_sales >= 2:
            updates["short_description"] = (
                f"Trusted by discerning buyers - join {total_sales}+ customers who chose quality"
            )
            print(f"  ✨ {self.name}: Strong sales, emphasizing social proof")
        
        # Strategy 2: If we have zero sales and market is much cheaper
        elif total_sales == 0 and current_price > avg_price * 1.5:
            # Market is significantly cheaper - make a modest adjustment
            # Try to stay above preferred minimum, but can go lower in extreme cases
            new_price = max(
                int(current_price * 0.92),  # 8% reduction maximum
                self.preferred_min  # Prefer to stay above 80% margin
            )
            
            # Only drop below preferred if absolutely necessary
            if new_price < current_price:
                if new_price < self.spec.wholesale_cost_cents:
                    print(f"  ✨ {self.name}: WARNING - Considering pricing below cost at ${new_price/100:.2f}")
                updates["price"] = new_price
                updates["short_description"] = (
                    "Limited time pricing - experience luxury without compromise"
                )
                print(f"  ✨ {self.name}: Modest price adjustment to ${new_price/100:.2f}")
        
        # Strategy 3: No sales but we're reasonably priced - enhance messaging
        elif total_sales == 0:
            updates["name"] = "★ " + my_products[0].get("name", "Luxury Towels").replace("★ ", "")
            updates["short_description"] = (
                "Uncompromising quality for those who demand excellence - "
                "experience the difference luxury makes"
            )
            print(f"  ✨ {self.name}: Enhancing premium messaging and visibility")
        
        return updates

