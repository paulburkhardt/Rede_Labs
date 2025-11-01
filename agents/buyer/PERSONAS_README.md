# Buyer Personas - CSI Research-Based Implementation

## Overview
This directory contains 10 buyer personas based on the **Consumer Style Inventory (CSI)** framework by Sproles & Kendall (1986), extended with modern digital-era consumer types.

## The 10 Personas

### Core 8 CSI Dimensions

#### 1. Perfectionist Quality Maximizer (12%)
**File:** `persona_perfectionist_quality.toml`  
**CSI Dimension:** Perfectionism/High-Quality Consciousness  
**Key Traits:**
- Seeks absolute best quality with detailed specifications
- Analyzes GSM, materials, construction details
- Willing to pay 50-150% more for proven quality
- Requires 3-4 quality indicators to feel confident

#### 2. Price-Conscious Bargain Hunter (15%)
**File:** `persona_price_bargain_hunter.toml`  
**CSI Dimension:** Price-Value Consciousness  
**Key Traits:**
- Price is #1 priority (scans prices first)
- Automatically chooses cheaper if >35% price difference
- Skeptical of premium pricing and marketing
- Calculates value-per-dollar for everything

#### 3. Brand Prestige Seeker (9%)
**File:** `persona_brand_prestige_seeker.toml`  
**CSI Dimension:** Brand Consciousness  
**Key Traits:**
- Uses price as quality and status indicator
- Prefers top 25-35% price tier
- Seeks premium language and prestige positioning
- Suspicious of cheap products ("What's wrong with it?")

#### 4. Fashion-Forward Trendsetter (8%)
**File:** `persona_fashion_trendsetter.toml`  
**CSI Dimension:** Novelty-Fashion Consciousness  
**Key Traits:**
- Drawn to new, innovative, unique products
- Seeks differentiation from mass-market
- Attracted to "modern," "contemporary," "innovative" language
- Willing to pay 30-50% more for novelty

#### 5. Recreational Hedonistic Experiencer (11%)
**File:** `persona_hedonistic_experiencer.toml`  
**CSI Dimension:** Recreational/Hedonistic Shopping Consciousness  
**Key Traits:**
- Shopping is entertainment and pleasure
- Responds to sensory language ("plush," "luxurious," "spa-quality")
- Visual appeal and aesthetics critical
- Willing to pay 40-70% more for emotional appeal

#### 6. Impulsive Spontaneous Buyer (10%)
**File:** `persona_impulsive_spontaneous.toml`  
**CSI Dimension:** Impulsiveness  
**Key Traits:**
- Makes decisions in 30-60 seconds
- First impressions and gut feelings dominate
- Doesn't read long descriptions (too much effort)
- Will pay 20-40% more if immediately excited

#### 7. Confused Overwhelmed Chooser (16%)
**File:** `persona_confused_overwhelmed.toml`  
**CSI Dimension:** Confusion from Overchoice  
**Key Traits:**
- Overwhelmed by too many options
- Relies on bestseller badges and mid-price heuristics
- Avoids reading long descriptions (stress)
- Values "good enough" over "perfect"

#### 8. Habitual Brand Loyalist (9%)
**File:** `persona_habitual_brand_loyal.toml`  
**CSI Dimension:** Brand Loyalty/Habitual Behavior  
**Key Traits:**
- Sticks with familiar brands and past purchases
- "If it ain't broke, don't fix it" philosophy
- Resistant to trying new brands without good reason
- Willing to pay 15-30% more for familiar brands

### Modern Extended Dimensions

#### 9. Ethical Sustainability Advocate (6%)
**File:** `persona_ethical_sustainable.toml`  
**Modern Dimension:** Ethical/Sustainable Consciousness  
**Key Traits:**
- Prioritizes environmental and social responsibility
- Seeks organic, recycled, eco-friendly materials
- Willing to pay 30-60% more for genuine sustainability
- Skeptical of greenwashing, wants specific details

#### 10. Social Proof Validator (4%)
**File:** `persona_social_proof_validator.toml`  
**Modern Dimension:** Social Validation Consciousness (Digital Era)  
**Key Traits:**
- Heavily relies on reviews, ratings, social proof
- Trusts crowd wisdom over manufacturer claims
- Needs 4.5+ star ratings and bestseller badges
- Willing to pay 20-40% more for highly-rated products

## Distribution Rationale

The persona distribution in `simulation_config.toml` reflects realistic market composition:

1. **Confused Overwhelmed (16%)** - Highest due to modern choice overload in e-commerce
2. **Price Bargain Hunter (15%)** - Large segment, especially in commoditized markets like towels
3. **Perfectionist Quality (12%)** - Significant quality-focused segment
4. **Hedonistic Experiencer (11%)** - Growing experiential consumer segment
5. **Impulsive Spontaneous (10%)** - Common in online shopping environments
6. **Brand Prestige Seeker (9%)** - Premium/luxury segment
7. **Habitual Brand Loyal (9%)** - Established routine shoppers
8. **Fashion Trendsetter (8%)** - Early adopters and innovation seekers
9. **Ethical Sustainable (6%)** - Growing but still niche segment
10. **Social Proof Validator (4%)** - Heavy social media/review dependence

**Total: 100%**

## Research Foundation

### Primary Source
**Sproles, G. B., & Kendall, E. L. (1986).** "A methodology for profiling consumers' decision‐making styles." *Journal of Consumer Affairs*, 20(2), 267-279.

The CSI framework identified 8 distinct mental characteristics (decision-making styles) that consumers use when shopping. These have been validated across cultures and product categories for over 35 years.

### Extensions
The two additional personas (Ethical Sustainability Advocate and Social Proof Validator) represent modern consumer trends emerging from:
- Digital/social media influence on purchase behavior
- Growing environmental consciousness
- Online review culture and social commerce

## Implementation Details

Each persona TOML file includes:
- **Psychology**: Core motivations and beliefs
- **What Matters**: Priority hierarchy
- **Shopping Behavior**: Observable actions and preferences
- **Decision Criteria**: Specific thresholds and weights
- **Skills**: Four common marketplace tools contextualized to persona behavior

## Previous Personas (Deprecated)

The following 5-persona system has been superseded:
- `persona_brand_conscious.toml.old`
- `persona_price_conscious.toml.old`
- `persona_quality_seeker.toml.old`
- `persona_hedonistic_shopper.toml.old`
- `persona_confused_overchoice.toml.old`

These files are preserved with `.old` extension for reference but should not be used in new simulations.

## Usage

Personas are loaded by the simulation system based on the distribution percentages in `simulation_config.toml`. Each persona has access to four marketplace tools:
1. `search_products` - Browse/search marketplace
2. `get_product_details` - Examine specific products
3. `compare_products` - Compare multiple options
4. `purchase_product` - Make purchase decision

The tools behave identically across personas, but each persona's description guides how the AI agent uses them according to that persona's psychology and decision-making style.

