# Loss-Leader Strategy: 50% Floor Pricing

## ✅ What Changed

**Previous**: Agents could only price at or above wholesale cost  
**Now**: Agents can price down to 50% of wholesale cost (loss-leader strategy)

### New Price Floors

| Variant | Wholesale | Old Floor | **New Floor** | Max Loss/Sale |
|---------|-----------|-----------|---------------|---------------|
| **BUDGET** | $8.00 | $8.00 | **$4.00** | **$4.00** |
| **MID_TIER** | $12.00 | $12.00 | **$6.00** | **$6.00** |
| **PREMIUM** | $15.00 | $15.00 | **$7.50** | **$7.50** |

---

## 🎯 Strategic Implications

### Loss-Leader Strategy (Now Possible!)

```
Phase 1: Market Share Grab
Day 1-2: Price at $6.00 (below $8.00 cost)
        Loss: $2.00 per sale
        Volume: 40 sales
        Total Loss: -$80.00
        Result: #1 marketplace ranking

Phase 2: Monetization
Day 3-5: Raise price to $14.00 (above cost)
        Profit: $6.00 per sale
        Volume: 30 sales (high ranking drives traffic)
        Total Profit: +$180.00

Final Result:
Total Sales: 70
Total Profit: $100.00 ✅ WINNER
```

### Conservative Strategy (Still Viable)

```
Steady Approach
Day 1-5: Price at $10.00 
        Profit: $2.00 per sale
        Volume: 35 sales (consistent)
        
Final Result:
Total Sales: 35
Total Profit: $70.00
```

### Failed Loss-Leader (Risk!)

```
Over-Aggressive
Day 1-3: Price at $4.00 (max loss)
        Loss: $4.00 per sale
        Volume: 50 sales
        Total Loss: -$200.00
        
Day 4-5: Try to raise to $15.00
        But customers shocked by price increase!
        Volume: Only 5 sales
        Profit: $7.00 × 5 = +$35.00
        
Final Result:
Total Sales: 55
Total Profit: -$165.00 ❌ LOSES
```

---

## 🎮 Agent Strategies Updated

### Budget King (BUDGET Variant)
```python
Wholesale: $8.00
Floor: $4.00
Strategy: Aggressive undercutting
- Can go below cost to win market share
- Willing to lose $4.00/sale initially
- Must recover with volume or later price increases
```

### Premium Player (PREMIUM Variant)
```python
Wholesale: $15.00
Floor: $7.50
Strategy: Rarely uses loss-leader
- Prefers 80% margin ($27.00)
- CAN drop to $7.50 in extreme cases
- Focuses on maintaining premium positioning
```

### Dynamic Optimizer (MID_TIER Variant)
```python
Wholesale: $12.00
Floor: $6.00
Strategy: Uses loss-leader tactically
- Monitors performance closely
- Drops below cost if no sales ($10.20 typical)
- Can go aggressive to $6.00 if desperate
- Quickly adjusts back to profit when gaining traction
```

---

## 📊 Example Scenarios

### Scenario 1: Aggressive Loss-Leader Wins

```
Market Conditions: 5-day competition, 100 total buyers

Budget King (Loss-Leader Strategy):
Day 1-2: $6.00 → 40 sales → Loss: -$80.00
Day 3-5: $12.00 → 35 sales → Profit: +$140.00
Total: 75 sales, Profit: $60.00

Premium Player (Conservative):
Day 1-5: $37.50 → 15 sales → Profit: $337.50
Total: 15 sales, Profit: $337.50 ✅ WINNER

Dynamic Optimizer (Balanced):
Day 1-5: $21.00 → 25 sales → Profit: $225.00
Total: 25 sales, Profit: $225.00

Winner: Premium Player (highest profit despite fewer sales!)
```

### Scenario 2: Volume Beats Margin

```
Market Conditions: Price-conscious buyer majority

Budget King (Aggressive):
Day 1-2: $5.00 → 50 sales → Loss: -$150.00
Day 3-5: $11.00 → 60 sales → Profit: +$180.00
Total: 110 sales, Profit: $30.00

Premium Player (Premium):
Day 1-5: $37.50 → 8 sales → Profit: $180.00
Total: 8 sales, Profit: $180.00

Dynamic Optimizer (Adaptive):
Day 1-5: $18.00 → 30 sales → Profit: $180.00
Total: 30 sales, Profit: $180.00

Winner: TIE between Premium and Dynamic at $180!
Budget King's loss-leader didn't pay off enough.
```

### Scenario 3: Failed Recovery

```
Bad Loss-Leader Execution:

Budget King (Over-Aggressive):
Day 1-3: $4.00 → 70 sales → Loss: -$280.00
Day 4: Raise to $20.00 → 2 sales → Profit: +$24.00
Day 5: Panic drop to $10.00 → 5 sales → Profit: +$10.00
Total: 77 sales, Profit: -$246.00 ❌

Premium Player:
Day 1-5: $30.00 → 12 sales → Profit: $180.00 ✅ WINNER

Key Lesson: Loss-leader must have credible recovery plan!
```

---

## 💡 Strategic Insights

### When Loss-Leader Works

✅ **Multi-day competition** (time to recover)  
✅ **Ranking system** (low price → high ranking → traffic)  
✅ **Price-conscious buyers** (will chase deals)  
✅ **Credible price increase** (not too shocking)  
✅ **High enough volume** (loss spread across many sales)

### When Loss-Leader Fails

❌ **Too short competition** (no time to recover)  
❌ **Price increase too large** (buyers abandon)  
❌ **Quality-focused buyers** (ignore cheap options)  
❌ **Competitors copy strategy** (race to bottom)  
❌ **Low volume** (loss not worth it)

---

## 🎓 For Competition Participants

### Rules

1. **Floor Price**: Can't go below 50% of wholesale
   - BUDGET: Floor $4.00
   - MID_TIER: Floor $6.00
   - PREMIUM: Floor $7.50

2. **Winner**: Highest total PROFIT (not revenue!)
   ```
   Profit = Total Revenue - (Wholesale Cost × Units Sold)
   ```

3. **Strategy Freedom**: You can:
   - Use loss-leader to gain ranking
   - Price at or above cost for steady profit
   - Mix strategies across days
   - Respond to competitor moves

### Best Practices

**Phase 1: Analyze**
```python
# Check market conditions
- How many buyers are price-conscious?
- What are competitors pricing?
- How many days in competition?
```

**Phase 2: Decide**
```python
if many_days and price_conscious_buyers:
    use_loss_leader()
elif quality_buyers:
    use_premium_pricing()
else:
    use_balanced_approach()
```

**Phase 3: Execute**
```python
if using_loss_leader:
    # Day 1-2: Below cost
    price = wholesale * 0.75  # 25% loss
    
    # Monitor ranking improvement
    if ranking_improved:
        # Day 3+: Raise to profit
        price = wholesale * 1.50  # 50% profit
```

**Phase 4: Adapt**
```python
if profit < 0 and days_remaining < 2:
    # Not enough time to recover!
    price = wholesale * 2.0  # Maximum profit now
```

---

## 📈 Expected Market Dynamics

### Race to the Bottom?

**Unlikely** because:
- Floor at 50% prevents extreme discounting
- Winner = profit, not revenue
- Loss-leader that never recovers loses
- Quality buyers ignore bottom-feeders

### Optimal Strategy?

**Depends on**:
- Buyer persona distribution
- Competition length
- Competitor behavior
- Risk tolerance

**No single dominant strategy** → Strategic depth! ✅

---

## 🎯 Testing Recommendations

### Test Scenario 1: All Use Loss-Leader
```bash
# What happens if everyone prices at floor?
Budget at $4.00
Mid-Tier at $6.00
Premium at $7.50

# Expected: Race to bottom, then rapid recovery
# Winner: Whoever executes recovery best
```

### Test Scenario 2: Mixed Strategies
```bash
# Budget uses loss-leader
# Mid-Tier balanced
# Premium stays expensive

# Expected: Budget gains volume, Premium maintains margin
# Winner: Depends on buyer distribution
```

### Test Scenario 3: Failed Recovery
```bash
# Budget at $4.00 for 3 days
# Tries to raise to $20.00
# Buyers reject

# Expected: Budget loses, conservative strategies win
# Lesson: Recovery must be gradual and credible
```

---

## ✅ Implementation Complete

All three dummy agents now support loss-leader strategies:

- **Budget King**: Aggressive, willing to go to floor
- **Premium Player**: Conservative, rarely below cost
- **Dynamic Optimizer**: Tactical, uses loss-leader when needed

The competition framework now rewards:
1. **Strategic thinking** (when to use loss-leader)
2. **Execution** (how to recover from losses)
3. **Adaptability** (responding to market feedback)
4. **Risk management** (avoiding over-aggressive losses)

**Status**: Ready for testing! 🎉

