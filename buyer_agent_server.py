#!/usr/bin/env python3
"""
Buyer Agent A2A Server
Direct A2A server for buyer agents.
"""

import os
import sys
import uvicorn
import tomllib
import argparse
import importlib.util
from pathlib import Path
from dotenv import load_dotenv

# Add agents directory to path for imports
PROJECT_ROOT = Path(__file__).parent
AGENTS_DIR = PROJECT_ROOT / "agents"
BUYER_DIR = AGENTS_DIR / "buyer"

if str(AGENTS_DIR) not in sys.path:
    sys.path.insert(0, str(AGENTS_DIR))

load_dotenv(PROJECT_ROOT / ".env")


def load_agent_card_toml(card_path: Path):
    """Load the agent card from TOML file."""
    with open(card_path, "rb") as f:
        return tomllib.load(f)


def load_tools_module(tools_path: Path):
    """Dynamically load the tools module."""
    spec = importlib.util.spec_from_file_location("buyer_tools", tools_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["buyer_tools"] = module
    spec.loader.exec_module(module)
    return module


def create_buyer_agent_app(card_path: Path, tools_path: Path, host: str, port: int):
    """Create the A2A application for the buyer agent."""
    from a2a.server.apps import A2AStarletteApplication
    from a2a.server.request_handlers import DefaultRequestHandler
    from a2a.server.agent_execution import AgentExecutor, RequestContext
    from a2a.server.events import EventQueue
    from a2a.server.tasks import InMemoryTaskStore
    from a2a.types import AgentCard
    from a2a.utils import new_agent_text_message
    
    # Load tools
    tools_module = load_tools_module(tools_path)
    
    class BuyerAgentExecutor(AgentExecutor):
        """Executor for the buyer agent."""
        
        def __init__(self):
            pass
        
        async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
            """Handle incoming messages."""
            # For buyer agents, the logic is usually handled by the A2A framework calling tools
            # But if we receive a direct message, we can just acknowledge it
            user_input = context.get_user_input()
            print(f"Buyer agent received: {user_input}")
            
            # In a real scenario, we might want to parse the input and call a specific tool
            # For now, we'll just return a generic response or try to use a tool if requested
            
            await event_queue.enqueue_event(
                new_agent_text_message(f"Received: {user_input}")
            )
        
        async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
            raise NotImplementedError
    
    # Load agent card
    agent_card_dict = load_agent_card_toml(card_path)
    agent_card_dict["url"] = f"http://{host}:{port}"
    
    # Create request handler
    request_handler = DefaultRequestHandler(
        agent_executor=BuyerAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )
    
    # Create A2A application
    app = A2AStarletteApplication(
        agent_card=AgentCard(**agent_card_dict),
        http_handler=request_handler,
    )
    
    # Register tools with the app (if A2A supports direct tool registration this way)
    # Note: The current A2A SDK might handle tools differently (via the agent card definition)
    # The tools in shared_tools.py are decorated with @ab.tool, which we mocked.
    # In a full implementation, we'd need to ensure these tools are exposed to the LLM.
    # However, for this benchmark, the "agent" is often just the tools + LLM loop.
    # Since we are replacing the 'agentbeats run' command which sets up that loop,
    # we are effectively creating a "dumb" agent here that just exposes the API.
    # BUT, the user wants the AGENT to run.
    # The 'agentbeats run' command usually starts an agent that *uses* an LLM.
    # Our simple Executor above doesn't use an LLM.
    
    # WAIT! The 'agentbeats run' command starts an agent that uses the configured LLM (OpenAI etc).
    # If I replace it with this simple Executor, the agent won't actually DO anything intelligent!
    # It won't call the LLM.
    
    # The chess-green-agent example implements its own logic in the Executor.
    # For the buyer agents, they are supposed to be generic LLM agents that use the tools defined in the TOML.
    
    # If I can't use 'agentbeats run' because of the CLI error, I need to instantiate the 
    # STANDARD AgentBeats agent class, not a custom empty one.
    
    # Let's check if we can import the standard agent implementation from agentbeats (the new one).
    # The new agentbeats has `agentbeats.agents.Agent`.
    
    return app.build()


def start_buyer_agent():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--persona", type=str, required=True)
    parser.add_argument("--tools", type=str, required=True)
    args = parser.parse_args()
    
    host = "0.0.0.0"
    
    print(f"Starting buyer agent on http://{host}:{args.port}")
    print(f"Persona: {args.persona}")
    
    # For now, let's try to use the A2A app structure. 
    # If this doesn't provide LLM capabilities, we might need a different approach.
    # But getting the server running is step 1.
    
    app = create_buyer_agent_app(Path(args.persona), Path(args.tools), host, args.port)
    uvicorn.run(app, host=host, port=args.port)


if __name__ == "__main__":
    start_buyer_agent()
