"""
Product Templates

Shared product data templates for different seller strategies.
"""

import random
from typing import Dict, List


# Product name templates by strategy
PRODUCT_NAMES = {
    "budget": [
        "Economy Bath Towel Set - Best Value",
        "Value Pack Bath Towels",
        "Budget-Friendly Towel Collection",
        "Affordable Quality Towels",
        "Smart Saver Bath Towel Set"
    ],
    "premium": [
        "Luxury Egyptian Cotton Towels",
        "Premium Hotel-Quality Collection",
        "Artisan-Crafted Bath Linens",
        "Royal Spa Collection Towels",
        "Designer Bath Towel Collection"
    ],
    "dynamic": [
        "Premium Comfort Bath Towels",
        "Professional Quality Towel Set",
        "Modern Bath Collection",
        "Essential Bath Towels Plus",
        "Superior Comfort Towel Collection"
    ]
}

# Short descriptions by strategy
SHORT_DESCRIPTIONS = {
    "budget": [
        "Affordable, practical towels that get the job done without breaking the bank",
        "Great value for everyday use - quality basics at an unbeatable price",
        "Simple, functional towels perfect for budget-conscious shoppers",
        "No-frills quality at a price that makes sense",
        "Practical towels that deliver real value for your money"
    ],
    "premium": [
        "Indulge in hotel-spa luxury with our hand-selected premium cotton towels",
        "Experience unparalleled softness and durability with premium craftsmanship",
        "Elevate your bathroom with luxury linens crafted from the finest materials",
        "Transform your daily routine into a spa-like experience",
        "Exceptional quality meets timeless elegance in every fiber"
    ],
    "dynamic": [
        "High-quality towels designed for comfort and durability",
        "Premium materials meet smart pricing for exceptional value",
        "Professional-grade towels for the discerning buyer",
        "Superior comfort without the premium price tag",
        "Quality you can feel, price you'll appreciate"
    ]
}

# Long descriptions by strategy
LONG_DESCRIPTIONS = {
    "budget": [
        """Looking for reliable bath towels without the luxury price tag? Our Economy Bath Towel Set 
delivers exactly what you need: absorbent, durable towels that handle daily use with ease. Made 
from quality cotton blend, these towels are practical, machine-washable, and built to last. 

Features:
• 100% functional design - no unnecessary frills
• Machine washable and quick-drying
• Suitable for everyday family use
• Generous size for full coverage
• Available in classic neutral colors

Perfect for budget-conscious households, rental properties, or anyone who values practical quality 
over brand names. Why pay more for the same functionality? Get the job done right without overspending.""",
        
        """Smart shoppers know that quality doesn't always come with a premium price tag. Our Value Pack 
Bath Towels prove it. These towels deliver reliable performance, good absorption, and durability at 
a fraction of what you'd pay elsewhere.

What you get:
• Solid cotton construction for reliable absorption
• Standard size suitable for all family members
• Easy-care fabric that stands up to regular washing
• Simple, honest quality with no marketing gimmicks
• The best price-to-performance ratio you'll find

No fancy packaging, no celebrity endorsements - just good towels at a fair price. That's value."""
    ],
    "premium": [
        """Crafted from the finest long-staple Egyptian cotton, our Luxury Collection represents the 
pinnacle of bath linen excellence. Each towel is woven using traditional methods passed down through 
generations, creating an exceptionally plush, absorbent texture that only improves with time.

Premium Features:
• 100% Egyptian cotton with 700 GSM weight
• Hand-selected fibers for maximum softness
• Double-stitched edges for lasting durability
• Oversized dimensions (30" x 58") for luxurious coverage
• Pre-washed for immediate softness
• Colorfast dyes that maintain vibrancy

Why settle for ordinary when you can experience extraordinary? Our towels transform your daily 
routine into a spa-like ritual. The investment in quality pays dividends in comfort, longevity, 
and pure indulgence. 

As featured in luxury hotels and exclusive spas worldwide, these towels represent a commitment 
to excellence that you'll feel with every use. Your bathroom deserves nothing less.""",
        
        """Welcome to the realm of true luxury. Our Artisan-Crafted Bath Linens collection represents 
hundreds of years of textile expertise, combined with modern quality control that ensures perfection 
in every thread.

Uncompromising Quality:
• Premium Turkish cotton, renowned for its superior absorbency
• 800 GSM ultra-plush construction
• Zero-twist yarn for cloud-like softness
• OEKO-TEX certified for purity and safety
• Reinforced hemming with elegant detailing
• Sophisticated color palette designed by textile artists

These aren't just towels - they're an investment in daily luxury. The exceptional density and 
careful craftsmanship create towels that are remarkably absorbent yet surprisingly lightweight. 
They dry quickly, resist pilling, and actually become softer with each wash.

Recommended by interior designers and preferred by discerning homeowners who understand that true 
quality is worth the investment. Experience the difference that genuine craftsmanship makes."""
    ],
    "dynamic": [
        """Our Premium Comfort Bath Towels strike the perfect balance between quality and value. 
Designed with input from hospitality professionals, these towels deliver professional-grade 
performance at a price that makes sense.

Quality Features:
• High-quality cotton blend optimized for absorption and durability
• 600 GSM weight provides excellent plushness
• Reinforced edges for extended lifespan
• Generous sizing (28" x 54") 
• Quick-drying design saves energy
• Available in modern, versatile colors

Whether you're upgrading your bathroom or replacing worn-out towels, this collection offers 
the reliability and comfort you need. Not too basic, not overpriced - just smart, quality 
towels that perform.""",
        
        """Introducing our Essential Bath Towels Plus - engineered for those who want genuine quality 
without paying for unnecessary luxury branding. These towels undergo rigorous testing to ensure 
they meet professional standards for absorption, durability, and comfort.

Practical Luxury:
• Premium cotton construction (no synthetic fillers)
• 650 GSM weight - the optimal density for quick drying and comfort
• Double-stitched hems prevent fraying
• Fade-resistant colors maintain their appeal
• Low-lint design for a cleaner bathroom
• Easy maintenance - machine wash and dry

We've eliminated the markup that comes with fancy packaging and celebrity endorsements. What 
remains is simply excellent towels at an honest price. Smart buyers recognize the difference."""
    ]
}

# Image URLs (using placeholder images)
PRODUCT_IMAGES = {
    "budget": [
        {
            "url": "https://images.unsplash.com/photo-1616627577649-cd673750e484?w=400",
            "alternative_text": "Simple white bath towel folded neatly"
        },
        {
            "url": "https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?w=400",
            "alternative_text": "Stack of basic cotton towels"
        },
        {
            "url": "https://images.unsplash.com/photo-1582735689369-4fe89db7114c?w=400",
            "alternative_text": "Practical bath towel set in neutral colors"
        }
    ],
    "premium": [
        {
            "url": "https://images.unsplash.com/photo-1616627577649-cd673750e484?w=800",
            "alternative_text": "Luxurious Egyptian cotton towels in elegant setting"
        },
        {
            "url": "https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?w=800",
            "alternative_text": "Premium spa-quality towels with rich texture"
        },
        {
            "url": "https://images.unsplash.com/photo-1582735689369-4fe89db7114c?w=800",
            "alternative_text": "Designer bath towels in sophisticated color palette"
        }
    ],
    "dynamic": [
        {
            "url": "https://images.unsplash.com/photo-1616627577649-cd673750e484?w=600",
            "alternative_text": "Modern bath towels with professional quality"
        },
        {
            "url": "https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?w=600",
            "alternative_text": "High-quality comfort towels in contemporary style"
        },
        {
            "url": "https://images.unsplash.com/photo-1582735689369-4fe89db7114c?w=600",
            "alternative_text": "Superior comfort towel collection"
        }
    ]
}


def get_random_product_template(strategy: str) -> Dict:
    """
    Get a random product template for the given strategy.
    
    Args:
        strategy: One of "budget", "premium", or "dynamic"
        
    Returns:
        Dict with name, short_description, long_description, and image
    """
    if strategy not in PRODUCT_NAMES:
        raise ValueError(f"Invalid strategy: {strategy}. Must be one of: budget, premium, dynamic")
    
    return {
        "name": random.choice(PRODUCT_NAMES[strategy]),
        "short_description": random.choice(SHORT_DESCRIPTIONS[strategy]),
        "long_description": random.choice(LONG_DESCRIPTIONS[strategy]),
        "image": random.choice(PRODUCT_IMAGES[strategy])
    }


def get_base_prices() -> Dict[str, int]:
    """
    Get base prices (in cents) for each strategy.
    
    Returns:
        Dict mapping strategy to base price in cents
    """
    return {
        "budget": 1999,      # $19.99
        "premium": 5999,     # $59.99
        "dynamic": 3499      # $34.99
    }

