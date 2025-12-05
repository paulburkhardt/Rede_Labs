"""
Battle Logger Utility

Provides centralized logging for battle events across all agent tools.
This module maintains a global battle context that can be accessed by
buyer and seller shared tools to log their actions.

NOTE: This is a standalone implementation that does NOT depend on agentbeats.
"""

from typing import Optional, Any
import datetime

class BattleContext:
    """Standalone battle context."""
    def __init__(self, battle_id: str, backend_url: str, agent_name: str):
        self.battle_id = battle_id
        self.backend_url = backend_url
        self.agent_name = agent_name

_battle_context: Optional[BattleContext] = None


def set_battle_context(context: Optional[BattleContext]):
    """
    Set the global battle context for logging.
    
    Args:
        context: BattleContext instance or None to clear
    """
    global _battle_context
    _battle_context = context


def get_battle_context() -> Optional[BattleContext]:
    """
    Get the current battle context.
    
    Returns:
        The current BattleContext or None if not set
    """
    return _battle_context


def log_battle_event(message: str):
    """
    Log a battle event if context is available.
    Does nothing if battle context is not set.
    
    Args:
        message: The event message to log
    """
    if _battle_context:
        # Just print to stdout - main.py captures this and prefixes it
        # Format: [BATTLE_EVENT] <message>
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        print(f"[BATTLE] {message}")


def log_tool_request(tool_name: str, **kwargs):
    """
    Log a tool request with its parameters.
    
    Args:
        tool_name: Name of the tool being called
        **kwargs: Tool parameters (sensitive data like tokens will be masked)
    """
    if not _battle_context:
        return
    
    # Mask sensitive data
    safe_kwargs = {}
    for key, value in kwargs.items():
        if 'token' in key.lower() or 'auth' in key.lower():
            safe_kwargs[key] = "***"
        else:
            safe_kwargs[key] = value
    
    params_str = ", ".join(f"{k}={v}" for k, v in safe_kwargs.items())
    log_battle_event(f"🔧 {tool_name}({params_str})")


def log_tool_response(tool_name: str, success: bool, summary: str):
    """
    Log a tool response.
    
    Args:
        tool_name: Name of the tool
        success: Whether the operation succeeded
        summary: Brief summary of the result
    """
    if not _battle_context:
        return
    
    status = "✅" if success else "❌"
    log_battle_event(f"{status} {tool_name}: {summary}")
