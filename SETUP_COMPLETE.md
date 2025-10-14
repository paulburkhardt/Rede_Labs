# MarketArena Setup Complete! 🎉

The repository has been successfully set up with all the required components.

## 📁 Repository Structure

```
Rede_Labs/
├── README.md                                 # Project overview
├── REPOSITORY_SETUP_GUIDE.md                # Detailed setup instructions
├── requirements.txt                         # Python dependencies
├── scenario.toml                            # AgentBeats battle configuration
├── launch_battle.sh                         # Quick launch script
├── test_integration.sh                      # Integration test script
├── .gitignore                               # Git ignore rules
│
├── marketplace_api/                         # FastAPI Backend
│   ├── __init__.py
│   ├── main.py                             # API server (port 8100)
│   └── requirements.txt                    # API dependencies
│
├── green_agent/                            # Battle Orchestrator
│   ├── __init__.py
│   ├── green_agent_card.toml              # Agent definition
│   ├── tools.py                           # Orchestration tools
│   └── README.md
│
├── customer_agents/                        # LLM Customer Agents
│   ├── __init__.py
│   ├── shared_tools.py                    # Shared customer tools
│   ├── price_optimizer/
│   │   └── customer_agent_card.toml       # Port 9125
│   ├── quality_seeker/
│   │   └── customer_agent_card.toml       # Port 9135
│   ├── top_rank_buyer/
│   │   └── customer_agent_card.toml       # Port 9145
│   └── balanced_buyer/
│       └── customer_agent_card.toml       # Port 9155
│
├── white_agents/                           # Seller Agents
│   ├── __init__.py
│   ├── shared_tools.py                    # Shared seller tools
│   ├── baseline_seller/
│   │   └── white_agent_card.toml          # Port 9205
│   └── aggressive_pricer/
│       └── white_agent_card.toml          # Port 9215
│
└── docs/                                   # Documentation
    ├── API_REFERENCE.md                   # API documentation
    ├── ARCHITECTURE.md                    # System architecture
    └── BATTLE_GUIDE.md                    # How to run battles
```

## ✅ What's Been Created

### Core Files
- [x] Main README.md
- [x] requirements.txt with all dependencies
- [x] .gitignore for Python projects
- [x] scenario.toml for AgentBeats

### Marketplace API
- [x] FastAPI server (main.py)
- [x] Product management endpoints
- [x] Search and ranking algorithm
- [x] Phase management system
- [x] Admin endpoints for green agent

### Green Agent (Orchestrator)
- [x] Agent card with battle instructions
- [x] Tools for marketplace control
- [x] A2A communication tools
- [x] MCP logging helpers

### Customer Agents (4 personas)
- [x] Price Optimizer (cheapest option)
- [x] Quality Seeker (best quality)
- [x] Top Rank Buyer (trusts rankings)
- [x] Balanced Buyer (considers all factors)
- [x] Shared shopping tools

### White Agents (Sellers)
- [x] Baseline Seller (balanced strategy)
- [x] Aggressive Pricer (undercuts competitors)
- [x] Shared seller tools

### Utility Scripts
- [x] launch_battle.sh (executable)
- [x] test_integration.sh (executable)

### Documentation
- [x] API_REFERENCE.md
- [x] ARCHITECTURE.md
- [x] BATTLE_GUIDE.md

## 🚀 Next Steps

### 1. Install Dependencies

**Option A: Install all dependencies**
```bash
cd /Users/pauld/Github/Rede_Labs
pip install -r requirements.txt
```

**Option B: Install marketplace API dependencies only** (for testing API first)
```bash
cd /Users/pauld/Github/Rede_Labs/marketplace_api
pip install -r requirements.txt
```

### 2. Set Up OpenAI API Key

```bash
export OPENAI_API_KEY="sk-your-key-here"

# Or add to your shell profile permanently:
echo 'export OPENAI_API_KEY="sk-your-key-here"' >> ~/.zshrc
source ~/.zshrc
```

### 3. Install AgentBeats

AgentBeats is required to run the full battle system:

```bash
# Clone AgentBeats (if not already installed)
git clone https://github.com/pchaganti/gx-synth-beat.git ~/agentbeats
cd ~/agentbeats
pip install -e .

# Verify installation
agentbeats --version
```

### 4. Test the Marketplace API

```bash
cd /Users/pauld/Github/Rede_Labs/marketplace_api
python main.py
```

Then in another terminal:
```bash
curl http://localhost:8100/
```

You should see the API status response.

### 5. Run Integration Test

```bash
cd /Users/pauld/Github/Rede_Labs
./test_integration.sh
```

### 6. Launch Your First Battle

**Easy way:**
```bash
cd /Users/pauld/Github/Rede_Labs
./launch_battle.sh
```

**Manual way (3 terminals):**

Terminal 1 - Marketplace API:
```bash
cd /Users/pauld/Github/Rede_Labs/marketplace_api
python main.py
```

Terminal 2 - AgentBeats:
```bash
cd ~/Github/agentbeats
agentbeats deploy
```

Terminal 3 - Load Scenario:
```bash
agentbeats load_scenario /Users/pauld/Github/Rede_Labs/scenario.toml
```

### 7. Monitor the Battle

- **AgentBeats UI:** http://localhost:3000
- **Marketplace API:** http://localhost:8100
- **API Docs:** http://localhost:8100/docs

## 📚 Documentation

All documentation is in the `docs/` folder:

- **API_REFERENCE.md** - Complete API endpoint documentation
- **ARCHITECTURE.md** - System design and data flow
- **BATTLE_GUIDE.md** - How to run and customize battles

## 🎯 Quick Actions

### Test API Endpoints
```bash
# Health check
curl http://localhost:8100/

# Create organization
curl -X POST http://localhost:8100/createOrganization \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Corp"}'

# Search products
curl http://localhost:8100/search?q=towel

# Get stats
curl http://localhost:8100/admin/stats
```

### Customize the Battle

1. **Add more sellers**: Create new agent in `white_agents/` and add to `scenario.toml`
2. **Modify personas**: Edit customer agent cards in `customer_agents/*/`
3. **Change battle duration**: Edit green agent card description
4. **Use different LLM**: Change `model_name` in `scenario.toml`

## ⚠️ Important Notes

1. **Dependencies**: The import errors you see are expected - they'll resolve once you install the packages
2. **AgentBeats**: Must be installed separately (not in requirements.txt)
3. **API Key**: Required for LLM agents to function
4. **Ports**: Make sure ports 8100, 9115-9155, 9205-9215 are available

## 🤔 Need Help?

**Issue:** Dependencies not installing
- **Solution:** Make sure you're using Python 3.11+

**Issue:** Port already in use
- **Solution:** `lsof -i :PORT` then `kill -9 PID`

**Issue:** AgentBeats not found
- **Solution:** Install from ~/agentbeats with `pip install -e .`

**Issue:** API connection errors
- **Solution:** Verify marketplace API is running with `curl http://localhost:8100/`

## 🎊 You're Ready!

Your MarketArena repository is fully set up and ready to run. Follow the Next Steps above to start battling!

For detailed information, see:
- `REPOSITORY_SETUP_GUIDE.md` - Complete setup instructions
- `docs/BATTLE_GUIDE.md` - How to run battles
- `docs/ARCHITECTURE.md` - System design
