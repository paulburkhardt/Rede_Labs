# MarketArena Architecture

## System Overview

MarketArena is a multi-agent simulation environment for testing AI agents in an e-commerce marketplace scenario.

```
┌─────────────────────────────────────────────────────────────┐
│                        AgentBeats                            │
│                   (Infrastructure Layer)                     │
│  - Agent Lifecycle Management                                │
│  - A2A Communication Protocol                                │
│  - MCP Logging & UI                                          │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    MarketArena Battle                        │
└─────────────────────────────────────────────────────────────┘
                              ↓
        ┌─────────────────────┼─────────────────────┐
        ↓                     ↓                     ↓
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ Green Agent  │    │   Customer   │    │    White     │
│   (Host)     │    │    Agents    │    │   Agents     │
│              │    │  (Buyers)    │    │  (Sellers)   │
└──────────────┘    └──────────────┘    └──────────────┘
        │                   │                    │
        └───────────────────┼────────────────────┘
                            ↓
                ┌──────────────────────┐
                │  Marketplace API     │
                │  (FastAPI Backend)   │
                └──────────────────────┘
```

## Components

### 1. Marketplace API (FastAPI)
- **Location:** `marketplace_api/main.py`
- **Port:** 8100
- **Responsibilities:**
  - Product catalog management
  - Search and ranking algorithm
  - Purchase transactions
  - Phase state management
  - Revenue tracking

**Key Features:**
- In-memory database (can be upgraded to PostgreSQL)
- RESTful API design
- Phase-based access control
- Ranking algorithm based on sales, price, and description quality

### 2. Green Agent (Battle Orchestrator)
- **Location:** `green_agent/`
- **Port:** 9115
- **Responsibilities:**
  - Initialize marketplace
  - Manage edit/buy phases
  - Coordinate agent communications via A2A
  - Track statistics
  - Generate reports

**Communication:**
- REST API calls to Marketplace API
- A2A protocol for agent-to-agent messaging
- MCP protocol for logging to AgentBeats UI

### 3. Customer Agents (LLM Buyers)
- **Location:** `customer_agents/`
- **Ports:** 9125, 9135, 9145, 9155
- **Count:** 4 agents with different personas

**Agent Types:**
1. **Price Optimizer** - Seeks cheapest products
2. **Quality Seeker** - Prioritizes quality over price
3. **Top Rank Buyer** - Trusts marketplace rankings
4. **Balanced Buyer** - Considers all factors

**Behavior:**
- Browse products via API
- Evaluate based on persona
- Make purchase decisions
- Report actions to green agent

### 4. White Agents (Competing Sellers)
- **Location:** `white_agents/`
- **Ports:** 9205, 9215
- **Count:** 2+ agents with different strategies

**Agent Types:**
1. **Baseline Seller** - Balanced, competitive approach
2. **Aggressive Pricer** - Undercuts competitors

**Capabilities:**
- Create/update product listings
- Monitor competitors
- Adjust pricing strategies
- Optimize descriptions

## Data Flow

### Battle Initialization
```
1. AgentBeats loads scenario.toml
2. All agents start on designated ports
3. Green agent receives battle_id
4. Green agent resets marketplace
5. White agents register organizations
6. White agents create initial products
```

### Daily Cycle (Edit Phase)
```
1. Green agent: POST /admin/start_edit_phase
2. Green agent: Broadcast to white agents via A2A
3. White agents: Browse competitors
4. White agents: Update listings via API
5. Wait 120 seconds
6. Green agent: Log phase completion to MCP
```

### Daily Cycle (Buy Phase)
```
1. Green agent: POST /admin/start_buy_phase
2. Green agent: Broadcast to customer agents via A2A
3. Customer agents: Browse products via API
4. Customer agents: Make purchase decisions
5. Customer agents: POST /buy/{product_id}
6. Green agent: GET /admin/stats
7. Green agent: Log results to MCP
```

### Battle Completion
```
1. Green agent: Calculate final statistics
2. Green agent: Determine winner
3. Green agent: Generate comprehensive report
4. Green agent: Call report_on_battle_end MCP tool
5. Results displayed in AgentBeats UI
```

## Technology Stack

### Backend
- **FastAPI** - REST API framework
- **Pydantic** - Data validation
- **Uvicorn** - ASGI server

### Agent Framework
- **AgentBeats SDK** - Agent lifecycle and communication
- **A2A Protocol** - Agent-to-agent messaging
- **MCP Protocol** - Model Context Protocol for logging

### LLM Integration
- **OpenAI GPT-4o-mini** - Default model for agents
- Supports other OpenAI-compatible models

### Communication Protocols
- **REST** - Marketplace API access
- **A2A** - Inter-agent communication
- **MCP** - Logging and UI updates

## Scalability Considerations

### Current Design
- In-memory database (fast, simple)
- Single marketplace instance
- Fixed port assignments

### Production Enhancements
1. **Database:** Replace in-memory DB with PostgreSQL
2. **State Management:** Add Redis for distributed state
3. **Dynamic Ports:** Use port allocation service
4. **Monitoring:** Add Prometheus metrics
5. **Load Balancing:** Support multiple marketplace instances

## Security Considerations

### Current Implementation
- No authentication (suitable for local testing)
- Open CORS policy
- Admin endpoints unprotected

### Production Requirements
1. **Authentication:** Add API keys or JWT tokens
2. **Authorization:** Role-based access control
3. **Rate Limiting:** Prevent abuse
4. **Input Validation:** Enhanced Pydantic schemas
5. **HTTPS:** TLS/SSL encryption

## Extension Points

### Adding New Customer Personas
1. Create new directory in `customer_agents/`
2. Write `customer_agent_card.toml` with persona
3. Use `shared_tools.py` for marketplace access
4. Add to `scenario.toml`

### Adding New Seller Strategies
1. Create new directory in `white_agents/`
2. Write `white_agent_card.toml` with strategy
3. Use `shared_tools.py` for marketplace access
4. Optionally add custom strategy logic
5. Add to `scenario.toml`

### Enhancing Ranking Algorithm
- Modify `InMemoryDB.calculate_product_rank_score()` in `marketplace_api/main.py`
- Consider: reviews, seller reputation, click-through rate, conversion rate

### Adding New Product Categories
- Extend marketplace API to support categories
- Update customer agent personas
- Modify ranking algorithm for category-specific logic
