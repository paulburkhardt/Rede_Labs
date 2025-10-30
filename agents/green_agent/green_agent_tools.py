# -*- coding: utf-8 -*-
"""
Dummy Green Agent Tools

This file provides example tools for a green (evaluation) agent.
These tools are used to communicate with other agents and report battle results.
"""

import json
from nturl2path import url2pathname
from os import name
import agentbeats as ab
from agentbeats.logging import BattleContext
import requests
from agentbeats.utils.agents import send_message_to_agent
from agentbeats.logging import record_battle_event, record_battle_result
import random
import asyncio
import toml
from pathlib import Path
import os
from enum import Enum
import subprocess
import sys


# Global state to store battle context
battle_context = None

api_url = "http://localhost:8000"
admin_api_key = os.getenv("ADMIN_API_KEY")


from typing import NamedTuple


class Seller(NamedTuple):
    id: str
    url: str
    token: str


class Buyer(NamedTuple):
    id: str
    url: str
    token: str

# If you change this, also change it in app/services/phase_manager.py
class Phase(str, Enum):
    """Lifecycle phases that gate marketplace operations."""

    #: Phase for seller management, where sellers can update listings
    SELLER_MANAGEMENT = "seller_management"
    #: Phase for buyer shopping, where buyers can purchase products
    BUYER_SHOPPING = "buyer_shopping"
    #: Phase for open marketplace, where all interactions are allowed
    OPEN = "open"


sellers: list[Seller] = []
buyers: list[Buyer] = []

# If you change something here, also change it in app/services/phase_manager.py
class Phase(str, Enum):
    """Lifecycle phases that gate marketplace operations."""

    #: Phase for seller management, where sellers can update listings
    SELLER_MANAGEMENT = "seller_management"
    #: Phase for buyer shopping, where buyers can purchase products
    BUYER_SHOPPING = "buyer_shopping"
    #: Phase for open marketplace, where all interactions are allowed
    OPEN = "open"


def change_phase(phase: Phase) -> None:
    """
    Update the marketplace backend to the specified phase.
    """

    headers = {"X-Admin-Key": admin_api_key} if admin_api_key else None
    response = requests.post(
        f"{api_url}/admin/phase",
        # json={"phase": phase.value},
        # Currently, disabled because broken.
        json={"phase": Phase.OPEN.value},
        headers=headers,
    )
    if response.status_code != 200:
        raise Exception(
            f"Failed to update marketplace phase to {phase.value}: {response.text}"
        )

    if battle_context:
        record_battle_event(
            battle_context, f"Marketplace phase set to '{phase.value}'"
        )


def set_marketplace_day(day: int) -> None:
    """
    Update the marketplace backend to the specified simulated day.
    """
    headers = {"X-Admin-Key": admin_api_key} if admin_api_key else None
    response = requests.post(
        f"{api_url}/admin/day",
        json={"day": day},
        headers=headers,
    )
    if response.status_code != 200:
        raise Exception(
            f"Failed to update marketplace day to {day}: {response.text}"
        )

    if battle_context:
        record_battle_event(
            battle_context, f"Marketplace day set to '{day}'"
        )


def clear_database():
    """Clear all data from the database tables by running a script in the correct environment"""
    try:
        print("🗑️  Clearing database...")
        
        # Create a simple Python script to clear the database
        project_root = Path(__file__).parent.parent.parent
        clear_script = """
import sys
sys.path.insert(0, '.')
from app.database import SessionLocal, Base, engine
from app.models.purchase import Purchase
from app.models.product import Product
from app.models.buyer import Buyer
from app.models.seller import Seller
from app.models.image import Image

# Drop all tables and recreate them
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
print("Tables cleared and recreated")
"""
        
        # Run the script using uv run to ensure correct environment
        env = os.environ.copy()
        result = subprocess.run(
            ["uv", "run", "python", "-c", clear_script],
            cwd=str(project_root),
            env=env,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("✅ Database cleared and tables recreated")
        else:
            print(f"⚠️  Warning: Failed to clear database (code {result.returncode})")
            print(f"   stderr: {result.stderr}")
            
    except Exception as e:
        print(f"⚠️  Warning: Failed to clear database: {e}")
        import traceback
        traceback.print_exc()


def reload_images():
    """Reload images from the images directory using the creation script"""
    try:
        print("📸 Reloading images from images directory...")
        
        # Get the path to the images directory and script
        project_root = Path(__file__).parent.parent.parent
        images_dir = project_root / "images"
        script_path = images_dir / "create_image_descriptions.py"
        
        print(f"   Script path: {script_path}")
        print(f"   Working directory: {images_dir}")
        
        if not script_path.exists():
            print(f"⚠️  Warning: Image creation script not found at {script_path}")
            return
        
        # Run the script to reload images using uv run to ensure correct environment
        # Pass environment variables to ensure it uses the same database
        env = os.environ.copy()
        result = subprocess.run(
            ["uv", "run", "python", str(script_path)],
            cwd=str(images_dir),
            env=env,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            print("✅ Images reloaded successfully")
            # Print last few lines of output to confirm
            output_lines = result.stdout.strip().split('\n')
            if len(output_lines) > 5:
                print("   Last lines of output:")
                for line in output_lines[-5:]:
                    print(f"   {line}")
        else:
            print(f"⚠️  Warning: Image reload script failed with code {result.returncode}")
            print(f"   stderr: {result.stderr}")
            print(f"   stdout: {result.stdout}")
            
    except Exception as e:
        print(f"⚠️  Warning: Failed to reload images: {e}")
        import traceback
        traceback.print_exc()


@ab.tool
async def handle_incoming_message(message: str) -> str:
    """
    Handle incoming messages from the AgentBeats backend and orchestrate battles.
    This processes battle_start notifications and runs the full battle workflow.

    Args:
        message: The incoming message (usually JSON)

    Returns:
        str: Battle result summary
    """
    global battle_context

    try:
        # Parse the message as JSON
        try:
            message_data = json.loads(message)
        except json.JSONDecodeError:
            return f"Received non-JSON message: {message}"

        # Check if this is a battle start message
        if message_data.get("type") == "battle_start":
            battle_id = message_data.get("battle_id")
            green_battle_context = message_data.get("green_battle_context")
            seller_infos = message_data.get("opponent_infos", [])

            if not battle_id or not green_battle_context:
                return "Invalid battle start message - missing battle_id or green_battle_context"

            # Create battle context from the provided data
            battle_context = BattleContext(
                battle_id=green_battle_context.get("battle_id"),
                backend_url=green_battle_context.get("backend_url"),
                agent_name=green_battle_context.get("agent_name"),
            )

            # Now orchestrate the battle automatically
            return await orchestrate_battle(battle_id, seller_infos)

        return f"Received message of type: {message_data.get('type', 'unknown')}"

    except Exception as e:
        return f"Error processing message: {str(e)}"


async def orchestrate_battle(battle_id: str, seller_infos: list) -> str:
    """
    Orchestrate the dummy battle: send questions, collect responses, evaluate, and report.

    Args:
        battle_id: The battle ID
        seller_infos: List of seller info dicts with 'agent_url' and 'name'

    Returns:
        str: Battle completion summary
    """

    global battle_context, sellers, buyers

    if not battle_context:
        return "Error: Battle context not initialized"

    record_battle_event(battle_context, "Battle orchestration started")

    # Clear database and reload images at the start
    clear_database()
    reload_images()
    set_marketplace_day(0)

    days: int = 5  # Total days in the battle
    try:
        await create_sellers(seller_infos)
        await create_buyer()
        print(sellers)
        print(buyers)

        # Day 1: Create listings
        change_phase(Phase.SELLER_MANAGEMENT)
        await create_listings()
        await create_ranking()

        change_phase(Phase.BUYER_SHOPPING)
        await buyers_buy_products()

        for current_day in range(1, days):
            set_marketplace_day(current_day)
            await update_ranking()

            change_phase(Phase.SELLER_MANAGEMENT)
            await sellers_update_listings()

            change_phase(Phase.BUYER_SHOPPING)
            await buyers_buy_products()

    except Exception as e:
        error_msg = f"Error orchestrating battle: {str(e)}"
        record_battle_event(battle_context, error_msg)
        return error_msg

    finally:
        try:
            change_phase(Phase.OPEN)
        except Exception as phase_error:
            warning = f"Failed to reset marketplace phase: {phase_error}"
            if battle_context:
                record_battle_event(battle_context, warning)
            print(warning)

    await report_leaderboard()


async def create_sellers(seller_infos: list):
    for seller_info in seller_infos:
        # todo: add super admin auth token
        print("🥥 Creating seller")
        print(api_url + "/createSeller"),
        response = requests.post(
            api_url + "/createSeller",
            headers={"X-Admin-Key": admin_api_key} if admin_api_key else None,
        )
        print("🥥 Created seller")
        if response.status_code != 200:
            raise Exception(f"Failed to create seller: {response.text}")

        json = response.json()
        id = json.get("id")
        token = json.get("auth_token")
        sellers.append(Seller(id=id, url=seller_info.get("agent_url"), token=token))


async def create_buyer():
    """Create buyers based on configuration from tools/scenario.toml"""
    # Load scenario configuration
    scenario_path = Path(__file__).parent.parent.parent / "tools" / "scenario.toml"

    if not scenario_path.exists():
        raise Exception(f"Scenario file not found at {scenario_path}")

    scenario_config = toml.load(scenario_path)

    # Filter agents where card filename starts with "buyer_"
    buyer_agents = [
        agent
        for agent in scenario_config.get("agents", [])
        if Path(agent["card"]).name.startswith("buyer_")
    ]

    # Create buyers based on the configuration
    for buyer_agent in buyer_agents:
        agent_host = buyer_agent.get("agent_host")
        agent_port = buyer_agent.get("agent_port")

        if not agent_port:
            raise Exception(
                f"No agent_port found for buyer agent: {buyer_agent.get('name')}"
            )

        # Create buyer via API
        response = requests.post(
            api_url + "/createBuyer",
            headers={"X-Admin-Key": admin_api_key} if admin_api_key else None,
        )

        if response.status_code != 200:
            raise Exception(f"Failed to create buyer: {response.text}")

        buyer_data = response.json()
        # Store buyer with URL constructed from agent configuration
        # todo: is that a problem that the buyer has to run local (because of the http://)?
        url = f"http://{agent_host}:{agent_port}"
        buyers.append(
            Buyer(id=buyer_data.get("id"), url=url, token=buyer_data.get("auth_token"))
        )


async def create_participants(no_participants: int, route: str):
    for i in range(no_participants):
        # todo: add super admin auth token
        response = requests.post(
            api_url + route,
            headers={"X-Admin-Key": admin_api_key} if admin_api_key else None,
        )
        if response.status_code != 200:
            raise Exception(f"Failed to create seller: {response.text}")

        # todo: confirm if that actually works
        if route == "/createSeller":
            sellers.append(response.json())
        elif route == "/createBuyer":
            buyers.append(response.json())

        return response.json()


async def create_listings():
    timeout_minutes = 2  # Timeout duration in minutes
    timeout_seconds = timeout_minutes * 60

    for seller in sellers:
        prompt = f"""
Call /createProduct to create a product.

Your seller ID: {seller.id}
Your auth token: {seller.token}

Use the auth token in the Authorization header as "Bearer {seller.token}" when making API calls.

Response format:
{{
    "product_id": "123", # id of the product you created
}}
        """
        try:
            # Send message with timeout
            await asyncio.wait_for(
                send_message_to_agent(seller.url, prompt), timeout=timeout_seconds
            )
        except asyncio.TimeoutError:
            # Log timeout event
            timeout_msg = f"Seller {seller.id} timed out after {timeout_minutes} minutes and lost their chance"
            print(timeout_msg)
            if battle_context:
                record_battle_event(battle_context, timeout_msg)
        except Exception as e:
            # Log other errors but continue with other buyers
            error_msg = f"Error communicating with seller {seller.id}: {str(e)}"
            print(error_msg)
            if battle_context:
                record_battle_event(battle_context, error_msg)


async def create_ranking():
    # Initialize rankings with random values via API
    response = requests.post(f"{api_url}/rankings/initialize")
    if response.status_code != 200:
        raise Exception(f"Failed to initialize rankings: {response.text}")
    
    result = response.json()
    print(f"✅ {result['message']}")


async def update_ranking():
    # Update rankings based on sales performance via API
    response = requests.post(f"{api_url}/rankings/update-by-sales")
    if response.status_code != 200:
        print(f"Warning: Failed to update rankings: {response.text}")
        return
    
    result = response.json()
    print(f"✅ {result['message']}")
    
    # Log top products for visibility
    if "top_products" in result:
        print("📊 Top 5 products by sales:")
        for product in result["top_products"]:
            print(f"   Rank {product['ranking']}: {product['product_name']} ({product['sales_count']} sales)")


async def buyers_buy_products():
    timeout_minutes = 2  # Timeout duration in minutes
    timeout_seconds = timeout_minutes * 60

    for buyer in buyers:
        prompt = f"""
Call /search?q=keyword to find your product you want to buy. You can call /product/{{id}} to get more details about the product.

Your buyer ID: {buyer.id}
Your auth token: {buyer.token}

Use the auth token in the Authorization header as "Bearer {buyer.token}" when making API calls.

Response even if you decided not to buy a product.

Response format:
{{
    "product_id": "123", # id of the product you bought, null if you decided not to buy a product
    "decision": "buy" or "not buy"
}}
        """
        try:
            # Send message with timeout
            await asyncio.wait_for(
                send_message_to_agent(buyer.url, prompt), timeout=timeout_seconds
            )
        except asyncio.TimeoutError:
            # Log timeout event
            timeout_msg = f"Buyer {buyer.id} timed out after {timeout_minutes} minutes and lost their chance"
            print(timeout_msg)
            if battle_context:
                record_battle_event(battle_context, timeout_msg)
        except Exception as e:
            # Log other errors but continue with other buyers
            error_msg = f"Error communicating with buyer {buyer.id}: {str(e)}"
            print(error_msg)
            if battle_context:
                record_battle_event(battle_context, error_msg)


async def sellers_update_listings():
    timeout_minutes = 2  # Timeout duration in minutes
    timeout_seconds = timeout_minutes * 60

    for seller in sellers:
        prompt = f"""
Call /updateProduct to update your product.

Your seller ID: {seller.id}
Your auth token: {seller.token}

Use the auth token in the Authorization header as "Bearer {seller.token}" when making API calls.

Response format:
{{
    "product_id": "123", # id of the product you updated
}}
        """
        try:
            # Send message with timeout
            await asyncio.wait_for(
                send_message_to_agent(seller.url, prompt), timeout=timeout_seconds
            )
        except asyncio.TimeoutError:
            # Log timeout event
            timeout_msg = f"Seller {seller.id} timed out after {timeout_minutes} minutes and lost their chance"
            print(timeout_msg)
            if battle_context:
                record_battle_event(battle_context, timeout_msg)
        except Exception as e:
            # Log other errors but continue with other sellers
            error_msg = f"Error communicating with seller {seller.id}: {str(e)}"
            print(error_msg)
            if battle_context:
                record_battle_event(battle_context, error_msg)


async def report_leaderboard():
    """Queries the purchase history and reports a leaderboard (total revenue,
    etc.) to AgentBeats."""
    global battle_context

    if not battle_context:
        print("Warning: Battle context not initialized")
        return

    try:
        # Step 1: Fetch leaderboard data from API
        record_battle_event(battle_context, "Fetching leaderboard data")
        response = requests.get(f"{api_url}/buy/stats/leaderboard")

        if response.status_code != 200:
            error_msg = f"Failed to fetch leaderboard: {response.text}"
            record_battle_event(battle_context, error_msg)
            return

        leaderboard_data = response.json()

        # Step 2: Calculate winner and scores
        winner = None
        winner_score = 0
        scores = {}

        for entry in leaderboard_data:
            seller_id = entry["seller_id"]
            revenue = entry["total_revenue_cents"]
            purchase_count = entry["purchase_count"]

            # Score is based on total revenue
            score = revenue
            scores[seller_id] = {
                "revenue_cents": revenue,
                "revenue_dollars": entry["total_revenue_dollars"],
                "purchase_count": purchase_count,
                "score": score,
            }

            record_battle_event(
                battle_context,
                f"Seller {seller_id}: ${entry['total_revenue_dollars']:.2f} revenue, {purchase_count} purchases",
            )

            if score > winner_score:
                winner_score = score
                winner = seller_id

        # Step 3: Report final result
        result_detail = {
            "leaderboard": leaderboard_data,
            "scores": scores,
            "winner": winner,
            "winner_revenue": winner_score / 100.0 if winner_score else 0,
        }

        record_battle_result(
            battle_context,
            f"Battle completed - Winner: {winner} with ${winner_score / 100.0:.2f} total revenue",
            winner,
            result_detail,
        )

    except Exception as e:
        error_msg = f"Error reporting leaderboard: {str(e)}"
        record_battle_event(battle_context, error_msg)
        print(error_msg)
