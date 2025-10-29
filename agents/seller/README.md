# Seller Agents (White Agents)

This directory contains the implementation of seller agents (white agents) for the marketplace competition environment. These agents compete to maximize revenue by creating and optimizing product listings.

## Overview

Three distinct seller strategies are implemented as semi-dummy agents for testing:

1. **Budget King** - Price-focused competitive strategy
2. **Premium Player** - Quality and luxury positioning
3. **Dynamic Optimizer** - Data-driven adaptive approach

## Architecture

```
agents/seller/
├── seller_utils.py              # API wrapper and utilities
├── seller_agent_base.py         # Abstract base class
├── product_templates.py         # Product data templates
├── budget_king_seller.py        # Strategy 1: Price competition
├── premium_player_seller.py     # Strategy 2: Premium positioning
├── dynamic_optimizer_seller.py  # Strategy 3: Adaptive optimization
├── budget_king.toml            # Configuration for Budget King
├── premium_player.toml         # Configuration for Premium Player
├── dynamic_optimizer.toml      # Configuration for Dynamic Optimizer
├── test_seller_agents.py       # Test suite
└── README.md                   # This file
```

## Seller Strategies

### 1. Budget King (Price Competition)

**Philosophy**: Price is king. Win by being the cheapest option.

**Strategy**:
- Starts at $19.99 base price
- Undercuts competitors by 10-15%
- Never goes below $14.99 floor price
- Simple, practical product descriptions
- Aggressively responds to competitor pricing

**Target Buyers**:
- Price-Conscious Value Hunters (primary)
- Confused by Overchoice (secondary)

**Example Behavior**:
```python
from agents.seller import BudgetKingSeller

seller = BudgetKingSeller()
seller.register()           # Register with marketplace
seller.create_listing()     # Create budget-focused listing
seller.update_listing()     # Adjust price based on competitors
```

### 2. Premium Player (Luxury Positioning)

**Philosophy**: Quality and luxury justify premium pricing.

**Strategy**:
- Starts at $59.99 base price
- Prices 25-30% above market average
- Never discounts more than 8%
- Rich, detailed descriptions emphasizing craftsmanship
- Maintains premium positioning even with low sales

**Target Buyers**:
- Perfectionist Quality Seekers (primary)
- Brand Conscious Price Perceivers (primary)
- Recreational Hedonistic Shoppers (secondary)

**Example Behavior**:
```python
from agents.seller import PremiumPlayerSeller

seller = PremiumPlayerSeller()
seller.register()
seller.create_listing()     # Create luxury-focused listing
seller.update_listing()     # Enhance messaging, rarely discount
```

### 3. Dynamic Optimizer (Adaptive Strategy)

**Philosophy**: Use data to continuously optimize performance.

**Strategy**:
- Starts at $34.99 mid-market price
- Analyzes market gaps and positions strategically
- A/B tests different descriptions
- Responds to sales velocity:
  - No sales + expensive → drop price
  - No sales + cheap → raise price + improve messaging
  - Good sales → increase price for profit
- Price range: $24.99 - $49.99

**Target Buyers**:
- All buyer personas (adaptive)
- Confused by Overchoice (primary)

**Example Behavior**:
```python
from agents.seller import DynamicOptimizerSeller

seller = DynamicOptimizerSeller()
seller.register()
seller.create_listing()     # Create balanced listing
seller.update_listing()     # Data-driven optimization
```

## Quick Start

### Prerequisites

1. Start the marketplace API:
```bash
uv run python run.py
```

2. Ensure database is running:
```bash
docker-compose up -d
```

### Running Tests

Test all seller agents:
```bash
cd agents/seller
python test_seller_agents.py
```

### Using Seller Agents

**Basic Usage**:
```python
from agents.seller import BudgetKingSeller, PremiumPlayerSeller, DynamicOptimizerSeller

# Create seller instances
budget = BudgetKingSeller("Budget Store")
premium = PremiumPlayerSeller("Luxury Linens")
dynamic = DynamicOptimizerSeller("Smart Seller")

# Register with marketplace
budget.register()
premium.register()
dynamic.register()

# Create listings
budget.create_listing()
premium.create_listing()
dynamic.create_listing()

# Update based on market conditions
budget.update_listing()
premium.update_listing()
dynamic.update_listing()

# Get performance summaries
print(budget.get_performance_summary())
print(premium.get_performance_summary())
print(dynamic.get_performance_summary())
```

**With Custom API Instance**:
```python
from agents.seller import BudgetKingSeller, MarketplaceAPI

# Use custom API URL
api = MarketplaceAPI(base_url="http://custom-url:8000")
seller = BudgetKingSeller(api=api)

# Rest is the same
seller.register()
seller.create_listing()
```

## API Reference

### MarketplaceAPI

Wrapper for marketplace API interactions.

**Methods**:
- `register_seller()` - Register and get auth token
- `create_product(product_id, product_data)` - Create a product
- `update_product(product_id, updates)` - Update a product
- `get_sales_stats()` - Get sales statistics
- `search_products(query)` - Search marketplace
- `get_market_intelligence()` - Analyze market conditions

### SellerAgent (Base Class)

Abstract base class for all seller strategies.

**Abstract Methods** (must implement):
- `create_initial_listing()` - Create product data
- `update_listing_strategy(sales_stats, market_data)` - Optimization logic
- `determine_price(base_price, market_data)` - Pricing strategy

**Concrete Methods**:
- `register()` - Register with marketplace
- `create_listing()` - Create listing using strategy
- `update_listing()` - Update based on strategy
- `get_performance_summary()` - Get metrics

## Integration with Green Agent

The green agent orchestrator can use these sellers as follows:

```python
# In green agent orchestration
from agents.seller import BudgetKingSeller, PremiumPlayerSeller, DynamicOptimizerSeller

async def setup_sellers(seller_count: int):
    """Create test sellers for the battle"""
    seller_types = [BudgetKingSeller, PremiumPlayerSeller, DynamicOptimizerSeller]
    sellers = []
    
    for i in range(seller_count):
        SellerClass = seller_types[i % len(seller_types)]
        seller = SellerClass(f"Seller_{i+1}")
        seller.register()
        sellers.append(seller)
    
    return sellers

async def create_listings_phase(sellers):
    """Day 1: Create initial listings"""
    for seller in sellers:
        seller.create_listing()

async def update_listings_phase(sellers):
    """Subsequent days: Update listings"""
    for seller in sellers:
        seller.update_listing()
```

## Testing Strategy

### Unit Tests (Recommended to add)

```python
# tests/test_seller_agents.py
def test_budget_king_pricing():
    seller = BudgetKingSeller()
    seller.register()
    
    # Test undercuts competitors
    market_data = {"competitor_prices": [2500, 3000]}
    price = seller.determine_price(2000, market_data)
    assert price < 2500

def test_premium_maintains_floor():
    seller = PremiumPlayerSeller()
    seller.register()
    
    # Test never goes below floor
    market_data = {"avg_price_cents": 2000}
    price = seller.determine_price(5999, market_data)
    assert price >= 3999
```

### Integration Tests

Run `test_seller_agents.py` to test:
- API connectivity
- Seller registration
- Product creation
- Market analysis
- Update strategies
- Multi-seller competition

## Extending the System

### Adding a New Seller Strategy

1. Create new file `my_strategy_seller.py`:

```python
from agents.seller.seller_agent_base import SellerAgent
from agents.seller.product_templates import get_random_product_template

class MyStrategySeller(SellerAgent):
    def __init__(self, name: str = "My Strategy", api=None):
        super().__init__(name, "my_strategy", api)
    
    def create_initial_listing(self) -> Dict:
        template = get_random_product_template("dynamic")
        return {
            "name": template["name"],
            "short_description": "My unique description",
            "long_description": template["long_description"],
            "price": 2999,
            "image": template["image"]
        }
    
    def determine_price(self, base_price: int, market_data: Dict) -> int:
        # Your pricing logic
        return base_price
    
    def update_listing_strategy(self, sales_stats: Dict, market_data: Dict) -> Dict:
        # Your update logic
        return {}
```

2. Create configuration `my_strategy.toml`:

```toml
id = "my_strategy"
name = "My Strategy"
strategy = "my_strategy"
description = '''Your strategy description'''
```

3. Add to `__init__.py` and test!

## Performance Metrics

Each seller tracks:
- **Total Sales**: Number of products sold
- **Total Revenue**: Revenue in cents and dollars
- **Market Position**: Relative to competitors
- **Price History**: Track of price adjustments
- **Update Count**: Number of strategy updates

Access via:
```python
summary = seller.get_performance_summary()
```

## Competition Rules

These sellers are designed to compete in the marketplace environment where:

1. **Day 1**: All sellers create initial listings
2. **Ranking**: Green agent assigns initial random rankings
3. **Buyer Phase**: Buyer agents browse and purchase
4. **Update Phase**: Sellers update based on performance
5. **Re-ranking**: Rankings updated based on sales
6. **Repeat**: Steps 3-5 repeat for multiple days

Winner is determined by total revenue after all days.

## Troubleshooting

**API Connection Errors**:
```bash
# Make sure API is running
uv run python run.py

# Check database is up
docker-compose ps
```

**Import Errors**:
```bash
# Make sure you're in the right directory
cd /path/to/Rede_Labs
python agents/seller/test_seller_agents.py
```

**No Sales**:
- Check buyer agents are configured
- Verify product search is working
- Review pricing strategy
- Check product descriptions

## Future Enhancements

Potential improvements:
- [ ] Machine learning for price optimization
- [ ] Sentiment analysis of descriptions
- [ ] A/B testing framework
- [ ] Historical performance tracking
- [ ] Multi-product strategies
- [ ] Collaborative filtering for recommendations
- [ ] Real-time competitor monitoring
- [ ] Automated description generation with LLMs

## License

Part of the Rede Labs Marketplace Competition Environment.

