"""
Towel Product Definitions - Environment Configuration

This file defines the towel product variants available in the marketplace.
These are FIXED by the environment and cannot be changed by participants.

Sellers can:
1. Choose which variant(s) to sell
2. Set their markup/retail price (above wholesale cost)
3. Create their own marketing descriptions
4. Choose product images

Sellers cannot:
1. Change the physical specifications
2. Change the wholesale cost
3. Create custom product variants
"""

from typing import Dict, List, NamedTuple
from enum import Enum


class TowelVariant(Enum):
    """Available towel variants in the marketplace"""
    BUDGET = "budget"
    MID_TIER = "mid_tier"
    PREMIUM = "premium"


class TowelSpecification(NamedTuple):
    """Physical specifications of a towel variant"""
    variant: TowelVariant
    gsm: int  # Grams per square meter (fabric density)
    width_inches: int
    length_inches: int
    material: str
    wholesale_cost_cents: int  # Cost seller must pay
    
    @property
    def size_description(self) -> str:
        """Get size as readable string"""
        return f"{self.width_inches}\" x {self.length_inches}\""
    
    @property
    def wholesale_cost_dollars(self) -> float:
        """Get wholesale cost in dollars"""
        return self.wholesale_cost_cents / 100


# ============================================================
# ENVIRONMENT CONFIGURATION - Fixed Product Variants
# ============================================================

TOWEL_VARIANTS: Dict[TowelVariant, TowelSpecification] = {
    TowelVariant.BUDGET: TowelSpecification(
        variant=TowelVariant.BUDGET,
        gsm=500,
        width_inches=27,
        length_inches=54,
        material="Standard Cotton",
        wholesale_cost_cents=800  # $8.00 wholesale cost
    ),
    
    TowelVariant.MID_TIER: TowelSpecification(
        variant=TowelVariant.MID_TIER,
        gsm=600,
        width_inches=27,
        length_inches=54,
        material="Premium Cotton",
        wholesale_cost_cents=1200  # $12.00 wholesale cost
    ),
    
    TowelVariant.PREMIUM: TowelSpecification(
        variant=TowelVariant.PREMIUM,
        gsm=600,
        width_inches=27,
        length_inches=59,
        material="Premium Cotton Extra Large",
        wholesale_cost_cents=1500  # $15.00 wholesale cost
    )
}


def get_towel_spec(variant: TowelVariant) -> TowelSpecification:
    """
    Get specification for a towel variant.
    
    Args:
        variant: The towel variant to get specs for
        
    Returns:
        TowelSpecification for that variant
    """
    return TOWEL_VARIANTS[variant]


def get_all_variants() -> List[TowelSpecification]:
    """Get all available towel variants"""
    return list(TOWEL_VARIANTS.values())


def get_minimum_price(variant: TowelVariant) -> int:
    """
    Get the absolute minimum price (50% of wholesale cost).
    
    This floor enables loss-leader strategies while preventing extreme pricing.
    Sellers can sell below wholesale cost (at a loss) but not below 50% of wholesale.
    
    Strategic implications:
    - Agents can use loss-leader pricing to gain market share
    - Must eventually recover losses with profitable sales
    - Competition winner determined by total profit (revenue - costs)
    
    Args:
        variant: The towel variant
        
    Returns:
        Minimum price in cents (50% of wholesale)
    """
    return TOWEL_VARIANTS[variant].wholesale_cost_cents // 2


def calculate_suggested_retail(variant: TowelVariant, markup_percent: float = 100) -> int:
    """
    Calculate suggested retail price based on markup.
    
    Args:
        variant: The towel variant
        markup_percent: Markup percentage (100 = 2x wholesale, 50 = 1.5x wholesale)
        
    Returns:
        Suggested retail price in cents
    """
    wholesale = TOWEL_VARIANTS[variant].wholesale_cost_cents
    return int(wholesale * (1 + markup_percent / 100))


def validate_price(variant: TowelVariant, retail_price_cents: int) -> tuple[bool, str]:
    """
    Validate that a retail price is acceptable.
    
    Pricing rules:
    - Minimum: 50% of wholesale cost (allows loss-leader strategies)
    - Maximum: 10x wholesale cost (prevents extreme pricing)
    
    Args:
        variant: The towel variant
        retail_price_cents: Proposed retail price
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    spec = TOWEL_VARIANTS[variant]
    min_price = spec.wholesale_cost_cents // 2
    max_price = spec.wholesale_cost_cents * 10
    
    if retail_price_cents < min_price:
        return False, f"Price ${retail_price_cents/100:.2f} is below minimum floor ${min_price/100:.2f} (50% of wholesale)"
    
    if retail_price_cents > max_price:
        return False, f"Price ${retail_price_cents/100:.2f} exceeds 10x markup limit"
    
    return True, ""


def get_variant_summary() -> str:
    """
    Get a formatted summary of all towel variants.
    Useful for displaying to sellers.
    
    Returns:
        Formatted string with all variant information
    """
    lines = ["=" * 70]
    lines.append("AVAILABLE TOWEL VARIANTS")
    lines.append("=" * 70)
    lines.append("")
    lines.append("Note: Floor price is 50% of wholesale (allows loss-leader strategies)")
    lines.append("Winner determined by total PROFIT (revenue - costs)")
    
    for variant in TowelVariant:
        spec = TOWEL_VARIANTS[variant]
        min_price = spec.wholesale_cost_cents // 2
        max_loss = spec.wholesale_cost_cents - min_price
        
        lines.append(f"\n{variant.value.upper().replace('_', ' ')}:")
        lines.append(f"  Size: {spec.size_description}")
        lines.append(f"  GSM: {spec.gsm} (fabric density)")
        lines.append(f"  Material: {spec.material}")
        lines.append(f"  Wholesale Cost: ${spec.wholesale_cost_dollars:.2f}")
        lines.append(f"  Floor Price: ${min_price/100:.2f} (50% of wholesale)")
        lines.append(f"  Max Loss/Sale: ${max_loss/100:.2f} (if priced at floor)")
        lines.append(f"  Suggested Retail: ${calculate_suggested_retail(variant, 100)/100:.2f} (100% markup)")
    
    lines.append("")
    lines.append("=" * 70)
    lines.append("STRATEGIC OPTIONS:")
    lines.append("  • Loss-Leader: Price below wholesale to gain market share")
    lines.append("  • Balanced: Price at moderate markup for steady profit")
    lines.append("  • Premium: Price high to maximize profit per sale")
    lines.append("  • Dynamic: Adjust strategy based on performance")
    lines.append("=" * 70)
    return "\n".join(lines)


# ============================================================
# Marketing Templates - Sellers Can Use/Customize These
# ============================================================

# Default product names by variant (sellers can customize)
DEFAULT_PRODUCT_NAMES = {
    TowelVariant.BUDGET: [
        "Economy Bath Towel",
        "Value Bath Towel",
        "Essential Bath Towel",
        "Budget-Friendly Bath Towel"
    ],
    TowelVariant.MID_TIER: [
        "Premium Bath Towel",
        "Comfort Plus Bath Towel",
        "Quality Bath Towel",
        "Professional Bath Towel"
    ],
    TowelVariant.PREMIUM: [
        "Luxury Bath Towel XL",
        "Deluxe Bath Towel",
        "Hotel-Quality Bath Towel",
        "Premium Oversized Bath Towel"
    ]
}

# Technical description that should be included (can be embedded in marketing copy)
def get_technical_description(variant: TowelVariant) -> str:
    """
    Get the technical/factual description that must be included.
    
    Args:
        variant: The towel variant
        
    Returns:
        Technical description string
    """
    spec = TOWEL_VARIANTS[variant]
    return f"{spec.gsm} GSM {spec.material}, {spec.size_description} inches"


# Placeholder images by variant
DEFAULT_IMAGES = {
    TowelVariant.BUDGET: {
        "url": "https://images.unsplash.com/photo-1616627577649-cd673750e484?w=400",
        "alternative_text": "Budget bath towel - standard cotton"
    },
    TowelVariant.MID_TIER: {
        "url": "https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?w=600",
        "alternative_text": "Premium bath towel - premium cotton"
    },
    TowelVariant.PREMIUM: {
        "url": "https://images.unsplash.com/photo-1582735689369-4fe89db7114c?w=800",
        "alternative_text": "Luxury bath towel - premium cotton extra large"
    }
}


if __name__ == "__main__":
    # Display variant summary
    print(get_variant_summary())
    
    # Example: Calculate pricing strategies
    print("\nEXAMPLE PRICING STRATEGIES:")
    print("-" * 70)
    
    for variant in TowelVariant:
        spec = TOWEL_VARIANTS[variant]
        min_price = get_minimum_price(variant)
        
        print(f"\n{variant.value.upper().replace('_', ' ')}:")
        print(f"  Wholesale Cost: ${spec.wholesale_cost_dollars:.2f}")
        print(f"  Floor Price: ${min_price/100:.2f} (50% of wholesale)")
        print(f"  ")
        print(f"  Loss-Leader: ${min_price/100:.2f} (lose ${(spec.wholesale_cost_cents - min_price)/100:.2f}/sale)")
        print(f"  Below Cost: ${(spec.wholesale_cost_cents * 0.75)/100:.2f} (lose ${(spec.wholesale_cost_cents * 0.25)/100:.2f}/sale)")
        print(f"  Break-Even: ${spec.wholesale_cost_dollars:.2f} (no profit/loss)")
        print(f"  Small Profit: ${calculate_suggested_retail(variant, 25)/100:.2f} (earn ${(spec.wholesale_cost_cents * 0.25)/100:.2f}/sale)")
        print(f"  Balanced: ${calculate_suggested_retail(variant, 100)/100:.2f} (earn ${spec.wholesale_cost_dollars:.2f}/sale)")
        print(f"  Premium: ${calculate_suggested_retail(variant, 150)/100:.2f} (earn ${(spec.wholesale_cost_cents * 1.5)/100:.2f}/sale)")

