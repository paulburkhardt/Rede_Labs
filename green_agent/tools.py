# -*- coding: utf-8 -*-
"""
MarketArena Green Agent Tools
"""

import httpx
import agentbeats as ab
import requests
from uuid import uuid4
from typing import List, Dict
from a2a.client import A2AClient, A2ACardResolver
from a2a.types import (
    AgentCard, Message, Part, TextPart, Role,
    SendStreamingMessageRequest,
    SendStreamingMessageSuccessResponse,
    MessageSendParams,
    TaskArtifactUpdateEvent,
    TaskStatusUpdateEvent,
)

MARKETPLACE_URL = "http://localhost:8100"


@ab.tool
async def talk_to_agent(query: str, target_url: str) -> str:
    """
    Send A2A message to any agent (white or customer).
    
    Args:
        query: Message to send
        target_url: Agent URL (e.g., http://localhost:9125)
    
    Returns:
        Agent's response
    """
    httpx_client = httpx.AsyncClient()
    resolver = A2ACardResolver(httpx_client=httpx_client, base_url=target_url)
    card: AgentCard | None = await resolver.get_agent_card(
        relative_card_path="/.well-known/agent.json"
    )
    if card is None:
        raise RuntimeError(f"Failed to resolve agent card from {target_url}")

    client = A2AClient(httpx_client=httpx_client, agent_card=card)

    params = MessageSendParams(
        message=Message(
            role=Role.user,
            parts=[Part(TextPart(text=query))],
            messageId=uuid4().hex,
            taskId=None,
        )
    )
    req = SendStreamingMessageRequest(id=str(uuid4()), params=params)
    chunks: List[str] = []

    async for chunk in client.send_message_streaming(req):
        if not isinstance(chunk.root, SendStreamingMessageSuccessResponse):
            continue
        event = chunk.root.result
        if isinstance(event, TaskArtifactUpdateEvent):
            for p in event.artifact.parts:
                if isinstance(p.root, TextPart):
                    chunks.append(p.root.text)
        elif isinstance(event, TaskStatusUpdateEvent):
            msg = event.status.message
            if msg:
                for p in msg.parts:
                    if isinstance(p.root, TextPart):
                        chunks.append(p.root.text)

    return "".join(chunks).strip() or "No response from agent."


@ab.tool
def reset_marketplace() -> str:
    """Reset marketplace to clean state"""
    try:
        response = requests.post(f"{MARKETPLACE_URL}/admin/reset")
        response.raise_for_status()
        result = response.json()
        return f"Marketplace reset successfully. {result}"
    except Exception as e:
        return f"Error resetting marketplace: {str(e)}"


@ab.tool
def start_edit_phase() -> str:
    """Start edit phase (sellers can update listings)"""
    try:
        response = requests.post(f"{MARKETPLACE_URL}/admin/start_edit_phase")
        response.raise_for_status()
        result = response.json()
        return f"Edit phase started. Day {result.get('day')}. {result}"
    except Exception as e:
        return f"Error starting edit phase: {str(e)}"


@ab.tool
def start_buy_phase() -> str:
    """Start buy phase (customers can purchase)"""
    try:
        response = requests.post(f"{MARKETPLACE_URL}/admin/start_buy_phase")
        response.raise_for_status()
        result = response.json()
        return f"Buy phase started. {result}"
    except Exception as e:
        return f"Error starting buy phase: {str(e)}"


@ab.tool
def get_revenue_stats() -> str:
    """Get current revenue statistics"""
    try:
        response = requests.get(f"{MARKETPLACE_URL}/admin/stats")
        response.raise_for_status()
        stats = response.json()
        
        import json
        return json.dumps(stats, indent=2)
    except Exception as e:
        return f"Error fetching stats: {str(e)}"


@ab.tool
def get_product_rankings(category: str = "towel") -> str:
    """Get current product rankings"""
    try:
        response = requests.get(f"{MARKETPLACE_URL}/search", params={"q": category})
        response.raise_for_status()
        products = response.json()
        
        import json
        return json.dumps(products, indent=2)
    except Exception as e:
        return f"Error fetching rankings: {str(e)}"


@ab.tool
async def broadcast_to_customers(message: str) -> str:
    """
    Broadcast message to all customer agents.
    
    Args:
        message: Message to send
    
    Returns:
        Summary of responses
    """
    customer_urls = [
        "http://localhost:9125",  # Price Optimizer
        "http://localhost:9135",  # Quality Seeker
        "http://localhost:9145",  # Top Rank Buyer
        "http://localhost:9155",  # Balanced Buyer
    ]
    
    responses = []
    for i, url in enumerate(customer_urls, 1):
        try:
            response = await talk_to_agent(message, url)
            responses.append(f"Customer {i}: {response}")
        except Exception as e:
            responses.append(f"Customer {i}: Error - {str(e)}")
    
    return "\n\n".join(responses)


def format_leaderboard_markdown(stats: Dict) -> str:
    """Helper: Format stats as markdown table"""
    if "sellers" not in stats:
        return "No seller data"
    
    sellers = sorted(stats["sellers"], key=lambda x: x["total_revenue"], reverse=True)
    
    md = "### Current Leaderboard\n\n"
    md += "| Rank | Seller | Total Revenue | Units Sold | Avg Price |\n"
    md += "|------|--------|---------------|------------|----------|\n"
    
    for i, seller in enumerate(sellers, 1):
        name = seller.get("name", "Unknown")
        revenue = seller.get("total_revenue", 0) / 100
        units = seller.get("units_sold", 0)
        avg = seller.get("avg_price", 0) / 100 if units > 0 else 0
        
        md += f"| {i} | {name} | ${revenue:.2f} | {units} | ${avg:.2f} |\n"
    
    total_revenue = stats.get("marketplace_totals", {}).get("total_revenue", 0) / 100
    total_units = stats.get("marketplace_totals", {}).get("total_units_sold", 0)
    md += f"\n**Marketplace Total**: ${total_revenue:.2f} ({total_units} units sold)\n"
    
    return md
