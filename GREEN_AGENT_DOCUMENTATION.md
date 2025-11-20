# MarketArena Green Agent Documentation

## Executive Summary

The **Green Agent** is the central orchestrator of the MarketArena benchmark, a simulated e-commerce marketplace designed to evaluate AI agents' ability to maximize profit through strategic product optimization in competitive settings. This document explains the conceptual design, implementation architecture, and the economic modeling principles behind our evaluation framework.

---

## Table of Contents

1. [Conceptual Overview](#conceptual-overview)
2. [Core Design Principles](#core-design-principles)
3. [Implementation Architecture](#implementation-architecture)
4. [Economic Modeling](#economic-modeling)
5. [Battle Orchestration System](#battle-orchestration-system)
6. [Evaluation Methodology](#evaluation-methodology)
7. [Design Evolution](#design-evolution)
8. [Technical Implementation Details](#technical-implementation-details)

---

## Conceptual Overview

### What is the Green Agent?

The Green Agent is the **evaluation orchestrator** that manages the complete lifecycle of marketplace battle simulations. Unlike traditional benchmarks that evaluate buyer-side agent behavior (WebMall, LMAgent) or abstract game-theoretic scenarios (ALYMPICS), MarketArena specifically assesses **seller-side profit optimization** in a practical e-commerce context.

### The Core Idea

We simulate a realistic e-commerce marketplace where:

- **White Agents (Sellers)**: Compete by optimizing product listings (pricing, descriptions, images)
- **Buyer Agents**: Make purchasing decisions based on diverse consumer personas
- **Green Agent**: Orchestrates the simulation, enforces marketplace rules, and evaluates performance

The Green Agent creates an environment where sellers must balance multiple competing objectives:
- **Pricing strategy** vs. **cost structure**
- **Quality positioning** vs. **price competitiveness**
- **Market segment targeting** vs. **broad appeal**
- **Short-term sales** vs. **long-term profitability**

---

## Core Design Principles

### 1. Profit-Based Evaluation (Not Revenue)

**Key Insight**: We measure **total profit** (revenue minus costs) rather than revenue alone.

**Rationale**: 
- Prevents exploitation strategies (e.g., selling premium products at budget prices)
- Forces agents to balance pricing with their cost structure
- Mirrors real-world business constraints
- Creates natural economic boundaries without arbitrary price caps

**Implementation**:
```python
profit = revenue - wholesale_cost
# Example: Selling a $15 wholesale premium towel for $20 = $5 profit
# Example: Selling a $15 wholesale premium towel for $10 = -$5 loss
```

### 2. Heterogeneous Demand Through Consumer Personas

**Key Insight**: Diverse customer preferences prevent convergence on a single dominant strategy.

**Rationale**:
- Real marketplaces serve multiple customer segments simultaneously
- Forces agents to make strategic trade-offs rather than finding one "optimal" solution
- Tests adaptability to varying market conditions
- Grounded in empirically-validated consumer behavior theory (Sproles & Kendall CSI)

**Five Persona Types**:
1. **Perfectionist Quality Seeker**: Prioritizes specifications (GSM, dimensions, materials)
2. **Brand Conscious Price Perceiver**: Associates higher prices with quality
3. **Recreational Hedonistic Shopper**: Emphasizes visual appeal and imagery
4. **Price-Conscious Value Hunter**: Focuses on competitive pricing
5. **Confused by Overchoice**: Relies on simplified heuristics (ranking position)

### 3. Three-Tier Product Differentiation

**Key Insight**: Fixed product variants with distinct cost structures create strategic positioning choices.

**Product Variants**:

| Variant | GSM | Dimensions | Material | Wholesale Cost | Positioning |
|---------|-----|------------|----------|----------------|-------------|
| **Budget** | 500 | 27×54" | Standard Cotton | $8.00 | Price-performance |
| **Mid-Tier** | 550 | 27×54" | Premium Cotton | $12.00 | Quality at standard size |
| **Premium** | 600 | 27×59" | Premium Cotton | $15.00 | Luxury sizing + materials |

**Strategic Implications**:
- Budget: Lower margins, higher volume potential
- Mid-Tier: Balanced positioning for mainstream market
- Premium: Higher margins, requires targeting quality-focused buyers

### 4. Dynamic Ranking Algorithm

**Key Insight**: Product visibility drives sales, creating feedback loops that reward both quality and performance.

**Ranking Factors**:
- **Sales velocity** (with recency weighting): Rewards recent performance
- **Price competitiveness**: Relative to category median
- **Listing quality**: Description completeness and specification detail
- **Time on market**: Slight boost for recently listed products

**Purpose**: Creates realistic marketplace dynamics where early success compounds, but quality listings can break through.

---

## Implementation Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                      GREEN AGENT                            │
│  (Battle Orchestrator - agents/green_agent/green_agent_tools.py)│
└─────────────────────────────────────────────────────────────┘
                            │
                            │ orchestrates
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   MARKETPLACE API                           │
│              (FastAPI Backend - app/)                       │
│  • Phase Management (seller/buyer/open)                     │
│  • Product CRUD with authentication                         │
│  • Search with ranking                                      │
│  • Purchase tracking with profit calculation                │
│  • Admin endpoints for orchestration                        │
└─────────────────────────────────────────────────────────────┘
                            │
                ┌───────────┴───────────┐
                ▼                       ▼
┌───────────────────────────┐  ┌───────────────────────────┐
│   WHITE AGENTS (Sellers)  │  │   BUYER AGENTS            │
│  agents/seller/           │  │   agents/buyer/           │
│  • Create products        │  │   • Search products       │
│  • Update listings        │  │   • Evaluate options      │
│  • Optimize pricing       │  │   • Make purchases        │
│  • Select images          │  │   • Follow persona logic  │
└───────────────────────────┘  └───────────────────────────┘
```

### Technology Stack

- **Backend**: FastAPI with PostgreSQL database
- **ORM**: SQLAlchemy with Alembic migrations
- **Agent Framework**: AgentBeats for battle orchestration
- **Authentication**: Token-based (Bearer tokens)
- **Phase Management**: State machine controlling marketplace operations

---

## Economic Modeling

### Cost Structure

We implemented a **realistic wholesale cost model** based on Amazon marketplace analysis:

```python
TOWEL_VARIANTS = {
    TowelVariant.BUDGET: TowelSpecification(
        gsm=500,
        wholesale_cost_cents=800  # $8.00
    ),
    TowelVariant.MID_TIER: TowelSpecification(
        gsm=550,
        wholesale_cost_cents=1200  # $12.00
    ),
    TowelVariant.PREMIUM: TowelSpecification(
        gsm=600,
        wholesale_cost_cents=1500  # $15.00
    )
}
```

**Wholesale-to-Retail Ratios**: Derived from industry-standard markups observed in real Amazon listings.

### Profit Calculation

```python
# For each purchase:
profit = price_of_purchase - wholesale_cost_at_purchase

# Total seller score:
total_profit = sum(profit for all purchases)
```

**Key Properties**:
- Pricing below cost → negative profit per sale
- Pricing far above market → zero sales, zero profit
- Natural economic constraints without arbitrary bounds

### Market Dynamics

**Feedback Loops**:
1. **Sales → Ranking**: More sales improve visibility
2. **Ranking → Visibility**: Better ranking increases exposure
3. **Visibility → Sales**: Higher exposure drives more purchases

**Balancing Mechanisms**:
- Price competitiveness factor in ranking
- Listing quality signals
- Diverse buyer personas with different preferences

---

## Battle Orchestration System

### Battle Lifecycle

The Green Agent manages a **5-day simulation** with distinct phases:

```
┌─────────────────────────────────────────────────────────────┐
│ INITIALIZATION                                              │
│  • Clear database                                           │
│  • Reload product images                                    │
│  • Create seller accounts (white agents)                    │
│  • Create buyer accounts (persona agents)                   │
│  • Store battle context in metadata                         │
└─────────────────────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ DAY 0: Initial Setup                                        │
│  Phase: SELLER_MANAGEMENT                                   │
│   → Sellers create initial product listings                 │
│  Phase: OPEN                                                │
│   → Initialize rankings (random)                            │
│  Phase: BUYER_SHOPPING                                      │
│   → Buyers make first purchases                             │
└─────────────────────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ DAYS 1-4: Competition Loop (repeated 4 times)              │
│  • Set marketplace day counter                              │
│  • Update rankings based on sales performance               │
│  Phase: SELLER_MANAGEMENT                                   │
│   → Sellers update listings (price, description, images)    │
│  Phase: BUYER_SHOPPING                                      │
│   → Buyers make purchases based on updated listings         │
└─────────────────────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ FINALIZATION                                                │
│  • Calculate total profit per seller                        │
│  • Generate leaderboard                                     │
│  • Report results to AgentBeats                             │
│  • Reset marketplace phase to OPEN                          │
└─────────────────────────────────────────────────────────────┘
```

### Phase Management

The Green Agent controls marketplace state through a **phase state machine**:

```python
class Phase(str, Enum):
    SELLER_MANAGEMENT = "seller_management"  # Sellers can update listings
    BUYER_SHOPPING = "buyer_shopping"        # Buyers can make purchases
    OPEN = "open"                            # All operations allowed
```

**Enforcement**: The FastAPI backend validates operations against the current phase, preventing out-of-turn actions.

**Implementation** (`app/services/phase_manager.py`):
```python
def ensure_phase(db: Session, allowed_phases: Iterable[Phase]) -> Phase:
    """Ensure the active phase is one of the allowed phases."""
    current_phase = get_current_phase(db)
    
    if current_phase == Phase.OPEN or current_phase in allowed_set:
        return current_phase
    
    raise HTTPException(
        status_code=403,
        detail=f"Operation not allowed during phase '{current_phase.value}'"
    )
```

### Agent Communication Protocol

The Green Agent communicates with white agents through **message dispatch**:

```python
async def _send_prompts_to_agents(
    agents: list, 
    prompt_template: str, 
    log_message: str, 
    timeout_seconds: int
):
    """Send templated prompts to agents with their credentials."""
    messages = [
        prompt_template.format(id=agent.id, token=agent.token) 
        for agent in agents
    ]
    target_urls = [agent.url for agent in agents]
    
    # Dispatch messages to all agents in parallel
    await send_messages_to_agents(target_urls, messages, timeout_seconds)
```

**Example Prompt** (Seller Update):
```
Call /updateProduct to update your product.

Your seller ID: {id}
Your auth token: {token}

Use the auth token in the Authorization header as "Bearer {token}" when making API calls.

Response format:
{
    "product_id": "123"
}
```

---

## Evaluation Methodology

### Primary Metric: Total Profit

```python
async def report_leaderboard():
    """Calculate and report final rankings based on total profit."""
    
    # Fetch leaderboard data from API
    response = requests.get(f"{api_url}/buy/stats/leaderboard")
    leaderboard_data = response.json()
    
    # Calculate winner
    winner_id = None
    winner_score = 0
    
    for entry in leaderboard_data:
        seller_id = entry["seller_id"]
        profit = entry["total_profit_cents"]  # Revenue - costs
        purchase_count = entry["purchase_count"]
        
        if profit > winner_score:
            winner_score = profit
            winner_id = seller_id
    
    # Report to AgentBeats
    record_battle_result(
        battle_context,
        f"Winner: {winner_name} with ${winner_score / 100.0:.2f} total profit",
        winner_name,
        result_detail
    )
```

### Leaderboard API Implementation

**Endpoint**: `GET /buy/stats/leaderboard`

**Query** (`app/routers/purchases.py`):
```python
results = (
    db.query(
        Seller.id,
        func.count(Purchase.id).label("purchase_count"),
        func.coalesce(
            func.sum(Purchase.price_of_purchase - Purchase.wholesale_cost_at_purchase),
            0
        ).label("total_profit_cents")
    )
    .outerjoin(Product, Product.seller_id == Seller.id)
    .outerjoin(Purchase, Purchase.product_id == Product.id)
    .group_by(Seller.id)
    .order_by(total_profit_cents.desc())
    .all()
)
```

**Response Format**:
```json
[
    {
        "seller_id": "seller-123",
        "purchase_count": 45,
        "total_profit_cents": 28000,
        "total_profit_dollars": 280.00
    },
    ...
]
```

### Ranking Algorithm

**Endpoint**: `POST /rankings/update-by-sales`

**Implementation** (`app/routers/rankings.py`):
```python
def update_rankings_by_sales(db: Session = Depends(get_db)):
    """Update product rankings based on sales performance."""
    
    # Count purchases per product
    purchase_counts = (
        db.query(
            Purchase.product_id,
            func.count(Purchase.id).label("purchase_count")
        )
        .group_by(Purchase.product_id)
        .all()
    )
    
    # Sort by sales count (descending)
    sorted_products = sorted(
        products_with_sales, 
        key=lambda x: x["sales_count"], 
        reverse=True
    )
    
    # Assign rankings: rank 1 = most sales
    for rank, item in enumerate(sorted_products, start=1):
        item["product"].ranking = rank
    
    db.commit()
```

**Current Implementation**: Simple sales-based ranking (most sales = rank 1).

**Planned Enhancements**: Multi-factor weighting including price competitiveness, listing quality, and recency.

---

## Design Evolution

### Major Design Changes

#### 1. Revenue → Profit Metric (Critical Fix)

**Original Design**: Evaluated agents by total revenue.

**Problem Discovered**: White agents could exploit by selecting premium variants ($15 wholesale) and pricing at budget levels ($10), generating high revenue while destroying profitability.

**Solution**: Changed primary metric to **total profit** (revenue - costs).

**Impact**:
- Forces realistic pricing strategies
- Eliminates exploitation
- Better reflects real-world business objectives

#### 2. Five Categories → Single Category (Scope Refinement)

**Original Design**: Multiple product categories (towels, sheets, pillows, etc.).

**Problem**: Managing multiple categories diluted evaluation focus without adding strategic depth.

**Solution**: Concentrated on **bath towels only** with three quality variants.

**Benefits**:
- Clearer quality differentiation (GSM, dimensions)
- Focused evaluation of pricing and positioning strategies
- Maintained implementation feasibility within timeline

#### 3. Planned Enhancements Not Yet Implemented

**Scam Detection Filter** (Planned):
- Detect false claims in descriptions contradicting fixed specifications
- Penalize through ranking suppression
- Model real-world platform moderation

**Advanced Ranking Algorithm** (Planned):
- Multi-factor weighting (sales velocity, price competitiveness, listing quality)
- Recency weighting for sales
- Time-on-market boost for new listings

---

## Technical Implementation Details

### Database Schema

**Core Tables**:

```sql
-- Sellers (White Agents)
CREATE TABLE sellers (
    id VARCHAR PRIMARY KEY,
    auth_token VARCHAR UNIQUE NOT NULL
);

-- Products (Seller Listings)
CREATE TABLE products (
    id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    short_description VARCHAR NOT NULL,
    long_description VARCHAR NOT NULL,
    price_in_cent INTEGER NOT NULL,
    ranking INTEGER,
    
    -- Towel specifications
    towel_variant VARCHAR NOT NULL,  -- 'budget', 'mid_tier', 'premium'
    gsm INTEGER NOT NULL,
    width_inches INTEGER NOT NULL,
    length_inches INTEGER NOT NULL,
    material VARCHAR NOT NULL,
    wholesale_cost_cents INTEGER NOT NULL,
    
    seller_id VARCHAR REFERENCES sellers(id)
);

-- Purchases (Transaction History)
CREATE TABLE purchases (
    id VARCHAR PRIMARY KEY,
    product_id VARCHAR REFERENCES products(id),
    buyer_id VARCHAR REFERENCES buyers(id),
    price_of_purchase INTEGER NOT NULL,
    wholesale_cost_at_purchase INTEGER NOT NULL,
    purchased_at TIMESTAMP DEFAULT NOW()
);

-- Images (Product Photography)
CREATE TABLE images (
    id VARCHAR PRIMARY KEY,
    image_base64 TEXT NOT NULL,
    image_description TEXT,
    product_number VARCHAR  -- '01'=budget, '02'=mid, '03'=premium
);

-- Metadata (Battle Context & Configuration)
CREATE TABLE metadata (
    key VARCHAR PRIMARY KEY,
    value VARCHAR NOT NULL
);
```

### Authentication Flow

**Seller Creation**:
```python
# Green Agent creates seller
response = requests.post(
    f"{api_url}/createSeller",
    headers={"X-Admin-Key": admin_api_key}
)

seller_data = response.json()
# Returns: {"id": "seller-123", "auth_token": "abc...xyz"}
```

**Seller API Usage**:
```python
# Seller creates product
response = requests.post(
    f"{api_url}/product/{product_id}",
    json=payload,
    headers={"Authorization": f"Bearer {auth_token}"}
)
```

**Authorization Enforcement** (`app/routers/products.py`):
```python
def verify_seller_token(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
) -> str:
    """Verify seller authentication token."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    
    token = authorization.split(" ")[1]
    seller = db.query(Seller).filter(Seller.auth_token == token).first()
    
    if not seller:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    
    return seller.id
```

### Product Variant Enforcement

**Specification Lookup** (`app/models/towel_specs.py`):
```python
TOWEL_VARIANTS = {
    TowelVariant.BUDGET: TowelSpecification(
        variant=TowelVariant.BUDGET,
        gsm=500,
        width_inches=27,
        length_inches=54,
        material="Standard Cotton",
        wholesale_cost_cents=800
    ),
    # ... mid_tier and premium
}

def get_towel_specification(variant: TowelVariant) -> TowelSpecification:
    """Get the specification for a given towel variant."""
    return TOWEL_VARIANTS[variant]
```

**Product Creation with Variant** (`app/routers/products.py`):
```python
@router.post("/product/{product_id}")
def create_product(
    product_id: str,
    product_data: ProductCreate,
    seller_id: str = Depends(verify_seller_token),
    db: Session = Depends(get_db)
):
    # Get towel specifications
    towel_spec = get_towel_specification(product_data.towel_variant)
    
    # Create product with fixed specifications
    product = Product(
        id=product_id,
        name=product_data.name,
        price_in_cent=product_data.price,
        towel_variant=towel_spec.variant,
        gsm=towel_spec.gsm,
        width_inches=towel_spec.width_inches,
        length_inches=towel_spec.length_inches,
        material=towel_spec.material,
        wholesale_cost_cents=towel_spec.wholesale_cost_cents,
        seller_id=seller_id
    )
    
    db.add(product)
    db.commit()
```

**Key Property**: Sellers specify variant, system enforces specifications and costs.

### Image Management

**Image-Variant Validation**:
```python
# Images are categorized by product_number
TOWEL_VARIANT_TO_PRODUCT_NUMBER = {
    TowelVariant.BUDGET: "01",
    TowelVariant.MID_TIER: "02",
    TowelVariant.PREMIUM: "03"
}

# API validates image category matches product variant
def validate_images_match_variant(image_ids, towel_variant, db):
    """Ensure all images match the product's variant category."""
    expected_product_number = get_product_number_for_variant(towel_variant)
    
    for image_id in image_ids:
        image = db.query(Image).filter(Image.id == image_id).first()
        if image.product_number != expected_product_number:
            raise HTTPException(
                status_code=400,
                detail=f"Image {image_id} category mismatch"
            )
```

**Purpose**: Prevents sellers from using premium imagery with budget products.

### Buyer Persona Implementation

**Persona Configuration** (`agents/buyer/persona_quality_seeker.toml`):
```toml
name = "Perfectionist Quality Seeker"
description = '''
ROLE: You are a quality-focused shopper who researches purchases carefully.

DECISION CRITERIA:
- Detailed technical specs > vague marketing language
- Specific quality mentions (GSM, dimensions, materials) heavily influence you
- You'll pay more if descriptions demonstrate genuine quality
- Bestseller status matters less than specification details
'''

[[skills]]
id = "search_products"
name = "Search Products"
description = "Search marketplace for products to thoroughly research quality options"

[[skills]]
id = "purchase_product"
name = "Purchase Product"
description = "Purchase the product with the best quality indicators and specifications"
```

**Persona Diversity**:
- Each persona has distinct decision weights
- Prompts encode CSI-based preferences
- Tools guide persona-appropriate behavior

---

## References

**Sproles, G.B., & Kendall, E.L. (1986)**. A methodology for profiling consumers' decision-making styles. *Journal of Consumer Affairs, 20*(2), 267-279.

**AgentBeats Platform**: https://agentbeats.com

**Repository**: https://github.com/paulburkhardt/Rede_Labs

**DeepWiki Documentation**: https://deepwiki.com/paulburkhardt/Rede_Labs

---

## Conclusion

The MarketArena Green Agent implements a rigorous evaluation framework for strategic business agents operating in competitive e-commerce environments. By combining profit-based evaluation, empirically-grounded consumer heterogeneity, and realistic economic constraints, we create a benchmark that:

1. **Prevents exploitation** through economic self-regulation
2. **Tests adaptability** through diverse customer preferences
3. **Rewards strategy** over simple optimization
4. **Models reality** through grounded consumer behavior
5. **Enables research** into emergent competitive dynamics

The implementation demonstrates that effective agent evaluation requires not just measuring performance, but creating environments where the right strategies naturally emerge from realistic constraints and heterogeneous objectives.
