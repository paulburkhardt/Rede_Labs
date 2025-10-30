# Agent Management Tools

This directory contains scripts to manage AgentBeats agents for the marketplace simulation using **tmux sessions**.

## Overview

The scripts generate a temporary `scenario.toml` file with all agent configurations and launch them in a tmux session. This approach provides:
- **Better log visibility**: Each agent runs in its own tmux pane
- **Easy monitoring**: Navigate between agents to see their logs
- **Clean configuration**: Ports and hosts are properly set in the scenario file
- **Simple cleanup**: Stop all agents and remove temp files with one command

## Scripts

### `start_agents.py`

Generates a `scenario.toml` and starts agents in a tmux session.

#### Usage

```bash
# Start ALL agents (green, buyers, and sellers) - DEFAULT
uv run tools/start_agents.py

# Start only white agents (buyers and sellers)
uv run tools/start_agents.py --only-white-agents

# Start only buyer agents
uv run tools/start_agents.py --only-buyers

# Start only seller agents
uv run tools/start_agents.py --only-sellers

# Start green agent (evaluation orchestrator)
uv run tools/start_agents.py --only-green-agent

# Start specific number of buyers
uv run tools/start_agents.py --only-buyers --num-buyers 50

# Start with custom model
uv run tools/start_agents.py --only-white-agents --model-type openai --model-name gpt-4-turbo

# Start with custom tmux session name
uv run tools/start_agents.py --only-white-agents --tmux-session my-simulation
```

#### Arguments

- `--only-buyers`: Start only buyer agents
- `--only-sellers`: Start only seller agents
- `--only-green-agent`: Start only the green agent (evaluation orchestrator)
- `--only-white-agents`: Start both buyers and sellers
- `--num-buyers N`: Number of buyer agents to start (default: from `simulation_config.toml`)
- `--num-sellers N`: Number of seller agents to start (default: 1)
- `--model-type TYPE`: Model type to use (default: from `MODEL_TYPE` env var or "openai")
- `--model-name NAME`: Model name to use (default: from `MODEL_NAME` env var or "gpt-4o-mini")
- `--tmux-session NAME`: Name of the tmux session (default: "agentbeats-marketplace")

#### What It Does

1. Reads buyer distribution from `agents/buyer/simulation_config.toml`
2. Discovers and assigns tools files for each agent (see Tools Discovery below)
3. Creates temporary agent card files with correct ports and hosts
4. Generates a `scenario.toml` with all agent configurations
5. Launches agents using `agentbeats load_scenario`
6. Creates a tmux session with one pane per agent

#### Default Behavior

**If no flags are specified, ALL agents are started** (green agent, buyers, and sellers). This is the most common use case for running a full simulation.

#### Tools Discovery

The script automatically finds and assigns tools files for buyers and sellers:

1. **Shared tools**: If a `shared_*.py` file exists in the agent folder (e.g., `agents/buyer/shared_tools.py`), it's used for all agents in that folder
2. **Agent-specific tools**: If a `{agent_id}_tools.py` file exists (e.g., `persona_price_tools.py`), it overrides the shared tools for that specific agent
3. **Prefix matching**: The script tries prefix matches (e.g., `persona_price_tools.py` matches `persona_price_conscious.toml`)

Example:
- `agents/buyer/shared_buyer_tools.py` → Used by all buyers
- `agents/buyer/persona_price_tools.py` → Used only by price-conscious buyers (overrides shared)
- `agents/seller/shared_seller_tools.py` → Used by all sellers

#### Buyer Distribution

The script reads `agents/buyer/simulation_config.toml` to determine:
- Total number of buyers to spawn (default: 100)
- Distribution of buyer personas based on percentages

Example distribution:
- Price Conscious: 35%
- Quality Seeker: 25%
- Confused by Overchoice: 20%
- Hedonistic Shopper: 12%
- Brand Conscious: 8%

---

### `kill_agents.py`

Stops the tmux session and cleans up the temporary scenario file.

#### Usage

```bash
# Stop agents with default session name
uv run tools/kill_agents.py

# Stop agents with custom session name
uv run tools/kill_agents.py --tmux-session my-simulation

# List all tmux sessions
uv run tools/kill_agents.py --list

# Force cleanup even if session doesn't exist
uv run tools/kill_agents.py --force

# Keep the temp scenario file (for debugging)
uv run tools/kill_agents.py --keep-scenario
```

#### Arguments

- `--tmux-session NAME`: Name of the tmux session to kill (default: "agentbeats-marketplace")
- `--list`: List all active tmux sessions and exit
- `--force`: Force cleanup even if session doesn't exist
- `--keep-scenario`: Keep the temporary scenario.toml file (don't delete it)

#### What It Does

1. Checks if the tmux session exists
2. Kills the tmux session (stops all agents)
3. Deletes the `scenario.toml` file
4. Reports cleanup status

---

## Tmux Navigation

Once agents are running, you can attach to the tmux session to view logs:

```bash
# Attach to the session
tmux attach -t agentbeats-marketplace

# Detach from session (agents keep running)
Ctrl+B then d

# Navigate between panes
Ctrl+B then arrow keys

# Enter scroll mode (to view logs)
Ctrl+B then [
# Use arrow keys or Page Up/Down to scroll
# Press q to exit scroll mode

# Zoom into a pane (fullscreen)
Ctrl+B then z
# Press again to zoom out

# List all sessions
tmux ls

# Kill session from outside
tmux kill-session -t agentbeats-marketplace
```

---

## Port Configuration

Ports can be configured via environment variables:

```bash
# Green agent
export GREEN_AGENT_PORT=9110
export GREEN_LAUNCHER_PORT=9115

# Buyers (base ports, incremented for each agent)
export BUYER_BASE_PORT=9200
export BUYER_LAUNCHER_BASE_PORT=9300

# Sellers (base ports, incremented for each agent)
export SELLER_BASE_PORT=10000
export SELLER_LAUNCHER_BASE_PORT=10100
```

Default ports:
- **Green Agent**: 9110 (agent), 9115 (launcher)
- **Buyers**: 9200-9399 (agents), 9300-9499 (launchers)
- **Sellers**: 10000-10099 (agents), 10100-10199 (launchers)

---

## Examples

### Full Simulation Workflow

```bash
# 1. Start all agents for simulation
uv run tools/start_agents.py --only-white-agents --num-buyers 100 --num-sellers 2

# 2. Attach to tmux to monitor logs
tmux attach -t agentbeats-marketplace

# 3. Detach from tmux (Ctrl+B then d)

# 4. Run your simulation/tests
# ... your simulation code ...

# 5. Kill all agents when done
uv run tools/kill_agents.py
```

### Development Workflow

```bash
# Start only a few buyers for testing
uv run tools/start_agents.py --only-buyers --num-buyers 5

# Attach to view logs
tmux attach -t agentbeats-marketplace

# Stop when done
uv run tools/kill_agents.py
```

### Green Agent Testing

```bash
# Start green agent for evaluation
uv run tools/start_agents.py --only-green-agent

# Test evaluation logic
# ...

# Kill green agent
uv run tools/kill_agents.py
```

### Multiple Simulations

```bash
# Start first simulation
uv run tools/start_agents.py --only-white-agents --tmux-session sim1

# Start second simulation (different session)
uv run tools/start_agents.py --only-white-agents --tmux-session sim2

# List all sessions
uv run tools/kill_agents.py --list

# Kill specific simulation
uv run tools/kill_agents.py --tmux-session sim1
```

---

## Temporary Files

The scripts create a temporary file:
- `tools/scenario.toml`: Generated scenario configuration

This file is automatically deleted when you run `kill_agents.py`. If you want to keep it for debugging, use the `--keep-scenario` flag.

---

## Troubleshooting

### Agents won't start

- **Check tmux is installed**: `tmux -V`
  - macOS: `brew install tmux`
  - Ubuntu/Debian: `sudo apt-get install tmux`
- **Check agentbeats is installed**: `pip install agentbeats`
- **Verify agent card files exist** in `agents/` directory
- **Check for existing session**: `tmux ls`
  - Kill existing session: `uv run tools/kill_agents.py`

### Session already exists error

```bash
# List sessions
uv run tools/kill_agents.py --list

# Kill the existing session
uv run tools/kill_agents.py

# Or use a different session name
uv run tools/start_agents.py --only-white-agents --tmux-session my-session
```

### Can't see logs

```bash
# Attach to the session
tmux attach -t agentbeats-marketplace

# Navigate to the agent pane you want to see
Ctrl+B then arrow keys

# Enter scroll mode to view history
Ctrl+B then [
```

### Agents won't stop

```bash
# Force cleanup
uv run tools/kill_agents.py --force

# Or manually kill the session
tmux kill-session -t agentbeats-marketplace
```

### Port conflicts

- Change base ports via environment variables
- Check what's using a port: `lsof -i :PORT_NUMBER`
- Kill process on port: `lsof -ti :PORT | xargs kill -9`

---

## Environment Variables

Both scripts respect the following environment variables:

```bash
# Model configuration
MODEL_TYPE=openai
MODEL_NAME=gpt-4o-mini

# Port configuration
GREEN_AGENT_PORT=9110
GREEN_LAUNCHER_PORT=9115
BUYER_BASE_PORT=9200
BUYER_LAUNCHER_BASE_PORT=9300
SELLER_BASE_PORT=10000
SELLER_LAUNCHER_BASE_PORT=10100
```

You can set these in your `.env` file or export them in your shell.

---

## Requirements

- Python 3.7+
- tmux
- agentbeats
- toml package (`pip install toml`)

---

## Notes

- Agents run in a tmux session and persist until explicitly stopped
- Always use `kill_agents.py` to clean up when done
- The `--list` flag is useful to see all active sessions
- Buyer distribution is automatically calculated from `simulation_config.toml`
- Each agent gets its own tmux pane for easy log monitoring
- The temporary scenario file is automatically cleaned up (unless `--keep-scenario` is used)
