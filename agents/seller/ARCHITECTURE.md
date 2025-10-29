# Seller Agent Architecture

## 🏗️ System Design: Environment vs. Agent Separation

This document explains the critical architectural separation between the **environment configuration** (what the platform provides) and the **agent implementation** (what participants control).

---

## 📋 Overview

The marketplace is built on a clear separation of concerns:

1. **Environment Layer** - Fixed by the platform (you)
2. **Agent Layer** - Implemented by participants (competition entrants)

This separation ensures:
- ✅ Fair competition (everyone has access to same products)
- ✅ Realistic marketplace (fixed wholesale costs simulate real business)
- ✅ Easy testing (your dummy agents demonstrate what participants will build)
- ✅ Clear rules (participants know what they can/cannot change)

---

## 🌍 Environment Layer (Platform-Controlled)

### What the Platform Provides

**File**: `towel_products.py`

**Purpose**: Defines the fixed product variants available in the marketplace.

### Three Towel Variants

```python
BUDGET Towel:
- GSM: 500 (fabric density)
- Size: 27" x 54"
- Material: Standard Cotton
- Wholesale Cost: $8.00
- Who buys: Price-conscious customers

MID_TIER Towel:
- GSM: 600 (fabric density)
- Size: 27" x 54"  
- Material: Premium Cotton
- Wholesale Cost: $12.00
- Who buys: Balance seekers

PREMIUM Towel:
- GSM: 600 (fabric density)
- Size: 27" x 59" (extra large!)
- Material: Premium Cotton XL
- Wholesale Cost: $15.00
- Who buys: Luxury/quality seekers
```

### What Cannot Be Changed

Participants **CANNOT** modify:
- ❌ Physical specifications (GSM, size, material)
- ❌ Wholesale costs
- ❌ Create custom product variants
- ❌ Sell below wholesale cost

### Key Functions

```python
get_towel_spec(variant)           # Get specs for a variant
get_minimum_price(variant)         # Get wholesale cost (price floor)
validate_price(variant, price)     # Validate price is above wholesale
calculate_suggested_retail(...)    # Helper for markup calculations
```

---

## 🤖 Agent Layer (Participant-Controlled)

### What Participants Control

Participants implement seller agents that can:

1. **Choose Product Variant**
   - Select which towel to sell (Budget, Mid-Tier, or Premium)
   - Match variant to their strategy

2. **Set Pricing Strategy**
   - Determine markup over wholesale cost
   - Must be ≥ wholesale cost
   - Can adjust dynamically based on performance

3. **Create Marketing Copy**
   - Product names
   - Short descriptions
   - Long descriptions
   - Product images

4. **Optimize Performance**
   - Analyze market conditions
   - Respond to competitor pricing
   - Update listings based on sales data

### Base Class Architecture

**File**: `seller_agent_base.py`

All seller agents inherit from `SellerAgent` and must implement:

```python
class SellerAgent(ABC):
    @abstractmethod
    def select_product_and_create_listing(self) -> tuple[TowelVariant, Dict]:
        """
        1. Choose which variant to sell
        2. Create marketing materials
        3. Set retail price (>= wholesale)
        4. Choose product image
        """
        pass
    
    @abstractmethod
    def update_listing_strategy(self, sales_stats, market_data) -> Dict:
        """
        Adapt strategy based on:
        - Sales performance
        - Competitor analysis
        - Market position
        """
        pass
    
    @abstractmethod
    def determine_price(self, wholesale_cost, market_data) -> int:
        """
        Calculate retail price based on:
        - Wholesale cost (must be above this)
        - Market conditions
        - Strategy (budget/premium/dynamic)
        """
        pass
```

---

## 🎯 Three Dummy Agent Strategies

These demonstrate what participants will build:

### 1. Budget King (Budget Variant)

**Variant**: BUDGET  
**Wholesale**: $8.00  
**Strategy**: Low markup, undercut competitors

```python
Pricing Logic:
- Base Markup: 25% ($10.00 retail)
- Min Markup: 10% ($8.80 retail - floor price)
- Competitive: 12% below cheapest competitor
- Profit Margin: $2.00 - $8.00 per sale

Example:
Wholesale: $8.00
Initial Price: $10.00 (25% markup)
If competitor at $12.00 → Drop to $10.56 (12% under)
Never below: $8.80 (10% profit margin)
```

### 2. Premium Player (Premium Variant)

**Variant**: PREMIUM  
**Wholesale**: $15.00  
**Strategy**: High markup, luxury positioning

```python
Pricing Logic:
- Base Markup: 150% ($37.50 retail)
- Min Markup: 100% ($30.00 retail - floor price)
- Positioning: 25% above market average
- Profit Margin: $15.00 - $30.00 per sale

Example:
Wholesale: $15.00
Initial Price: $37.50 (150% markup)
Market avg $25.00 → Price at $31.25 (25% above)
Never below: $30.00 (100% profit margin)
```

### 3. Dynamic Optimizer (Mid-Tier Variant)

**Variant**: MID_TIER  
**Wholesale**: $12.00  
**Strategy**: Adaptive markup, data-driven

```python
Pricing Logic:
- Base Markup: 75% ($21.00 retail)
- Min Markup: 30% ($15.60 retail - floor price)
- Max Markup: 150% ($30.00 retail - cap)
- Adaptive: Adjusts based on sales velocity
- Profit Margin: $3.60 - $18.00 per sale

Example:
Wholesale: $12.00
Initial Price: $21.00 (75% markup)
No sales + expensive → Drop to $16.80
Good sales + cheap → Raise to $23.52
Always above: $15.60 (30% profit margin)
```

---

## 🔄 Complete Workflow

### Initial Setup Phase

```
1. Environment provides 3 towel variants
   ├─ BUDGET: $8.00 wholesale
   ├─ MID_TIER: $12.00 wholesale  
   └─ PREMIUM: $15.00 wholesale

2. Seller agents register
   ├─ Budget King chooses BUDGET variant
   ├─ Premium Player chooses PREMIUM variant
   └─ Dynamic Optimizer chooses MID_TIER variant

3. Each agent creates listing
   ├─ Selects variant
   ├─ Sets initial price (markup strategy)
   ├─ Creates marketing copy
   └─ API validates price >= wholesale
```

### Market Cycle Phase

```
Day 1: Initial Listings
├─ Budget King: BUDGET at $10.00 (25% markup)
├─ Premium Player: PREMIUM at $37.50 (150% markup)
└─ Dynamic Optimizer: MID_TIER at $21.00 (75% markup)

Buyers Purchase
├─ Price-conscious → Budget King ($10.00)
├─ Quality-seeker → Premium Player ($37.50)
└─ Balanced → Dynamic Optimizer ($21.00)

Day 2: First Update
├─ Budget King analyzes sales
│   └─ If no sales → Drop to $8.80 (min margin)
├─ Premium Player maintains position
│   └─ Updates messaging with social proof
└─ Dynamic Optimizer adapts
    └─ Adjusts price based on performance

Day N: Continuous Optimization
└─ Agents compete, adapt, optimize...
```

---

## 💰 Profit Margin Examples

### Scenario: All 3 Agents Sell 1 Towel Each

```
Budget King:
├─ Sells BUDGET at $10.00
├─ Cost: $8.00
├─ Profit: $2.00 (25% margin)
└─ Revenue: $10.00

Premium Player:
├─ Sells PREMIUM at $37.50
├─ Cost: $15.00
├─ Profit: $22.50 (150% margin)
└─ Revenue: $37.50

Dynamic Optimizer:
├─ Sells MID_TIER at $21.00
├─ Cost: $12.00
├─ Profit: $9.00 (75% margin)
└─ Revenue: $21.00

Total Revenue Rankings:
1st: Premium Player ($37.50)
2nd: Dynamic Optimizer ($21.00)
3rd: Budget King ($10.00)
```

### Scenario: Budget King Sells 5, Others Sell 1

```
Budget King:
├─ Sells 5x BUDGET at $10.00 each
├─ Cost: 5 × $8.00 = $40.00
├─ Profit: 5 × $2.00 = $10.00
└─ Revenue: $50.00 ✨ WINNER

Premium Player:
├─ Sells 1x PREMIUM at $37.50
├─ Cost: $15.00
├─ Profit: $22.50
└─ Revenue: $37.50

Dynamic Optimizer:
├─ Sells 1x MID_TIER at $21.00
├─ Cost: $12.00
├─ Profit: $9.00
└─ Revenue: $21.00
```

**Key Insight**: Volume can beat margin! The Budget King wins by selling more units, even with lower profit per sale.

---

## 🎓 For Competition Participants

### What You'll Implement

1. **Variant Selection Logic**
   ```python
   def select_product_and_create_listing(self):
       # Choose variant based on your strategy
       variant = TowelVariant.BUDGET  # or MID_TIER or PREMIUM
       
       # Set your retail price
       price = self.calculate_my_price(variant)
       
       # Create your marketing
       marketing = self.create_marketing_copy(variant)
       
       return variant, marketing
   ```

2. **Pricing Strategy**
   ```python
   def determine_price(self, wholesale_cost, market_data):
       # Your logic here
       # Must return price >= wholesale_cost
       
       if self.aggressive_strategy:
           markup = 20  # 20% markup
       else:
           markup = 100  # 100% markup
           
       return int(wholesale_cost * (1 + markup/100))
   ```

3. **Adaptive Updates**
   ```python
   def update_listing_strategy(self, sales_stats, market_data):
       updates = {}
       
       # Analyze performance
       if sales_stats['total_sales'] == 0:
           # Drop price?
           updates['price'] = lower_price
       else:
           # Raise price?
           updates['price'] = higher_price
           
       return updates
   ```

### Rules & Constraints

✅ **You CAN**:
- Choose any towel variant
- Set any price ≥ wholesale cost
- Create any marketing copy
- Update price/copy based on performance
- Analyze competitor behavior
- Use any decision-making algorithm

❌ **You CANNOT**:
- Sell below wholesale cost
- Modify product specifications
- Access competitor's internal data
- Create custom product variants

---

## 🧪 Testing Your Environment

### Verify Fixed Costs

```python
from agents.seller.towel_products import get_variant_summary

print(get_variant_summary())
```

Output shows all 3 variants with fixed specs.

### Test Dummy Agents

```python
from agents.seller import BudgetKingSeller, PremiumPlayerSeller

# Create agents
budget = BudgetKingSeller()
premium = PremiumPlayerSeller()

# They select different variants
budget_variant = budget.variant  # BUDGET
premium_variant = premium.variant  # PREMIUM

# They have different wholesale costs
budget_cost = budget.spec.wholesale_cost_cents  # 800 cents
premium_cost = premium.spec.wholesale_cost_cents  # 1500 cents

# They set different markups
budget.base_markup_percent  # 25%
premium.base_markup_percent  # 150%
```

---

## 📊 Competition Metrics

### Leaderboard Calculation

```python
Winner = Seller with highest Total Revenue

Total Revenue = Σ(retail_price × quantity_sold)

Example:
Seller A: 10 sales × $10.00 = $100.00
Seller B: 3 sales × $35.00 = $105.00 ← WINNER
```

**Note**: The competition ranks by revenue, not profit. This incentivizes finding the optimal balance between volume and margin.

---

## 🔍 Key Takeaways

1. **Environment** = Fixed product variants with wholesale costs
2. **Agents** = Choose variant, set markup, create marketing
3. **Competition** = Optimize total revenue over multiple days
4. **Strategy** = Balance between margin and volume
5. **Testing** = Your 3 dummy agents demonstrate the framework

This architecture ensures:
- Fair competition (same constraints for all)
- Realistic business simulation (must cover costs)
- Strategic depth (many ways to win)
- Easy to test (dummy agents prove it works)

---

## 🚀 Next Steps

1. **Test the environment**: Run `python towel_products.py`
2. **Test dummy agents**: Run `python test_seller_agents.py`
3. **Verify separation**: Participants can only control agents, not environment
4. **Document for participants**: Create competition rules based on this architecture

The system is now ready for competition deployment! 🎉

