#!/usr/bin/env python3
"""
Green Agent A2A Server
Direct A2A server for the green agent, following the chess-green-agent pattern.
"""

import os
import sys
import uvicorn
import tomllib
from pathlib import Path
from dotenv import load_dotenv

# Add agents directory to path for imports
PROJECT_ROOT = Path(__file__).parent
AGENTS_DIR = PROJECT_ROOT / "agents"
GREEN_AGENT_DIR = AGENTS_DIR / "green_agent"

if str(AGENTS_DIR) not in sys.path:
    sys.path.insert(0, str(AGENTS_DIR))

load_dotenv(PROJECT_ROOT / ".env")


def load_agent_card_toml():
    """Load the green agent card from TOML file."""
    card_path = GREEN_AGENT_DIR / "green_agent_card.toml"
    with open(card_path, "rb") as f:
        return tomllib.load(f)


def create_green_agent_app(host: str = "0.0.0.0", port: int = 9110):
    """Create the A2A application for the green agent."""
    from a2a.server.apps import A2AStarletteApplication
    from a2a.server.request_handlers import DefaultRequestHandler
    from a2a.server.agent_execution import AgentExecutor, RequestContext
    from a2a.server.events import EventQueue
    from a2a.server.tasks import InMemoryTaskStore
    from a2a.types import AgentCard
    from a2a.utils import new_agent_text_message
    
    # Import the green agent tools
    sys.path.insert(0, str(GREEN_AGENT_DIR))
    import green_agent_tools
    
    class GreenAgentExecutor(AgentExecutor):
        """Executor for the green agent - handles incoming messages."""
        
        def __init__(self):
            pass
        
        async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
            """Handle incoming messages by calling the green agent tools."""
            print("Green agent: Received a task, parsing...")
            user_input = context.get_user_input()
            
            try:
                # Call the handle_incoming_message tool from green_agent_tools
                if hasattr(green_agent_tools, 'handle_incoming_message'):
                    result = green_agent_tools.handle_incoming_message(user_input)
                else:
                    result = f"Green agent received: {user_input}\nTools available: {dir(green_agent_tools)}"
                
                await event_queue.enqueue_event(
                    new_agent_text_message(str(result))
                )
            except Exception as e:
                await event_queue.enqueue_event(
                    new_agent_text_message(f"Error: {e}")
                )
        
        async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
            raise NotImplementedError
    
    # Load agent card
    agent_card_dict = load_agent_card_toml()
    agent_card_dict["url"] = f"http://{host}:{port}"
    
    # Create request handler
    request_handler = DefaultRequestHandler(
        agent_executor=GreenAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )
    
    # Create A2A application
    app = A2AStarletteApplication(
        agent_card=AgentCard(**agent_card_dict),
        http_handler=request_handler,
    )
    
    return app.build()


def start_green_agent(host: str = "0.0.0.0", port: int = 9110):
    """Start the green agent server."""
    print(f"Starting green agent on http://{host}:{port}")
    app = create_green_agent_app(host, port)
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    port = int(os.getenv("GREEN_AGENT_PORT", "9110"))
    start_green_agent(host="0.0.0.0", port=port)
