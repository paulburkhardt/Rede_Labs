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

sellers : list[Seller] = []
buyers : list[Buyer] = []

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

    days: int = 5  # Total days in the battle
    print("🌴 Battle orchestration started")
    try:
        print("🌴 Creating sellers and buyer")
        await create_sellers(seller_infos)
        print("🌴 Created sellers")
        await create_buyer()
        print("🌴 Created buyer")
        print(sellers)
        print(buyers)

        # Day 1: Create listings
        await create_listings()
        await create_ranking()
        await buyers_buy_products()

        for i in range(days - 1):
            await update_ranking()
            await sellers_update_listings()
            await buyers_buy_products()
        
    except Exception as e:
        error_msg = f"Error orchestrating battle: {str(e)}"
        record_battle_event(battle_context, error_msg)
        return error_msg
    
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
        agent for agent in scenario_config.get("agents", [])
        if Path(agent["card"]).name.startswith("buyer_")
    ]
    
    # Create buyers based on the configuration
    for buyer_agent in buyer_agents:
        agent_host = buyer_agent.get("agent_host")
        agent_port = buyer_agent.get("agent_port")
        
        if not agent_port:
            raise Exception(f"No agent_port found for buyer agent: {buyer_agent.get('name')}")
        
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
        buyers.append(Buyer(id=buyer_data.get("id"), url=url, token=buyer_data.get("auth_token")))

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
                send_message_to_agent(seller.url, prompt),
                timeout=timeout_seconds
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
    # Get all products and assign random rankings
    response = requests.get(f"{api_url}/search?q=")
    if response.status_code != 200:
        raise Exception(f"Failed to get products: {response.text}")
    
    products = response.json()
    random_ranking = list(range(1, len(products) + 1))
    random.shuffle(random_ranking)
    
    # Prepare batch update payload
    rankings = [
        {"product_id": product["id"], "ranking": random_ranking[i]}
        for i, product in enumerate(products)
    ]
    
    # Update all rankings in one call
    update_response = requests.patch(
        f"{api_url}/product/batch/rankings",
        json={"rankings": rankings}
    )
    if update_response.status_code != 200:
        raise Exception(f"Failed to set initial rankings: {update_response.text}")



async def update_ranking():
    # Query sales data and update product rankings
    response = requests.get(
        api_url + "/buy/stats/by-seller",
    )
    if response.status_code != 200:
        raise Exception(f"Failed to get sales stats: {response.text}")
    sales_stats = response.json()
    
    # Sort by number of purchases
    sorted_stats = sorted(sales_stats, key=lambda x: x["purchase_count"], reverse=True)
    
    # Prepare batch update payload
    rankings = []
    for rank, stat in enumerate(sorted_stats, start=1):
        seller_id = stat["seller_id"]
        # Get all products for this seller
        response = requests.get(f"{api_url}/search?seller_id={seller_id}")
        if response.status_code == 200:
            products = response.json()
            for product in products:
                rankings.append({"product_id": product["id"], "ranking": rank})
    
    # Update all rankings in one call
    if rankings:
        update_response = requests.patch(
            f"{api_url}/product/batch/rankings",
            json={"rankings": rankings}
        )
        if update_response.status_code != 200:
            print(f"Warning: Failed to update rankings: {update_response.text}")



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
                send_message_to_agent(buyer.url, prompt),
                timeout=timeout_seconds
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
                send_message_to_agent(seller.url, prompt),
                timeout=timeout_seconds
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
                "score": score
            }
            
            record_battle_event(
                battle_context, 
                f"Seller {seller_id}: ${entry['total_revenue_dollars']:.2f} revenue, {purchase_count} purchases"
            )
            
            if score > winner_score:
                winner_score = score
                winner = seller_id
        
        # Step 3: Report final result
        result_detail = {
            "leaderboard": leaderboard_data,
            "scores": scores,
            "winner": winner,
            "winner_revenue": winner_score / 100.0 if winner_score else 0
        }
        
        record_battle_result(
            battle_context,
            f"Battle completed - Winner: {winner} with ${winner_score / 100.0:.2f} total revenue",
            result_detail
        )
        
    except Exception as e:
        error_msg = f"Error reporting leaderboard: {str(e)}"
        record_battle_event(battle_context, error_msg)
        print(error_msg)