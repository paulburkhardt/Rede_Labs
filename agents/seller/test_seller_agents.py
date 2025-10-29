"""
Test Script for Seller Agents

Demonstrates how to use and test the three seller agent strategies.
Run this to verify the seller agents are working correctly.
"""

import sys
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.seller.budget_king_seller import BudgetKingSeller
from agents.seller.premium_player_seller import PremiumPlayerSeller
from agents.seller.dynamic_optimizer_seller import DynamicOptimizerSeller
from agents.seller.seller_utils import MarketplaceAPI


def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def test_single_seller():
    """Test a single seller agent end-to-end"""
    print_section("TEST 1: Single Seller Agent")
    
    # Create and register a seller
    seller = BudgetKingSeller()
    
    print("\n1. Registering seller...")
    registration = seller.register()
    print(f"   Seller ID: {registration['id']}")
    print(f"   Auth Token: {registration['auth_token'][:20]}...")
    
    print("\n2. Creating initial listing...")
    listing = seller.create_listing()
    print(f"   Product created: {listing}")
    
    print("\n3. Simulating market cycle...")
    time.sleep(1)
    
    print("\n4. Updating listing based on market...")
    update = seller.update_listing()
    print(f"   Update result: {update if update else 'No updates needed'}")
    
    print("\n5. Getting performance summary...")
    summary = seller.get_performance_summary()
    print(f"   Performance: {summary}")
    
    print("\n✓ Single seller test completed!")
    return seller


def test_all_three_sellers():
    """Test all three seller agents competing"""
    print_section("TEST 2: Three Competing Sellers")
    
    # Create all three seller types
    sellers = [
        BudgetKingSeller("Budget King"),
        PremiumPlayerSeller("Premium Player"),
        DynamicOptimizerSeller("Dynamic Optimizer")
    ]
    
    print("\n1. Registering all sellers...")
    for seller in sellers:
        reg = seller.register()
        print(f"   ✓ {seller.name} registered")
    
    print("\n2. Creating initial listings...")
    for seller in sellers:
        seller.create_listing()
    
    print("\n3. Getting market intelligence...")
    market_data = sellers[0].api.get_market_intelligence()
    print(f"\n   Market Analysis:")
    print(f"   - Total Products: {market_data['total_products']}")
    print(f"   - Average Price: ${market_data['avg_price_cents']/100:.2f}")
    print(f"   - Price Range: ${market_data['min_price_cents']/100:.2f} - ${market_data['max_price_cents']/100:.2f}")
    
    print("\n4. Simulating 3 market cycles...")
    for cycle in range(1, 4):
        print(f"\n   --- Cycle {cycle} ---")
        time.sleep(1)
        
        for seller in sellers:
            seller.update_listing()
        
        # Show current prices
        market_data = sellers[0].api.get_market_intelligence()
        for product in market_data.get('my_products', []) + market_data.get('competitor_products', []):
            seller_id = product.get('seller_id', 'unknown')
            print(f"   Product: {product['name'][:40]}... | ${product['price_in_cent']/100:.2f}")
    
    print("\n5. Final Performance Summary:")
    print("   " + "-" * 66)
    for seller in sellers:
        summary = seller.get_performance_summary()
        print(f"\n   {summary['seller_name']} ({summary['strategy']})")
        print(f"   - Sales: {summary['total_sales']}")
        print(f"   - Revenue: ${summary['total_revenue_dollars']:.2f}")
        print(f"   - Market Position: {summary['market_position']}")
    
    print("\n✓ Three-seller competition test completed!")
    return sellers


def test_market_response():
    """Test how sellers respond to different market conditions"""
    print_section("TEST 3: Market Response Testing")
    
    print("\nScenario: All sellers start, one gets sales")
    print("Testing how agents respond to competitive success...\n")
    
    # In a real scenario, you'd simulate purchases here
    # For now, we just show the structure
    
    sellers = [
        BudgetKingSeller("Budget Tester"),
        PremiumPlayerSeller("Premium Tester"),
        DynamicOptimizerSeller("Dynamic Tester")
    ]
    
    for seller in sellers:
        seller.register()
        seller.create_listing()
    
    print("Market created with 3 competing sellers")
    print("\nTo fully test market response:")
    print("1. Start the API server: uv run python run.py")
    print("2. Use the buyer agents to make purchases")
    print("3. Call update_listing() to see how sellers adapt")
    
    print("\n✓ Market response test setup completed!")
    return sellers


def test_api_connectivity():
    """Test connection to the marketplace API"""
    print_section("TEST 0: API Connectivity Check")
    
    try:
        api = MarketplaceAPI()
        
        print("\n1. Testing seller registration...")
        seller_data = api.register_seller()
        print(f"   ✓ Registration successful")
        print(f"   Seller ID: {seller_data['id']}")
        
        print("\n2. Testing product search...")
        products = api.search_products("")
        print(f"   ✓ Search successful")
        print(f"   Found {len(products)} products in marketplace")
        
        print("\n3. Testing market intelligence...")
        market_data = api.get_market_intelligence()
        print(f"   ✓ Market intelligence retrieved")
        print(f"   Total products: {market_data['total_products']}")
        print(f"   Competitors: {market_data['competitor_count']}")
        
        print("\n✓ API connectivity test passed!")
        return True
        
    except Exception as e:
        print(f"\n✗ API connectivity test failed: {e}")
        print("\nMake sure the API server is running:")
        print("  uv run python run.py")
        return False


def main():
    """Run all tests"""
    print("\n" + "█" * 70)
    print("  SELLER AGENT TEST SUITE")
    print("█" * 70)
    
    # Test 0: Check API connectivity
    if not test_api_connectivity():
        print("\n⚠ Please start the API server before running tests")
        return
    
    # Test 1: Single seller
    test_single_seller()
    
    # Test 2: Three competing sellers
    test_all_three_sellers()
    
    # Test 3: Market response
    test_market_response()
    
    print("\n" + "█" * 70)
    print("  ALL TESTS COMPLETED")
    print("█" * 70)
    print("\nNext Steps:")
    print("1. Review the performance of each seller strategy")
    print("2. Integrate with the green agent orchestration")
    print("3. Test with buyer agents to simulate full marketplace")
    print("4. Adjust strategies based on results")
    print()


if __name__ == "__main__":
    main()

