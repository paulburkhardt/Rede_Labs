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
from agentbeats.utils.agents import send_message_to_agent, send_messages_to_agents
from agentbeats.logging import record_battle_event, record_battle_result
import random
import asyncio
import toml
from pathlib import Path
import os
from enum import Enum
import subprocess
import sys

# Add agents directory to sys.path to enable shared battle_logger import
agents_dir = Path(__file__).parent.parent
if str(agents_dir) not in sys.path:
    sys.path.insert(0, str(agents_dir))

# Import battle logger - this will be cached by Python's import system
# ensuring all modules share the same instance
import battle_logger
set_battle_context = battle_logger.set_battle_context


# Global state to store battle context
battle_context = None

api_url = "http://localhost:8000"
admin_api_key = os.getenv("ADMIN_API_KEY")


from typing import NamedTuple


class Seller(NamedTuple):
    id: str
    url: str
    token: str
    name: str = ""  # Agent name from opponent_infos


class Buyer(NamedTuple):
    id: str
    url: str
    token: str
    name: str = ""

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


def set_marketplace_round(round_number: int) -> None:
    """
    Persist the active simulation round in the marketplace backend.
    """
    headers = {"X-Admin-Key": admin_api_key} if admin_api_key else None
    response = requests.post(
        f"{api_url}/admin/round",
        json={"round": round_number},
        headers=headers,
    )
    if response.status_code != 200:
        raise Exception(
            f"Failed to update marketplace round to {round_number}: {response.text}"
        )

    if battle_context:
        record_battle_event(
            battle_context, f"Marketplace round set to '{round_number}'"
        )


def clear_database():
    """Clear all data from the database tables by running a script in the correct environment"""
    try:
        print("🗑️  Clearing database...")
        if battle_context:
            record_battle_event(battle_context, "Clearing database...")
        
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
            message = "✅ Database cleared and tables recreated"
            print(message)
            if battle_context:
                record_battle_event(battle_context, "Database cleared and tables recreated")
        else:
            warning = f"⚠️  Warning: Failed to clear database (code {result.returncode})"
            print(warning)
            print(f"   stderr: {result.stderr}")
            if battle_context:
                record_battle_event(battle_context, f"Failed to clear database (code {result.returncode})")
            
    except Exception as e:
        error_msg = f"⚠️  Warning: Failed to clear database: {e}"
        print(error_msg)
        if battle_context:
            record_battle_event(battle_context, f"Failed to clear database: {str(e)}")
        import traceback
        traceback.print_exc()


def reload_images():
    """Reload images from the images directory using the creation script"""
    try:
        print("📸 Reloading images from images directory...")
        if battle_context:
            record_battle_event(battle_context, "Reloading images from database...")
        
        # Get the path to the images directory and script
        project_root = Path(__file__).parent.parent.parent
        images_dir = project_root / "images"
        script_path = images_dir / "create_image_descriptions.py"
        
        print(f"   Script path: {script_path}")
        print(f"   Working directory: {images_dir}")
        
        if not script_path.exists():
            warning = f"⚠️  Warning: Image creation script not found at {script_path}"
            print(warning)
            if battle_context:
                record_battle_event(battle_context, "Image creation script not found")
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
            message = "✅ Images reloaded successfully"
            print(message)
            # Print last few lines of output to confirm
            output_lines = result.stdout.strip().split('\n')
            if len(output_lines) > 5:
                print("   Last lines of output:")
                for line in output_lines[-5:]:
                    print(f"   {line}")
            if battle_context:
                record_battle_event(battle_context, "Images reloaded successfully")
        else:
            warning = f"⚠️  Warning: Image reload script failed with code {result.returncode}"
            print(warning)
            print(f"   stderr: {result.stderr}")
            print(f"   stdout: {result.stdout}")
            if battle_context:
                record_battle_event(battle_context, f"Image reload failed (code {result.returncode})")
            
    except Exception as e:
        error_msg = f"⚠️  Warning: Failed to reload images: {e}"
        print(error_msg)
        if battle_context:
            record_battle_event(battle_context, f"Failed to reload images: {str(e)}")
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
            
            # Set the battle context globally so shared tools can access it
            set_battle_context(battle_context)

            # Now orchestrate the battle automatically
            # Note: Battle context will be stored in metadata AFTER database clear
            return await orchestrate_battle(battle_id, seller_infos, green_battle_context)

        return f"Received message of type: {message_data.get('type', 'unknown')}"

    except Exception as e:
        return f"Error processing message: {str(e)}"


async def orchestrate_battle(battle_id: str, seller_infos: list, green_battle_context: dict) -> str:
    """
    Orchestrate the dummy battle: send questions, collect responses, evaluate, and report.

    Args:
        battle_id: The battle ID
        seller_infos: List of seller info dicts with 'agent_url' and 'name'
        green_battle_context: Battle context data to store in metadata

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

    await set_battle_metadata(battle_id, green_battle_context.get("backend_url"))

    rounds_env = os.getenv("MARKETPLACE_ROUNDS") or os.getenv("SIMULATION_ROUNDS")
    days_env = os.getenv("MARKETPLACE_DAYS") or os.getenv("SIMULATION_DAYS")

    try:
        rounds = int(rounds_env) if rounds_env else 3
    except (TypeError, ValueError):
        rounds = 3

    try:
        days = int(days_env) if days_env else 5
    except (TypeError, ValueError):
        days = 5

    if battle_context:
        record_battle_event(
            battle_context,
            f"Configuring battle for {rounds} round(s) with {days} day(s) each",
        )

    try:
        await create_sellers(seller_infos)
        await create_buyer()
        print(sellers)
        print(buyers)

        for current_round in range(1, rounds + 1):
            set_marketplace_round(current_round)
            set_marketplace_day(0)

            if battle_context:
                record_battle_event(
                    battle_context,
                    f"Round {current_round}/{rounds} started",
                )

            # Day 0 preparation
            change_phase(Phase.SELLER_MANAGEMENT)
            if current_round == 1:
                await create_listings()
            else:
                await sellers_update_listings()
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

            if battle_context:
                record_battle_event(
                    battle_context,
                    f"Round {current_round}/{rounds} completed",
                )

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
    seller_names = {}  # Map seller_id to agent_name
    
    for seller_info in seller_infos:
        # todo: add super admin auth token
        print("🥥 Creating seller")
        response = requests.post(
            api_url + "/createSeller",
            headers={"X-Admin-Key": admin_api_key} if admin_api_key else None,
        )
        if response.status_code != 200:
            raise Exception(f"Failed to create seller: {response.text}")

        json = response.json()
        id = json.get("id")
        token = json.get("auth_token")
        agent_name = seller_info.get("name", "Unknown Seller")
        sellers.append(Seller(id=id, url=seller_info.get("agent_url"), token=token, name=agent_name))
        seller_names[id] = agent_name
        
        message = f"🥥 Created seller {id} ({agent_name})"
        print(message)
        if battle_context:
            record_battle_event(battle_context, f"Created seller {id} ({agent_name})")
    
    # Store seller names in metadata so seller agents can retrieve their actual names
    try:
        headers = {"X-Admin-Key": admin_api_key} if admin_api_key else None
        import json as json_module
        requests.post(
            f"{api_url}/admin/metadata/seller_names",
            json={"seller_names": seller_names},
            headers=headers
        )
        print(f"✅ Stored seller names in metadata: {seller_names}")
    except Exception as e:
        print(f"⚠️  Warning: Failed to store seller names: {e}")


async def set_battle_metadata(battle_id: str, backend_url: str):
    try:
        headers = {"X-Admin-Key": admin_api_key} if admin_api_key else None
        requests.post(
            f"{api_url}/admin/metadata",
            json={"battle_id": battle_id, "backend_url": backend_url},
            headers=headers
        )
        print(f"✅ Stored battle metadata: {battle_id}, {backend_url}")
    except Exception as e:
        print(f"⚠️  Warning: Failed to store battle metadata: {e}")


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
        configured_name = buyer_agent.get("name")
        buyer_display_name = configured_name or f"Buyer {len(buyers) + 1}"

        if not agent_port:
            raise Exception(
                f"No agent_port found for buyer agent: {buyer_agent.get('name')}"
            )

        # Create buyer via API
        response = requests.post(
            api_url + "/createBuyer",
            json={"name": buyer_display_name},
            headers={"X-Admin-Key": admin_api_key} if admin_api_key else None,
        )

        if response.status_code != 200:
            raise Exception(f"Failed to create buyer: {response.text}")

        buyer_data = response.json()
        stored_name = buyer_data.get("name", buyer_display_name)
        # Store buyer with URL constructed from agent configuration
        # todo: is that a problem that the buyer has to run local (because of the http://)?
        url = f"http://{agent_host}:{agent_port}"
        buyer_id = buyer_data.get("id")
        buyers.append(
            Buyer(
                id=buyer_id,
                url=url,
                token=buyer_data.get("auth_token"),
                name=stored_name,
            )
        )
        
        message = f"🛒 Created buyer {buyer_id} ({stored_name})"
        print(message)
        if battle_context:
            record_battle_event(battle_context, f"Created buyer {buyer_id} ({stored_name})")


async def create_participants(no_participants: int, route: str):
    for i in range(no_participants):
        request_kwargs = {
            "headers": {"X-Admin-Key": admin_api_key} if admin_api_key else None,
        }
        if route == "/createBuyer":
            request_kwargs["json"] = {"name": f"Buyer {len(buyers) + 1}"}
        # todo: add super admin auth token
        response = requests.post(
            api_url + route,
            **request_kwargs,
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

    prompt_template = """
Call /createProduct to create a product.

Your seller ID: {id}
Your auth token: {token}

Use the auth token in the Authorization header as "Bearer {token}" when making API calls.

Response format:
{{
    "product_id": "123", # id of the product you created
}}
        """

    await _send_prompts_to_agents(sellers, prompt_template, "Telling sellers to create products...", timeout_seconds)


async def create_ranking():
    # Initialize rankings with random values via API
    response = requests.post(f"{api_url}/rankings/initialize")
    if response.status_code != 200:
        raise Exception(f"Failed to initialize rankings: {response.text}")
    
    result = response.json()
    message = f"✅ {result['message']}"
    print(message)
    if battle_context:
        record_battle_event(battle_context, result['message'])


async def update_ranking():
    # Update rankings based on sales performance via API
    response = requests.post(f"{api_url}/rankings/update-by-sales")
    if response.status_code != 200:
        warning = f"Warning: Failed to update rankings: {response.text}"
        print(warning)
        if battle_context:
            record_battle_event(battle_context, warning)
        return
    
    result = response.json()
    message = f"✅ {result['message']}"
    print(message)
    if battle_context:
        record_battle_event(battle_context, result['message'])
    
    # Log top products for visibility
    if "top_products" in result:
        print("📊 Top 5 products by sales:")
        top_products_summary = []
        for product in result["top_products"]:
            product_line = f"   Rank {product['ranking']}: {product['product_name']} ({product['sales_count']} sales)"
            print(product_line)
            top_products_summary.append(f"#{product['ranking']} {product['product_name']} ({product['sales_count']} sales)")
        
        if battle_context and top_products_summary:
            record_battle_event(battle_context, f"📊 Top products: {', '.join(top_products_summary[:3])}")


async def buyers_buy_products():
    timeout_minutes = 2  # Timeout duration in minutes
    timeout_seconds = timeout_minutes * 60

    prompt_template = """
Call /search?q=keyword to find your product you want to buy. You can call /product/{{id}} to get more details about the product.

Your buyer ID: {id}
Your auth token: {token}

Use the auth token in the Authorization header as "Bearer {token}" when making API calls.

Response even if you decided not to buy a product.

Response format:
{{
    "product_id": "123", # id of the product you bought, null if you decided not to buy a product
    "decision": "buy" or "not buy"
}}
        """

    await _send_prompts_to_agents(buyers, prompt_template, "Telling buyers to buy products...", timeout_seconds)


async def sellers_update_listings():
    timeout_minutes = 2  # Timeout duration in minutes
    timeout_seconds = timeout_minutes * 60

    prompt_template = """
Call /updateProduct to update your product.

Your seller ID: {id}
Your auth token: {token}

Use the auth token in the Authorization header as "Bearer {token}" when making API calls.

Response format:
{{
    "product_id": "123", # id of the product you updated
}}
        """

    await _send_prompts_to_agents(sellers, prompt_template, "Telling sellers to update products...", timeout_seconds)


async def report_leaderboard():
    """Queries the purchase history and reports a leaderboard (total profit,
    etc.) to AgentBeats."""
    global battle_context, sellers

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

        leaderboard_payload = response.json()

        seller_names = { seller.id: seller.name for seller in sellers }

        rounds_data = leaderboard_payload.get("rounds", [])
        overall_section = leaderboard_payload.get("overall", {})
        overall_leaderboard = overall_section.get("leaderboard", [])
        overall_winners = overall_section.get("winners", [])
        current_round = leaderboard_payload.get("current_round")

        # Step 2: Log per-round summaries
        for round_entry in rounds_data:
            round_number = round_entry.get("round")
            winners = round_entry.get("winners", [])
            winners_label = ", ".join(winners) if winners else "no winner"
            leaderboard_entries = round_entry.get("leaderboard", [])
            top_entry = leaderboard_entries[0] if leaderboard_entries else None

            summary_parts = [
                f"Round {round_number}: winners - {winners_label}",
            ]
            if top_entry:
                summary_parts.append(
                    f"top profit ${top_entry['total_profit_dollars']:.2f} (seller {top_entry['seller_id']})"
                )

            record_battle_event(battle_context, "; ".join(summary_parts))

        # Step 3: Calculate overall scores
        scores = {}
        for entry in overall_leaderboard:
            seller_id = entry["seller_id"]
            seller_name = seller_names.get(seller_id)
            profit_cents = entry["total_profit_cents"]
            purchase_count = entry["purchase_count"]
            round_wins = entry.get("round_wins", 0)

            scores[seller_id] = {
                "seller_name": seller_name,
                "profit_cents": profit_cents,
                "profit_dollars": entry["total_profit_dollars"],
                "purchase_count": purchase_count,
                "round_wins": round_wins,
            }

            record_battle_event(
                battle_context,
                (
                    f"Overall - Seller {seller_name} ({seller_id}): "
                    f"{round_wins} round win(s), "
                    f"${entry['total_profit_dollars']:.2f} profit, "
                    f"{purchase_count} purchases"
                ),
            )

        if overall_winners:
            primary_winner_id = overall_winners[0]
            primary_winner_name = seller_names.get(primary_winner_id)
            winner_stats = scores.get(primary_winner_id, {})
            winner_round_wins = winner_stats.get("round_wins", 0)
            winner_profit_dollars = winner_stats.get("profit_dollars", 0.0)

            if len(overall_winners) == 1:
                summary = (
                    "Battle completed - Winner: "
                    f"{primary_winner_name} ({primary_winner_id}) ({winner_round_wins} round win(s), "
                    f"${winner_profit_dollars:.2f} profit)"
                )
            else:
                tied_winners = ", ".join(overall_winners)
                summary = (
                    "Battle completed - Tie between "
                    f"{tied_winners} with {winner_round_wins} round win(s) each"
                )
        else:
            primary_winner_id = None
            primary_winner_name = None
            winner_round_wins = 0
            winner_profit_dollars = 0.0
            summary = "Battle completed - No overall winner determined"

        # Step 4: Report final result
        result_detail = {
            "current_round": current_round,
            "rounds": rounds_data,
            "overall": overall_section,
            "scores": scores,
        }

        record_battle_result(
            battle_context,
            summary,
            f"{primary_winner_name} ({primary_winner_id})",
            result_detail,
        )

    except Exception as e:
        error_msg = f"Error reporting leaderboard: {str(e)}"
        record_battle_event(battle_context, error_msg)
        print(error_msg)


async def _send_prompts_to_agents(agents: list, prompt_template: str, log_message: str, timeout_seconds: int):
    """Helper to send a templated prompt to a list of agents."""
    if battle_context:
        record_battle_event(battle_context, log_message)
    
    messages = [prompt_template.format(id=agent.id, token=agent.token) for agent in agents]
    target_urls = [agent.url for agent in agents]
    await send_messages_to_agents(target_urls, messages, timeout_seconds)
