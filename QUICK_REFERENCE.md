# MarketArena Quick Reference

## 🚀 Quick Start Commands

### Start Marketplace API
```bash
cd /Users/pauld/Github/Rede_Labs/marketplace_api
python main.py
```

### Launch Full Battle
```bash
cd /Users/pauld/Github/Rede_Labs
./launch_battle.sh
```

### Run Tests
```bash
cd /Users/pauld/Github/Rede_Labs
./test_integration.sh
```

## 🔌 Ports Reference

| Component | Port | URL |
|-----------|------|-----|
| Marketplace API | 8100 | http://localhost:8100 |
| Green Agent | 9115 | http://localhost:9115 |
| Price Optimizer | 9125 | http://localhost:9125 |
| Quality Seeker | 9135 | http://localhost:9135 |
| Top Rank Buyer | 9145 | http://localhost:9145 |
| Balanced Buyer | 9155 | http://localhost:9155 |
| Baseline Seller | 9205 | http://localhost:9205 |
| Aggressive Pricer | 9215 | http://localhost:9215 |
| AgentBeats UI | 3000 | http://localhost:3000 |

## 📡 API Endpoints

### Public Endpoints
```bash
GET  /                          # Health check
POST /createOrganization        # Register seller
POST /product                   # Create product
PATCH /product/{id}             # Update product (EDIT phase)
GET  /search?q=towel            # Search products
GET  /product/{id}              # Get product details
POST /buy/{id}                  # Purchase (BUY phase)
```

### Admin Endpoints (Green Agent Only)
```bash
POST /admin/reset               # Reset marketplace
POST /admin/start_edit_phase    # Start edit phase
POST /admin/start_buy_phase     # Start buy phase
GET  /admin/stats               # Get statistics
```

## 🎭 Agent Roles

### Green Agent (Orchestrator)
- Manages battle phases
- Coordinates agents
- Tracks statistics
- Reports results

### Customer Agents (Buyers)
1. **Price Optimizer** - Seeks lowest price
2. **Quality Seeker** - Prioritizes quality
3. **Top Rank Buyer** - Trusts rankings
4. **Balanced Buyer** - Considers all factors

### White Agents (Sellers)
1. **Baseline Seller** - Balanced strategy
2. **Aggressive Pricer** - Undercuts competitors

## 🔄 Battle Flow

```
1. Initialize → 2. Edit Phase → 3. Buy Phase → 4. Repeat → 5. Results
                 (120 seconds)    (60 seconds)    (5 days)
```

## 🛠️ Common Commands

### Check API Status
```bash
curl http://localhost:8100/
```

### Create Organization
```bash
curl -X POST http://localhost:8100/createOrganization \
  -H "Content-Type: application/json" \
  -d '{"name": "My Company"}'
```

### Search Products
```bash
curl http://localhost:8100/search?q=towel
```

### Get Statistics
```bash
curl http://localhost:8100/admin/stats
```

### View Logs
```bash
tail -f ~/.agentbeats/logs/green_agent.log
```

## 📁 Key Files

| File | Purpose |
|------|---------|
| `scenario.toml` | AgentBeats configuration |
| `marketplace_api/main.py` | API server |
| `green_agent/tools.py` | Orchestrator tools |
| `customer_agents/shared_tools.py` | Customer tools |
| `white_agents/shared_tools.py` | Seller tools |

## 🐛 Troubleshooting

### Port in Use
```bash
lsof -i :8100
kill -9 <PID>
```

### Missing Dependencies
```bash
pip install -r requirements.txt
```

### API Not Responding
```bash
# Check if running
curl http://localhost:8100/

# Restart
cd marketplace_api
python main.py
```

## 🔑 Environment Variables

```bash
# Required
export OPENAI_API_KEY="sk-your-key-here"
```

## 📊 Monitoring

- **Web UI**: http://localhost:3000
- **API Docs**: http://localhost:8100/docs
- **Logs**: `~/.agentbeats/logs/`

## ⚡ Tips

1. Start API first, then AgentBeats
2. Set OPENAI_API_KEY before launching
3. Check logs if agents don't respond
4. Use API docs for endpoint testing
5. Monitor phase transitions in green agent

## 📖 Full Documentation

- `SETUP_COMPLETE.md` - Setup summary
- `docs/API_REFERENCE.md` - API details
- `docs/ARCHITECTURE.md` - System design
- `docs/BATTLE_GUIDE.md` - Battle instructions
