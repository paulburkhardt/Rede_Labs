#!/usr/bin/env python3
"""
Agent Launcher Script
Generates a scenario.toml and starts AgentBeats agents using tmux.
"""

import argparse
import subprocess
import sys
import os
import toml
from pathlib import Path
from typing import List, Dict
from datetime import datetime

# Base paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
AGENTS_DIR = PROJECT_ROOT / "agents"
TEMP_DIR = SCRIPT_DIR / "temp_agents"
TEMP_SCENARIO_PATH = SCRIPT_DIR / "scenario.toml"

# Default configuration
DEFAULT_MODEL_TYPE = os.getenv("MODEL_TYPE", "openai")
DEFAULT_MODEL_NAME = os.getenv("MODEL_NAME", "gpt-5-mini")
DEFAULT_TMUX_SESSION = "agentbeats-marketplace"

# Port configuration
GREEN_AGENT_PORT = int(os.getenv("GREEN_AGENT_PORT", "9110"))
GREEN_LAUNCHER_PORT = int(os.getenv("GREEN_LAUNCHER_PORT", "9115"))

# Buyer and seller port ranges
BUYER_BASE_PORT = int(os.getenv("BUYER_BASE_PORT", "9200"))
BUYER_LAUNCHER_BASE_PORT = int(os.getenv("BUYER_LAUNCHER_BASE_PORT", "9300"))

SELLER_BASE_PORT = int(os.getenv("SELLER_BASE_PORT", "10000"))
SELLER_LAUNCHER_BASE_PORT = int(os.getenv("SELLER_LAUNCHER_BASE_PORT", "10100"))


def check_tmux_installed() -> bool:
    """Check if tmux is installed."""
    try:
        subprocess.run(["tmux", "-V"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def check_tmux_session_exists(session_name: str) -> bool:
    """Check if a tmux session already exists."""
    try:
        result = subprocess.run(
            ["tmux", "has-session", "-t", session_name],
            capture_output=True,
            check=False
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def load_simulation_config() -> Dict:
    """Load the buyer simulation configuration."""
    config_path = AGENTS_DIR / "buyer" / "simulation_config.toml"
    if not config_path.exists():
        print(f"Error: {config_path} not found. Please create it.")
        exit(1)
    
    with open(config_path, 'r') as f:
        return toml.load(f)


def calculate_buyer_counts(config: Dict, total_buyers: int = None) -> Dict[str, int]:
    """Calculate how many buyers of each persona to spawn."""
    distribution = config.get("persona_distribution", {})
    
    if total_buyers is None:
        total_buyers = config.get("simulation_settings", {}).get("customers_per_run", 100)
    
    buyer_counts = {}
    remaining = total_buyers
    
    # Calculate counts based on percentages
    personas = list(distribution.items())
    for i, (persona, percentage) in enumerate(personas):
        if i == len(personas) - 1:
            # Last persona gets the remaining count to ensure exact total
            buyer_counts[persona] = remaining
        else:
            count = int(total_buyers * percentage / 100.0)
            buyer_counts[persona] = count
            remaining -= count
    
    return buyer_counts


def create_temp_agent_card(source_card: Path, agent_port: int, launcher_port: int, agent_name: str) -> Path:
    """
    Create a temporary agent card file with updated URL, host, and port.
    
    Args:
        source_card: Path to the original agent card
        agent_port: Port for the agent
        launcher_port: Port for the launcher
        agent_name: Name for the temporary file
        
    Returns:
        Path to the temporary agent card file
    """
    # Create temp directory if it doesn't exist
    TEMP_DIR.mkdir(exist_ok=True)
    
    # Read the source card as text
    with open(source_card, 'r') as f:
        card_content = f.read()
    
    # Replace the URL, host, and port values
    # This preserves the original formatting and structure
    import re
    card_content = re.sub(r'url\s*=\s*"[^"]*"', f'url = "http://localhost:{agent_port}"', card_content)
    card_content = re.sub(r'host\s*=\s*"[^"]*"', f'host = "0.0.0.0"', card_content)
    card_content = re.sub(r'port\s*=\s*\d+', f'port = {agent_port}', card_content)
    
    # Create a safe filename
    safe_name = agent_name.replace(" ", "_").replace("(", "").replace(")", "").lower()
    temp_card_path = TEMP_DIR / f"{safe_name}.toml"
    
    # Write the temporary card
    with open(temp_card_path, 'w') as f:
        f.write(card_content)
    
    return temp_card_path


def cleanup_temp_files():
    """Remove all temporary agent card files and the temp directory."""
    import shutil
    if TEMP_DIR.exists():
        shutil.rmtree(TEMP_DIR)
    if TEMP_SCENARIO_PATH.exists():
        TEMP_SCENARIO_PATH.unlink()


def generate_scenario_toml(
    include_green: bool,
    buyer_counts: Dict[str, int],
    num_sellers: int,
    model_type: str,
    model_name: str,
    tmux_session: str
) -> Dict:
    """Generate the scenario configuration."""
    
    scenario = {
        "scenario": {
            "name": "Marketplace Simulation",
            "description": "E-commerce marketplace with AI buyers and sellers",
            "version": "1.0.0"
        },
        "agents": [],
        "launch": {
            "mode": "tmux",
            "tmux_session_name": tmux_session,
            "startup_interval": 2,
            "wait_for_services": True
        }
    }
    
    # Add green agent if requested
    if include_green:
        green_card_source = AGENTS_DIR / "green_agent" / "green_agent_card.toml"
        green_tools_path = AGENTS_DIR / "green_agent" / "green_agent_tools.py"
        
        # Create temporary agent card with correct port/host
        temp_green_card = create_temp_agent_card(
            green_card_source,
            GREEN_AGENT_PORT,
            GREEN_LAUNCHER_PORT,
            "Green Agent (Orchestrator)"
        )
        
        green_agent = {
            "name": "Green Agent (Orchestrator)",
            "card": str(temp_green_card),
            "launcher_host": "0.0.0.0",
            "launcher_port": GREEN_LAUNCHER_PORT,
            "agent_host": "0.0.0.0",
            "agent_port": GREEN_AGENT_PORT,
            "model_type": model_type,
            "model_name": model_name,
        }
        if green_tools_path.exists():
            green_agent["tools"] = [str(green_tools_path)]
        
        scenario["agents"].append(green_agent)
    
    # Add buyer agents
    port_offset = 0
    for persona, count in buyer_counts.items():
        persona_file = AGENTS_DIR / "buyer" / f"persona_{persona}.toml"
        
        if not persona_file.exists():
            print(f"Warning: Persona file not found: {persona_file}, skipping...")
            continue
        
        for i in range(count):
            agent_port = BUYER_BASE_PORT + port_offset
            launcher_port = BUYER_LAUNCHER_BASE_PORT + port_offset
            agent_name = f"Buyer {port_offset + 1} ({persona})"
            
            # Create temporary agent card with correct port/host
            temp_buyer_card = create_temp_agent_card(
                persona_file,
                agent_port,
                launcher_port,
                agent_name
            )
            
            buyer_agent = {
                "name": agent_name,
                "card": str(temp_buyer_card),
                "launcher_host": "0.0.0.0",
                "launcher_port": launcher_port,
                "agent_host": "0.0.0.0",
                "agent_port": agent_port,
                "model_type": model_type,
                "model_name": model_name,
            }
            
            scenario["agents"].append(buyer_agent)
            port_offset += 1
    
    # Add seller agents
    seller_file = AGENTS_DIR / "seller" / "baseseller.toml"
    
    if seller_file.exists():
        for i in range(num_sellers):
            agent_port = SELLER_BASE_PORT + i
            launcher_port = SELLER_LAUNCHER_BASE_PORT + i
            agent_name = f"Seller {i + 1}"
            
            # Create temporary agent card with correct port/host
            temp_seller_card = create_temp_agent_card(
                seller_file,
                agent_port,
                launcher_port,
                agent_name
            )
            
            seller_agent = {
                "name": agent_name,
                "card": str(temp_seller_card),
                "launcher_host": "0.0.0.0",
                "launcher_port": launcher_port,
                "agent_host": "0.0.0.0",
                "agent_port": agent_port,
                "model_type": model_type,
                "model_name": model_name,
            }
            
            scenario["agents"].append(seller_agent)
    else:
        if num_sellers > 0:
            print(f"Warning: Seller file not found: {seller_file}")
    
    return scenario


def write_scenario_file(scenario: Dict, output_path: Path):
    """Write the scenario configuration to a TOML file."""
    with open(output_path, 'w') as f:
        # Write header
        f.write("# ============================================================================\n")
        f.write("# TEMPORARY SCENARIO FILE - Generated by start_agents.py\n")
        f.write(f"# Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("# DO NOT EDIT - This file will be deleted when agents are stopped\n")
        f.write("# ============================================================================\n\n")
        
        # Write scenario metadata
        f.write("[scenario]\n")
        for key, value in scenario["scenario"].items():
            if isinstance(value, str):
                f.write(f'{key} = "{value}"\n')
            else:
                f.write(f'{key} = {value}\n')
        f.write("\n")
        
        # Write agents
        f.write("# ============================================================================\n")
        f.write("# AGENTS\n")
        f.write("# ============================================================================\n\n")
        
        for agent in scenario["agents"]:
            f.write("[[agents]]\n")
            for key, value in agent.items():
                if isinstance(value, str):
                    f.write(f'{key} = "{value}"\n')
                elif isinstance(value, list):
                    # Handle tools array
                    f.write(f'{key} = {value}\n')
                else:
                    f.write(f'{key} = {value}\n')
            f.write("\n")
        
        # Write launch configuration
        f.write("# ============================================================================\n")
        f.write("# LAUNCH CONFIGURATION\n")
        f.write("# ============================================================================\n\n")
        f.write("[launch]\n")
        for key, value in scenario["launch"].items():
            if isinstance(value, str):
                f.write(f'{key} = "{value}"\n')
            elif isinstance(value, bool):
                f.write(f'{key} = {str(value).lower()}\n')
            else:
                f.write(f'{key} = {value}\n')


def start_agents_with_tmux(scenario_path: Path, tmux_session: str):
    """Start agents using agentbeats with the scenario file."""
    
    # Check if session already exists
    if check_tmux_session_exists(tmux_session):
        print(f"\nError: tmux session '{tmux_session}' already exists!")
        print(f"Please stop the existing session first:")
        print(f"  uv run tools/kill_agents.py")
        print(f"\nOr attach to the existing session:")
        print(f"  tmux attach -t {tmux_session}")
        sys.exit(1)
    
    # Find agentbeats - prefer venv version
    agentbeats_cmd = "agentbeats"
    venv_agentbeats = PROJECT_ROOT / "venv" / "bin" / "agentbeats"
    dot_venv_agentbeats = PROJECT_ROOT / ".venv" / "bin" / "agentbeats"
    
    if venv_agentbeats.exists():
        agentbeats_cmd = str(venv_agentbeats)
    elif dot_venv_agentbeats.exists():
        agentbeats_cmd = str(dot_venv_agentbeats)
    
    scenario_dir = scenario_path.parent

    # Start agents with agentbeats
    cmd = [agentbeats_cmd, "load_scenario", str(scenario_dir)]
    
    print(f"\nStarting agents with tmux session: {tmux_session}")
    print(f"Using: {agentbeats_cmd}")
    print(f"Command: {' '.join(cmd)}\n")
    
    try:
        subprocess.run(cmd, cwd=PROJECT_ROOT, check=True)
    except subprocess.CalledProcessError as e:
        print(f"\nError starting agents: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nStartup interrupted by user.")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Start AgentBeats agents using tmux sessions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start all agents (buyers and sellers)
  uv run tools/start_agents.py --only-white-agents
  
  # Start only buyers
  uv run tools/start_agents.py --only-buyers
  
  # Start only sellers
  uv run tools/start_agents.py --only-sellers
  
  # Start green agent
  uv run tools/start_agents.py --only-green-agent
  
  # Start specific number of buyers
  uv run tools/start_agents.py --only-buyers --num-buyers 50
  
  # Start with custom model
  uv run tools/start_agents.py --only-white-agents --model-type openai --model-name gpt-4-turbo
  
  # Attach to running session
  tmux attach -t agentbeats-marketplace
  
  # View logs in tmux
  # Use Ctrl+B then arrow keys to navigate between panes
  # Use Ctrl+B then [ to scroll (q to exit scroll mode)
        """
    )
    
    parser.add_argument(
        "--only-buyers",
        action="store_true",
        help="Start only buyer agents"
    )
    
    parser.add_argument(
        "--only-sellers",
        action="store_true",
        help="Start only seller agents"
    )
    
    parser.add_argument(
        "--only-green-agent",
        action="store_true",
        help="Start only the green agent (evaluation orchestrator)"
    )
    
    parser.add_argument(
        "--only-white-agents",
        action="store_true",
        help="Start both buyers and sellers (white agents)"
    )
    
    parser.add_argument(
        "--num-buyers",
        type=int,
        default=None,
        help="Number of buyer agents to start (default: from simulation_config.toml)"
    )
    
    parser.add_argument(
        "--num-sellers",
        type=int,
        default=1,
        help="Number of seller agents to start (default: 1)"
    )
    
    parser.add_argument(
        "--model-type",
        type=str,
        default=None,
        help=f"Model type to use (default: {DEFAULT_MODEL_TYPE})"
    )
    
    parser.add_argument(
        "--model-name",
        type=str,
        default=None,
        help=f"Model name to use (default: {DEFAULT_MODEL_NAME})"
    )
    
    parser.add_argument(
        "--tmux-session",
        type=str,
        default=DEFAULT_TMUX_SESSION,
        help=f"Name of the tmux session (default: {DEFAULT_TMUX_SESSION})"
    )
    
    args = parser.parse_args()
    
    # Check if tmux is installed
    if not check_tmux_installed():
        print("Error: tmux is not installed!")
        print("Please install tmux:")
        print("  macOS: brew install tmux")
        print("  Ubuntu/Debian: sudo apt-get install tmux")
        sys.exit(1)
    
    # Determine what to start
    start_buyers = args.only_buyers or args.only_white_agents
    start_sellers = args.only_sellers or args.only_white_agents
    start_green = args.only_green_agent
    
    # If nothing specified, show help
    if not (start_buyers or start_sellers or start_green):
        parser.print_help()
        print("\nError: Please specify which agents to start.")
        sys.exit(1)
    
    # Get model configuration
    model_type = args.model_type or DEFAULT_MODEL_TYPE
    model_name = args.model_name or DEFAULT_MODEL_NAME
    
    # Calculate buyer counts
    buyer_counts = {}
    if start_buyers:
        config = load_simulation_config()
        num_buyers = args.num_buyers or config.get("simulation_settings", {}).get("customers_per_run", 100)
        buyer_counts = calculate_buyer_counts(config, num_buyers)
        
        print(f"\nBuyer Configuration:")
        print(f"  Total buyers: {num_buyers}")
        print(f"  Distribution:")
        for persona, count in buyer_counts.items():
            percentage = (count / num_buyers * 100) if num_buyers > 0 else 0
            print(f"    - {persona}: {count} ({percentage:.1f}%)")
    
    # Seller configuration
    num_sellers = args.num_sellers if start_sellers else 0
    if num_sellers > 0:
        print(f"\nSeller Configuration:")
        print(f"  Total sellers: {num_sellers}")
    
    # Green agent configuration
    if start_green:
        print(f"\nGreen Agent: Enabled")
    
    # Generate scenario
    print(f"\nGenerating scenario configuration...")
    scenario = generate_scenario_toml(
        include_green=start_green,
        buyer_counts=buyer_counts,
        num_sellers=num_sellers,
        model_type=model_type,
        model_name=model_name,
        tmux_session=args.tmux_session
    )
    
    total_agents = len(scenario["agents"])
    print(f"  Total agents: {total_agents}")
    print(f"  Model: {model_type}/{model_name}")
    print(f"  Tmux session: {args.tmux_session}")
    
    # Write scenario file
    print(f"\nWriting scenario to: {TEMP_SCENARIO_PATH}")
    write_scenario_file(scenario, TEMP_SCENARIO_PATH)
    
    # Start agents
    print(f"\n{'='*60}")
    print(f"STARTING AGENTS")
    print(f"{'='*60}")
    
    start_agents_with_tmux(TEMP_SCENARIO_PATH, args.tmux_session)
    
    print(f"\n{'='*60}")
    print(f"AGENTS STARTED SUCCESSFULLY")
    print(f"{'='*60}")
    print(f"\nTmux session: {args.tmux_session}")
    print(f"Total agents: {total_agents}")
    print(f"\nUseful commands:")
    print(f"  Attach to session:  tmux attach -t {args.tmux_session}")
    print(f"  List sessions:      tmux ls")
    print(f"  Stop agents:        uv run tools/kill_agents.py")
    print(f"\nTmux navigation:")
    print(f"  Switch panes:       Ctrl+B then arrow keys")
    print(f"  Scroll mode:        Ctrl+B then [ (press q to exit)")
    print(f"  Detach session:     Ctrl+B then d")
    print(f"\n")


if __name__ == "__main__":
    main()
