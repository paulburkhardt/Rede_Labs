"""
Simple Example: Using Seller Agents

This is a minimal example showing how to use the seller agents.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.seller import (
    BudgetKingSeller,
    PremiumPlayerSeller, 
    DynamicOptimizerSeller
)


def main():
    """Simple example of using all three seller agents"""
    
    print("\n=== Creating Seller Agents ===\n")
    
    # Create three sellers with different strategies
    budget = BudgetKingSeller("Bargain Towels")
    premium = PremiumPlayerSeller("Luxury Linens Co.")
    dynamic = DynamicOptimizerSeller("Smart Seller Inc.")
    
    sellers = [budget, premium, dynamic]
    
    # Step 1: Register all sellers
    print("Step 1: Registering sellers...")
    for seller in sellers:
        seller.register()
    
    # Step 2: Create initial listings
    print("\nStep 2: Creating product listings...")
    for seller in sellers:
        seller.create_listing()
    
    # Step 3: Simulate a market cycle
    print("\nStep 3: Running market cycle (updates)...")
    for seller in sellers:
        seller.update_listing()
    
    # Step 4: Show performance
    print("\n=== Performance Summary ===\n")
    for seller in sellers:
        summary = seller.get_performance_summary()
        print(f"{summary['seller_name']}:")
        print(f"  Strategy: {summary['strategy']}")
        print(f"  Sales: {summary['total_sales']}")
        print(f"  Revenue: ${summary['total_revenue_dollars']:.2f}")
        print(f"  Position: {summary['market_position']}")
        print()
    
    print("✓ Example completed!")
    print("\nTry running test_seller_agents.py for more comprehensive tests.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nMake sure the API server is running:")
        print("  uv run python run.py")

