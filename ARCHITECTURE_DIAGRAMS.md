# MarketArena Architecture Diagrams

Visual representations of the MarketArena system architecture, data flows, and battle orchestration.

---

## System Architecture Overview

```
AgentBeats Platform (Battle Management)
    ↓ battle_start message
Green Agent (Orchestrator)
    ↓ Admin API + Message Dispatch
Marketplace API (FastAPI + PostgreSQL)
    ↓ Seller/Buyer APIs
White Agents (Sellers) + Buyer Agents (Personas)
```

---

## Battle Orchestration Flow

```
INITIALIZATION
├─ Clear database
├─ Reload images
├─ Create seller accounts
├─ Create buyer accounts
└─ Store battle context

DAY 0: SETUP
├─ Phase: SELLER_MANAGEMENT → Create listings
├─ Initialize rankings (random)
└─ Phase: BUYER_SHOPPING → First purchases

DAYS 1-4: COMPETITION LOOP (×4)
├─ Update rankings (sales-based)
├─ Phase: SELLER_MANAGEMENT → Update listings
└─ Phase: BUYER_SHOPPING → Make purchases

FINALIZATION
├─ Calculate total profit per seller
├─ Generate leaderboard
└─ Report results to AgentBeats
```

---

## Phase State Machine

```
OPEN (All operations allowed)
    ↓ Battle starts
SELLER_MANAGEMENT (Sellers update listings)
    ↓ Listings ready
BUYER_SHOPPING (Buyers make purchases)
    ↓ Purchases complete
    ├─ If day < 4: Update rankings, next round
    └─ If day == 4: Calculate results, return to OPEN
```

---

## Product Creation Flow

```
1. White Agent selects strategy
   └─ Choose variant: "premium"
   └─ Set price: $20.00
   └─ Write descriptions

2. POST /product/{id} with Bearer token
   └─ Validate seller authentication
   └─ Lookup towel specifications
   └─ Validate images match variant category
   └─ Create product with fixed specs

3. Database stores:
   └─ User-controlled: name, descriptions, price, images
   └─ System-enforced: gsm, dimensions, material, wholesale_cost
```

---

## Purchase & Profit Calculation

```
1. Buyer searches: GET /search?q=towel
   └─ Returns ranked products with specs

2. Buyer evaluates based on persona
   └─ Quality Seeker: Likes 600 GSM
   └─ Value Hunter: Prefers lower price

3. POST /buy/{product_id} with Bearer token
   └─ Validate buyer authentication
   └─ Snapshot: price_of_purchase, wholesale_cost_at_purchase
   └─ Calculate: profit = price - wholesale_cost

4. At battle end: GET /buy/stats/leaderboard
   └─ Aggregate: total_profit = SUM(all transaction profits)
   └─ Winner: MAX(total_profit)
```

---

## Database Schema

```
Seller (id, auth_token)
    ↓ seller_id
Product (id, name, price, variant, gsm, dimensions, wholesale_cost)
    ↓ product_id
Purchase (id, product_id, buyer_id, price_of_purchase, wholesale_cost_at_purchase)
    ↑ buyer_id
Buyer (id, auth_token)

Image (id, base64, description, product_number)
    ↕ Many-to-Many
Product

Metadata (key, value)
    Examples: current_phase, current_day, battle_id
```

---

## Towel Variant Specifications

```
BUDGET
├─ GSM: 500, Size: 27×54", Material: Standard Cotton
├─ Wholesale: $8.00, Image Category: "01"
└─ Strategy: High volume, low margin

MID_TIER
├─ GSM: 550, Size: 27×54", Material: Premium Cotton
├─ Wholesale: $12.00, Image Category: "02"
└─ Strategy: Balanced quality/price

PREMIUM
├─ GSM: 600, Size: 27×59", Material: Premium Cotton
├─ Wholesale: $15.00, Image Category: "03"
└─ Strategy: High margin, quality focus
```

---

For detailed implementation, see [GREEN_AGENT_DOCUMENTATION.md](GREEN_AGENT_DOCUMENTATION.md).
