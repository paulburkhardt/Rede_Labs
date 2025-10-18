# MarketArena

AI agent benchmark for e-commerce marketplace competition.

## Quick Start

See REPOSITORY_SETUP_GUIDE.md for detailed setup instructions.

## Running a Battle

### 1. Start Marketplace API

```bash
cd marketplace_api
python main.py
```

### 2. Start AgentBeats

Open a new terminal and execute the following commands:

```bash
# Navigate to AgentBeats directory (could be different)
cd ~/Projects/agentbeats

# Create and activate virtual environment with Python 3.11
python3.11 -m venv venv
source venv/bin/activate

# Install AgentBeats
pip install -e .

# Create a .env file
touch .env
echo "OPENROUTER_API_KEY=your-openrouter-api-key" >> .env
echo "OPENAI_API_KEY=your-openai-api-key" >> .env

# Install frontend dependencies
agentbeats install_frontend --webapp_version webapp-v2

# Launch AgentBeats
agentbeats deploy
```

Now, you can access the AgentBeats UI at http://localhost:5173

### 3. Load Scenario

Open a new terminal and execute the following commands:

```bash
# Activate virtual environment with Python 3.11
source venv/bin/activate

# Kill previous tmux session
tmux kill-session -t agentbeats-marketarena

# Path to scenario.toml could be different
agentbeats load_scenario ~/Projects/Rede_Labs

# Open tmux session "agentbeats-marketarena"
tmux attach -t agentbeats-marketarena

# With "Ctrl+b w" you can switch between windows
```

### 4. Register Agents on AgentBeats UI

Open http://localhost:5173 in your browser.

1. Click on "Login"
2. Select [Agents](http://localhost:5173/agents/my-agents) on the left sidebar
3. Click the [plus icon](http://localhost:5173/agents/register) to create a new agent

**Register the Green Agent**
Agent URL: http://0.0.0.0:9115
Launcher URL: http://0.0.0.0:9110
Enable "Green?" switch button
Add the following participants:
- Role: "seller", Name: "baseline_seller"
- Role: "seller", Name: "aggressive_pricer"

**Register the Customer Agents**
Baseline Seller
Agent URL: http://0.0.0.0:9205
Launcher URL: http://0.0.0.0:9200

Aggressive Pricer
Agent URL: http://0.0.0.0:9215
Launcher URL: http://0.0.0.0:9210

### 5. Start Battle

1. Go [Home](http://localhost:5173/dashboard)
2. Click on "Create Your Own Battle"
3. Select the Green Agent
4. Select the Customer Agents
