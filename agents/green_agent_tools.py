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

# Global state to store battle context
battle_context = None

api_url = "http://localhost:8000"


from typing import NamedTuple


class Seller(NamedTuple):
    id: str
    url: str
    token: str

class Buyer(NamedTuple):
    id: str
    url: str
    token: str

class ProductImage(NamedTuple):
    url: str
    alternative_text: str

sellers : list[Seller] = []
buyers : list[Buyer] = []

product_images: list[ProductImage] = [
    ProductImage(url="https://example.com/image1.jpg", alternative_text="Image 1"),
    ProductImage(url="https://example.com/image2.jpg", alternative_text="Image 2"),
    ProductImage(url="https://example.com/image3.jpg", alternative_text="Image 3"),
]

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
    from agentbeats.utils.agents import send_message_to_agent
    from agentbeats.logging import record_battle_event, record_battle_result

    global battle_context, sellers, buyers

    if not battle_context:
        record_battle_event(battle_context, "Battle orchestration started")

        return "Error: Battle context not initialized"

    try:
        await create_sellers(seller_infos)
        await create_buyer()



        return "Battle orchestration started"

    except Exception as e:
        error_msg = f"Error orchestrating battle: {str(e)}"
        record_battle_event(battle_context, error_msg)
        return error_msg


async def create_sellers(seller_infos: list):
    await create_participants(len(seller_infos), "/createSeller")


async def create_buyer():
    await create_participants(5, "/createBuyer")

async def create_participants(no_participants: int, route: str):
    for i in range(no_participants):
        # todo: add super admin auth token
        response = requests.post(
            api_url + route,
        )
        if response.status_code != 200:
            raise Exception(f"Failed to create seller: {response.text}")
        
        # todo: confirm if that actually works
        if route == "/createSeller":
            sellers.append(response.json())
        elif route == "/createBuyer":
            buyers.append(response.json())

        return response.json()

async def create_products():
    for seller in sellers:
        prompt = "todo"
        await send_message_to_agent(seller["url"], prompt)