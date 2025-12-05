#!/usr/bin/env python3
"""
Unified Agent Starter
Starts all agents (green + white) with prefixed output in a single terminal.
Bypasses tmux completely by running agents as subprocesses.
"""

import os
import sys
import subprocess
import signal
import threading
import time
from pathlib import Path
from dotenv import load_dotenv

# Colors for different agents
COLORS = {
    "GREEN": "\033[92m",      # Bright green
    "BUYER_1": "\033[94m",    # Blue
    "BUYER_2": "\033[95m",    # Magenta
    "BUYER_3": "\033[96m",    # Cyan
    "BUYER_4": "\033[93m",    # Yellow
    "BUYER_5": "\033[91m",    # Red
    "SYSTEM": "\033[90m",     # Gray
    "RESET": "\033[0m",
}

PROJECT_ROOT = Path(__file__).parent
load_dotenv(PROJECT_ROOT / ".env")

# Track all processes
processes = []
shutdown_event = threading.Event()


def prefix_output(process, prefix: str, color: str):
    """Read process output and print with prefix."""
    reset = COLORS["RESET"]
    try:
        for line in iter(process.stdout.readline, ""):
            if shutdown_event.is_set():
                break
            if line:
                # Filter out some noisy logs if needed
                if "GET /info" in line or "GET /status" in line:
                    continue
                print(f"{color}[{prefix}]{reset} {line}", end="", flush=True)
    except Exception:
        pass


def start_agent_process(name: str, cmd: list, color: str, cwd: Path = None, env: dict = None):
    """Start an agent process and capture its output."""
    print(f"{COLORS['SYSTEM']}[SYSTEM]{COLORS['RESET']} Starting {name}...")
    
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        cwd=cwd or PROJECT_ROOT,
        env=env or os.environ.copy(),
        bufsize=1,
    )
    processes.append(process)
    
    # Start thread to read output
    thread = threading.Thread(target=prefix_output, args=(process, name, color), daemon=True)
    thread.start()
    
    return process


def cleanup(signum=None, frame=None):
    """Clean up all processes."""
    print(f"\n{COLORS['SYSTEM']}[SYSTEM]{COLORS['RESET']} Shutting down all agents...")
    shutdown_event.set()
    
    for p in processes:
        try:
            p.terminate()
            p.wait(timeout=3)
        except Exception:
            try:
                p.kill()
            except Exception:
                pass
    
    # Kill any remaining agentbeats
    subprocess.run(["pkill", "-f", "agentbeats"], capture_output=True)
    subprocess.run(["tmux", "kill-session", "-t", "agentbeats-marketplace"], capture_output=True)
    
    print(f"{COLORS['SYSTEM']}[SYSTEM]{COLORS['RESET']} Cleanup complete")
    sys.exit(0)


def start_white_agents():
    """Start white agents using our direct A2A server."""
    buyer_dir = PROJECT_ROOT / "agents" / "buyer"
    shared_tools = buyer_dir / "shared_tools.py"
    
    # Buyer distribution (5 agents)
    personas = [
        "persona_price_conscious.toml",
        "persona_confused_overchoice.toml",
        "persona_hedonistic_shopper.toml",
        "persona_brand_conscious.toml",
        "persona_brand_conscious.toml"
    ]
    
    base_port = 9000
    
    for i, persona_file in enumerate(personas):
        agent_name = f"BUYER_{i+1}"
        color = COLORS.get(agent_name, COLORS["SYSTEM"])
        port = base_port + i
        
        card_path = buyer_dir / persona_file
        
        # Use our direct A2A server
        cmd = [
            "uv", "run", "buyer_agent_server.py",
            "--port", str(port),
            "--persona", str(card_path),
            "--tools", str(shared_tools)
        ]
        
        start_agent_process(agent_name, cmd, color, cwd=PROJECT_ROOT)
        time.sleep(1)  # Stagger start


def start_green_agent():
    """Start the green agent using our direct A2A server."""
    port = int(os.getenv("GREEN_AGENT_PORT", "9110"))
    
    # Use our direct A2A server
    cmd = ["uv", "run", "green_agent_server.py"]
    
    print(f"{COLORS['SYSTEM']}[SYSTEM]{COLORS['RESET']} Green agent will be at http://localhost:{port}")
    
    return start_agent_process("GREEN", cmd, COLORS["GREEN"], cwd=PROJECT_ROOT)


def main():
    # Set up signal handlers
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)
    
    print(f"\n{COLORS['SYSTEM']}[SYSTEM]{COLORS['RESET']} Starting Marketplace Agents (Unified Terminal)...")
    print(f"{COLORS['SYSTEM']}[SYSTEM]{COLORS['RESET']} " + "=" * 50)
    
    # Start white agents first
    start_white_agents()
    
    # Wait for white agents to initialize
    print(f"{COLORS['SYSTEM']}[SYSTEM]{COLORS['RESET']} Waiting for white agents (3s)...")
    time.sleep(3)
    
    # Start green agent
    green_proc = start_green_agent()
    
    if green_proc:
        print(f"\n{COLORS['SYSTEM']}[SYSTEM]{COLORS['RESET']} All agents running!")
        print(f"{COLORS['SYSTEM']}[SYSTEM]{COLORS['RESET']} Green agent: http://localhost:9110")
        print(f"{COLORS['SYSTEM']}[SYSTEM]{COLORS['RESET']} Press Ctrl+C to stop\n")
        
        try:
            green_proc.wait()
        except KeyboardInterrupt:
            cleanup()
    else:
        print(f"{COLORS['SYSTEM']}[SYSTEM]{COLORS['RESET']} Green agent failed to start")
        cleanup()


if __name__ == "__main__":
    main()
