# MarketArena Battle Guide

## Prerequisites

Before running a battle, ensure you have:

1. **Python 3.11+** installed
2. **AgentBeats** installed (`pip install agentbeats`)
3. **OpenAI API key** set as environment variable
4. **All dependencies** installed (`pip install -r requirements.txt`)

## Quick Start

### Option 1: Using Launch Script (Recommended)

```bash
# Set your OpenAI API key
export OPENAI_API_KEY="sk-your-key-here"

# Run the launch script
cd /Users/pauld/Github/Rede_Labs
./launch_battle.sh
```

The script will:
- Start the Marketplace API
- Launch AgentBeats backend
- Load the MarketArena scenario
- Open the web UI

### Option 2: Manual Launch

#### Terminal 1: Marketplace API
```bash
cd /Users/pauld/Github/Rede_Labs/marketplace_api
python main.py
```

#### Terminal 2: AgentBeats Backend
```bash
export OPENAI_API_KEY="sk-your-key-here"
cd ~/agentbeats
agentbeats deploy --dev_login
```

#### Terminal 3: Load Scenario
```bash
cd /Users/pauld/Github/Rede_Labs
agentbeats load_scenario ./scenario.toml
```

## Accessing the Battle

Once launched:

- **Marketplace API:** http://localhost:8100
- **API Documentation:** http://localhost:8100/docs
- **AgentBeats UI:** http://localhost:3000

## Understanding the Battle Flow

### Phase 1: Initialization
The green agent will:
1. Reset the marketplace
2. Notify white agents to register
3. Wait for initial product listings

### Phase 2: Daily Cycles (5 days)
Each day consists of:

#### Edit Phase (120 seconds)
- White agents can update their listings
- Adjust prices, descriptions, etc.
- Monitor competitors

#### Buy Phase (60 seconds)
- Customer agents browse products
- Make purchase decisions based on personas
- Complete transactions

### Phase 3: Results
After all days:
1. Final statistics calculated
2. Winner determined (highest revenue)
3. Comprehensive report generated
4. Results displayed in AgentBeats UI

## Monitoring the Battle

### AgentBeats Web UI
The UI shows:
- Battle progress
- Agent communications
- MCP log entries
- Final results

### Marketplace API
Check marketplace state:
```bash
# Current status
curl http://localhost:8100/

# Current statistics
curl http://localhost:8100/admin/stats

# Product rankings
curl http://localhost:8100/search?q=towel
```

### Agent Logs
View individual agent logs:
```bash
tail -f ~/.agentbeats/logs/green_agent.log
tail -f ~/.agentbeats/logs/price_optimizer.log
```

## Testing Components

### Test Marketplace API
```bash
cd /Users/pauld/Github/Rede_Labs
./test_integration.sh
```

### Manual API Testing
```bash
# Start API
cd marketplace_api
python main.py &

# Test health
curl http://localhost:8100/

# Create organization
curl -X POST http://localhost:8100/createOrganization \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Corp"}'

# Create product
curl -X POST http://localhost:8100/product \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Towel",
    "shortDescription": "A test product",
    "longDescription": "Detailed description here",
    "price": 2999,
    "image": {"url": "https://example.com/image.jpg"}
  }'

# Search products
curl http://localhost:8100/search?q=towel
```

## Customizing the Battle

### Adjust Battle Duration
Edit `green_agent/green_agent_card.toml`:
- Change number of days in description
- Modify phase durations (default: 120s edit, 60s buy)

### Add More Sellers
1. Create new white agent in `white_agents/`
2. Add to `scenario.toml`:
```toml
[[agents]]
name = "My New Seller"
card = "./white_agents/my_seller/white_agent_card.toml"
launcher_host = "0.0.0.0"
launcher_port = 9220
agent_host = "0.0.0.0"
agent_port = 9225
model_type = "openai"
model_name = "gpt-4o-mini"
tools = ["./white_agents/shared_tools.py"]
```

### Modify Customer Personas
Edit customer agent card files:
- Change shopping preferences
- Adjust budgets
- Modify decision-making logic

### Change LLM Model
Edit `scenario.toml` - change `model_name` for any agent:
```toml
model_name = "gpt-4o"  # Use GPT-4 for better performance
```

## Troubleshooting

### Port Already in Use
```bash
# Find process using port
lsof -i :8100

# Kill process
kill -9 <PID>
```

### AgentBeats Not Found
```bash
# Install AgentBeats
pip install agentbeats

# Or from source
cd ~/agentbeats
pip install -e .
```

### API Connection Errors
- Verify Marketplace API is running: `curl http://localhost:8100/`
- Check firewall settings
- Ensure no port conflicts

### Agent Won't Launch
- Check logs: `cat ~/.agentbeats/logs/`
- Verify OPENAI_API_KEY is set
- Check port availability
- Review agent card TOML syntax

### No Purchases During Buy Phase
- Verify marketplace is in BUY phase: `curl http://localhost:8100/`
- Check customer agent logs
- Ensure products exist: `curl http://localhost:8100/search?q=towel`

## Best Practices

### Development
1. Test marketplace API independently first
2. Test one agent type at a time
3. Use verbose logging during development
4. Monitor agent communications

### Battle Design
1. Balance edit/buy phase durations
2. Ensure diverse customer personas
3. Create varied seller strategies
4. Run multiple iterations for consistent results

### Performance
1. Use gpt-4o-mini for faster, cheaper battles
2. Monitor OpenAI API usage
3. Adjust phase durations based on agent response times
4. Consider parallel processing for multiple battles

## Advanced Usage

### Running Multiple Battles
Create multiple scenario files with different configurations:
```bash
agentbeats load_scenario ./scenario_aggressive.toml
agentbeats load_scenario ./scenario_conservative.toml
```

### Custom Metrics
Extend the green agent to track:
- Price trends over time
- Customer satisfaction scores
- Market share by seller
- Product ranking changes

### Database Integration
Replace in-memory DB with PostgreSQL:
1. Add SQLAlchemy models
2. Update `marketplace_api/database.py`
3. Configure database connection
4. Maintain same API interface

## Getting Help

If you encounter issues:
1. Check this guide's troubleshooting section
2. Review AgentBeats documentation
3. Examine example scenarios in AgentBeats repo
4. Check agent logs for detailed error messages

## Next Steps

After a successful battle:
1. Analyze results in AgentBeats UI
2. Export statistics for further analysis
3. Create new agent strategies
4. Share your scenario with the community
