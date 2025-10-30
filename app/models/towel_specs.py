"""
Towel variant specifications and constants.
"""
from enum import Enum
from dataclasses import dataclass
from typing import Dict


class TowelVariant(str, Enum):
    """Enum for towel product variants"""
    BUDGET = "budget"
    MID_TIER = "mid_tier"
    PREMIUM = "premium"


@dataclass
class TowelSpecification:
    """Specification for a towel variant"""
    variant: TowelVariant
    gsm: int  # Grams per square meter
    width_inches: int
    length_inches: int
    material: str
    wholesale_cost_cents: int  # Wholesale cost in cents


# Available towel variants with their specifications
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
        gsm=550,
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
        material="Premium Cotton",
        wholesale_cost_cents=1500  # $15.00 wholesale cost
    )
}


def get_towel_specification(variant: TowelVariant) -> TowelSpecification:
    """Get the specification for a given towel variant"""
    return TOWEL_VARIANTS[variant]
