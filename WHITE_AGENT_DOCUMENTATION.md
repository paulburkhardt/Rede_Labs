# Strategic Optimizer White Agent Documentation

## Overview

The **Strategic Optimizer** is a sophisticated AI seller agent designed for the MarketArena e-commerce benchmark. It maximizes **profit** (not just revenue) through data-driven market analysis, persona-targeted messaging, and adaptive pricing strategies.

---

## Environment & Available Actions

### The MarketArena Marketplace

MarketArena is a simulated e-commerce environment where AI seller agents compete to maximize profit over multiple simulation days. Each seller can:

1. **Create product listings** with name, description, price, and images
2. **Update existing products** to adjust pricing and messaging
3. **Analyze the market** to see competitor prices and own sales
4. **View sales statistics** to track performance

### Available Actions (Tools)

#### 1. create_product()
Creates a new product listing in the marketplace.

```
create_product(
  auth_token="seller_abc123",
  product_id="towel-001", 
  name="Luxe Spa Collection Bath Towels",
  short_description="600 GSM Premium Cotton",
  long_description="Experience hotel-quality luxury...",
  price=4999,           # Price in CENTS ($49.99)
  image_ids=["img-1"],  # Must match variant category
  towel_variant="premium"  # budget ($8), mid_tier ($12), premium ($15)
)
```

#### 2. update_product()
Modifies an existing product's price or description.

```
update_product(
  auth_token="seller_abc123",
  product_id="towel-001",
  price=5499,  # Raise price to $54.99
  short_description="Updated description..."
)
```

#### 3. get_market_analysis()
Returns comprehensive market intelligence in a single call.

```
get_market_analysis(auth_token="seller_abc123")

# Returns:
{
  "competitor_count": 2,
  "price_stats": {"min": 14.99, "max": 59.99, "avg": 32.50},
  "my_price": 49.99,
  "my_sales": 3,
  "my_position": "premium",
  "recommendation": "RAISE PRICE: Good sales at premium position!"
}
```

#### 4. search_products()
Search the marketplace to see all available products.

#### 5. get_sales_stats()
Get your own sales count and revenue.

#### 6. get_images_by_product_number()
Get available images for a product category (01=budget, 02=mid_tier, 03=premium).

### Buyer Purchasing Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   BUYER     │     │   SEARCH    │     │   COMPARE   │     │  PURCHASE   │
│   ARRIVES   │────▶│  PRODUCTS   │────▶│   OPTIONS   │────▶│  DECISION   │
│             │     │             │     │             │     │             │
│ Has budget  │     │ See all     │     │ Evaluate:   │     │ Buy or      │
│ and needs   │     │ listings    │     │ - Price     │     │ don't buy   │
│             │     │ (ranked)    │     │ - Quality   │     │             │
│             │     │             │     │ - Ranking   │     │             │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

Different buyer personas have different priorities:
- **Price-Conscious**: Focuses on lowest price
- **Quality-Seeker**: Looks for premium specs (GSM, materials)
- **Brand-Conscious**: Avoids cheapest option, trusts higher prices
- **Confused by Overchoice**: Picks highly-ranked or simple options
- **Hedonistic**: Drawn to emotional, sensory descriptions

### Ranking System

The marketplace uses a ranking system that affects product visibility:

```
MORE SALES ──▶ HIGHER RANKING ──▶ MORE VISIBILITY ──▶ MORE SALES
    │                                                      │
    └──────────────────────────────────────────────────────┘
                        (Feedback Loop)
```

**Ranking Rules:**
- Products are ranked by total sales count
- Higher-ranked products appear first to buyers
- Buyers often purchase from top-ranked products
- Early sales are crucial for establishing ranking position

**Strategic Implication:**
Day 0-1: Price competitively to capture early sales and ranking
Day 2+: Once ranked, gradually raise prices to maximize margins

---

## Agent Framework Architecture

### Principle-Based Decision Framework

The Strategic Optimizer uses a simple but effective three-step process:

```
┌─────────────────────────────────────────────────────────────────┐
│                    STRATEGIC OPTIMIZER                          │
├─────────────────────────────────────────────────────────────────┤
│  CORE PRINCIPLE: Profit = (Price - Cost) × Sales                │
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │   OBSERVE   │───▶│   REASON    │───▶│     ACT     │         │
│  │             │    │             │    │             │         │
│  │ • Call      │    │ • Margin    │    │ • Create    │         │
│  │   get_      │    │   Math      │    │   Product   │         │
│  │   market_   │    │ • Adapt     │    │ • Update    │         │
│  │   analysis  │    │   Rules     │    │   Price     │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

### Decision Pipeline Walkthrough

#### Step 1: OBSERVE - Market Analysis

The agent ALWAYS calls `get_market_analysis()` first to understand the current state.

**Example Output:**
```json
{
  "competitor_count": 2,
  "competitors": [
    {"name": "Budget King Towels", "price": 14.99, "sales": 5},
    {"name": "Premium Luxury Set", "price": 59.99, "sales": 1}
  ],
  "price_stats": {
    "min": 14.99,
    "max": 59.99,
    "avg": 37.49,
    "median": 37.49
  },
  "my_product": {
    "name": "Luxe Spa Collection",
    "price": 49.99,
    "sales": 3,
    "wholesale_cost": 15.00,
    "margin_per_sale": 34.99
  },
  "my_position": "premium",
  "recommendation": "RAISE PRICE: Getting sales at premium position indicates pricing power."
}
```

#### Step 2: REASON - Apply Economic Principles

The agent applies simple but powerful rules:

**Rule 1: Margin Math**
```
Profit = (Sale Price - Wholesale Cost) × Number of Sales

Example:
- Selling at $50 with $15 cost = $35 margin per sale
- 3 sales × $35 = $105 profit

vs.

- Selling at $20 with $15 cost = $5 margin per sale  
- 10 sales × $5 = $50 profit

HIGH MARGINS WIN even with fewer sales!
```

**Rule 2: Adaptation Based on Sales**
```
IF getting sales at current price:
    → RAISE price (you have pricing power)
    → Increase by 10-15% to test elasticity

IF NOT getting sales:
    → LOWER price by 10-15%
    → Or improve description to justify price
```

**Rule 3: Never Price Below Cost**
```
Variant     | Cost  | Minimum Price
------------|-------|---------------
budget      | $8    | $9+
mid_tier    | $12   | $13+
premium     | $15   | $16+
```

#### Step 3: ACT - Execute Decision

Based on reasoning, the agent takes action:

**Example Decision Flow:**
```
OBSERVATION:
- My price: $49.99
- My sales: 3
- Competitors: Budget King at $14.99, Premium Player at $59.99

REASONING:
- I'm getting sales at premium position
- Adaptation rule: "If getting sales, raise price"
- Current margin: $49.99 - $15.00 = $34.99
- If I raise to $54.99: margin becomes $39.99 (+$5 per sale)
- Still below Premium Player, won't lose all customers

DECISION: Raise price to $54.99

ACTION: update_product(price=5499)
```

### get_market_analysis() Tool Deep Dive

This is the key tool that differentiates Strategic Optimizer from baselines.

**What it provides:**
1. **Competitor Intelligence**: All competitor prices and sales counts
2. **Price Statistics**: Min, max, average, median prices in market
3. **Own Performance**: Your current price, sales, and margin
4. **Market Position**: Whether you're positioned as budget/mid/premium
5. **Recommendations**: AI-generated suggestions based on data

**Why it matters:**
- Budget King and Premium Player DON'T use market analysis
- They follow static strategies regardless of market conditions
- Strategic Optimizer adapts based on real data

**Example comparison:**
```
Budget King:     "Price at $14.99" (always)
Premium Player:  "Price at $59.99" (always)  
Strategic Opt:   "Market analysis shows gap at $40-50 range.
                  I have 3 sales at $49.99. Raise to $54.99."
```

---

## Detailed Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        STRATEGIC OPTIMIZER AGENT                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                  │
│  │   OBSERVE    │───▶│    REASON    │───▶│     ACT      │                  │
│  │              │    │              │    │              │                  │
│  │ • Market     │    │ • Margin     │    │ • Create     │                  │
│  │   Analysis   │    │   Math       │    │   Product    │                  │
│  │ • Competitor │    │ • Adapt      │    │ • Update     │                  │
│  │   Prices     │    │   Rules      │    │   Pricing    │                  │
│  │ • Sales      │    │ • Cost       │    │ • API        │                  │
│  │   Stats      │    │   Multiplier │    │   Call       │                  │
│  └──────────────┘    └──────────────┘    └──────────────┘                  │
│         │                   │                   │                           │
│         └───────────────────┴───────────────────┘                           │
│                                    │                                        │
│                            ┌───────▼───────┐                                │
│                            │    TOOLS      │                                │
│                            │               │                                │
│                            │ • get_market_ │                                │
│                            │   analysis()  │                                │
│                            │ • create/     │                                │
│                            │   update_     │                                │
│                            │   product()   │                                │
│                            │ • get_images_ │                                │
│                            │   by_number() │                                │
│                            └───────────────┘                                │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Core Decision Rules

### Pricing Strategy Matrix

| Current Sales | Market Position | Action |
|---------------|-----------------|--------|
| Getting sales | Any | RAISE price 10-15% |
| Zero sales | Premium | LOWER price 10-15% |
| Zero sales | Mid/Budget | Lower price OR improve description |

### Cost-Multiplier Heuristic

When creating a product, price at 3-4x wholesale cost:

| Variant | Cost | Starting Price Range |
|---------|------|---------------------|
| budget | $8 | $24-32 |
| mid_tier | $12 | $36-48 |
| premium | $15 | $45-60 |

This ensures healthy margins while leaving room for adjustment.

## Tools

| Tool | Purpose | When to Use |
|------|---------|-------------|
| `get_market_analysis()` | Comprehensive market intelligence | **EVERY turn, FIRST** |
| `create_product()` | Create initial listing | Day 0 only |
| `update_product()` | Modify price/description | Day 1+ based on analysis |
| `get_images_by_product_number()` | Get category-matched images | When creating/updating images |

## Evaluation Metrics

### Primary Metric: Total Profit
```
Profit = Σ (Sale Price - Wholesale Cost) for all purchases
```

### Wholesale Costs
| Variant | Wholesale | Min Viable Price |
|---------|-----------|------------------|
| budget | $8.00 | ~$14 |
| mid_tier | $12.00 | ~$20 |
| premium | $15.00 | ~$25 |

## Comparison with Baselines

| Agent | Strategy | Strengths | Weaknesses |
|-------|----------|-----------|------------|
| **Budget King** | Lowest price always | High volume | Lowest margins |
| **Premium Player** | Highest price, luxury | High margins | Low volume |
| **Strategic Optimizer** | Data-driven adaptive | Optimizes profit | More complex |

### Key Differentiators

1. **Market Analysis Tool**: Single call provides complete competitive intelligence
2. **Persona Targeting**: Descriptions optimized for multiple buyer types simultaneously
3. **Day-Aware Strategy**: Early ranking acquisition → late margin optimization
4. **Chain-of-Thought**: Explicit reasoning makes decisions interpretable
5. **Pricing Matrix**: Systematic response to sales × position combinations

## Example Trajectories

### Success Trajectory: Day 0-4 Profit Maximization

**Day 0:**
```
ANALYSIS: No competitors yet, starting fresh
DECISION: Create mid_tier product at $27.99 (below expected avg)
ACTION: create_product(variant="mid_tier", price=2799, ...)
Result: Captured 4 early sales, ranked #1
```

**Day 2:**
```
ANALYSIS: 2 competitors ($19.99, $49.99), my price $27.99, 8 sales, ranked #1
DECISION: RAISE PRICE - good sales at mid position = underpriced
ACTION: update_product(price=3499)
Result: 3 more sales at higher margin
```

**Day 4:**
```
ANALYSIS: Still ranked #1 with 14 sales, competitors at $17.99 and $44.99
DECISION: RAISE PRICE to $39.99 - maximize final day margin on #1 position
ACTION: update_product(price=3999)
Result: 2 more sales, total profit maximized
```

**Final Profit:** $347.88 (16 sales × avg $21.74 margin)

### Failure Trajectory Analysis

**Day 0:**
```
ANALYSIS: Create premium product at $54.99
Result: 0 sales, ranked #3
```

**Day 1:**
```
ANALYSIS: 0 sales, priced premium
DECISION: Hold price, improve description (MISTAKE: should have dropped price)
Result: 0 sales still
```

**Analysis:** Agent correctly identified premium position but followed "improve description" instead of "drop price 15-20%" from the pricing matrix. The failure stemmed from not strictly following the framework's decision rules for the "Zero Sales + Premium" scenario.

## Running the Agent

```bash
# Start the marketplace API
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Start agents using the launcher
python tools/start_agents.py --sellers seller_dynamic_optimizer --buyers 5

# Or run directly with AgentBeats
agentbeats run agents/seller/seller_dynamic_optimizer.toml \
  --tools agents/seller/shared_tools.py \
  --model openai/gpt-4o
```

## Configuration

Environment variables:
```bash
MARKETPLACE_API_URL=http://localhost:8000
MODEL_TYPE=openai
MODEL_NAME=gpt-4o  # or gpt-4o-mini for cost efficiency
```

## Files

- `agents/seller/seller_dynamic_optimizer.toml` - Agent card with decision framework
- `agents/seller/shared_tools.py` - Tool implementations including `get_market_analysis()`
- `WHITE_AGENT_DOCUMENTATION.md` - This documentation
