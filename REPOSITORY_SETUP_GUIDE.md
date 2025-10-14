# MarketArena Repository Setup Guide

This guide provides **complete step-by-step instructions** for setting up the MarketArena e-commerce marketplace benchmark in your own repository. No prior AgentBeats knowledge required!

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Prerequisites](#prerequisites)
3. [Repository Structure](#repository-structure)
4. [Step 1: Initial Repository Setup](#step-1-initial-repository-setup)
5. [Step 2: Marketplace API Implementation](#step-2-marketplace-api-implementation)
6. [Step 3: Green Agent Setup](#step-3-green-agent-setup)
7. [Step 4: Customer Agents Setup](#step-4-customer-agents-setup)
8. [Step 5: White Agent Templates](#step-5-white-agent-templates)
9. [Step 6: Scenario Configuration](#step-6-scenario-configuration)
10. [Step 7: Testing & Integration](#step-7-testing--integration)
11. [Step 8: Running Battles](#step-8-running-battles)
12. [Troubleshooting](#troubleshooting)
13. [Team Workflow (2-Day Plan)](#team-workflow-2-day-plan)

---

## Project Overview

**MarketArena** is an AI agent benchmark where:
- **White agents (sellers)** compete to maximize revenue by optimizing product listings
- **Customer agents (LLM buyers)** make autonomous purchase decisions based on personas
- **Green agent (orchestrator)** manages the marketplace, coordinates agents, and evaluates results
- **Marketplace API** provides the e-commerce environment (products, rankings, purchases)

### What You're Building

```
Your MarketArena Repository
├── marketplace_api/          # FastAPI backend (e-commerce platform)
├── green_agent/              # Battle orchestrator
├── customer_agents/          # LLM customer agents with personas
├── white_agents/             # Sample seller agents
├── scenario.toml             # AgentBeats battle configuration
└── README.md
```

**Integration with AgentBeats:**
- Your repo is **separate** from AgentBeats
- AgentBeats provides the infrastructure (battle UI, MCP logging, agent management)
- Users run: `agentbeats load_scenario /path/to/your/scenario.toml`

---

## Prerequisites

### Required Software

```bash
# 1. Python 3.11 or higher
python --version  # Should be >= 3.11

# 2. Git
git --version

# 3. AgentBeats (installed separately)
pip install agentbeats
```

### Required API Keys

```bash
# OpenAI API key for LLM agents
export OPENAI_API_KEY="sk-your-key-here"

# Or add to ~/.zshrc or ~/.bashrc:
echo 'export OPENAI_API_KEY="sk-your-key-here"' >> ~/.zshrc
source ~/.zshrc
```

### AgentBeats Installation

AgentBeats is installed **separately** from your repo:

```bash
# Clone AgentBeats repository
git clone https://github.com/pchaganti/gx-synth-beat.git ~/agentbeats
cd ~/agentbeats
pip install -e .

# Verify installation
agentbeats --version
```

---

## Repository Structure

Create this **exact structure** in your own repository:

```
marketarena/                                  # Your repo root
│
├── README.md                                 # Project documentation
├── requirements.txt                          # Python dependencies
├── .gitignore                                # Git ignore file
├── scenario.toml                             # AgentBeats scenario config
│
├── marketplace_api/                          # FastAPI Backend
│   ├── __init__.py
│   ├── main.py                              # API server
│   ├── database.py                          # Database models
│   ├── models.py                            # Pydantic schemas
│   ├── ranking.py                           # Product ranking algorithm
│   └── requirements.txt                     # API dependencies
│
├── green_agent/                             # Battle Orchestrator
│   ├── __init__.py
│   ├── green_agent_card.toml               # Agent definition
│   ├── tools.py                            # Custom tools (@ab.tool)
│   └── README.md                           # Green agent docs
│
├── customer_agents/                         # LLM Customer Agents
│   ├── __init__.py
│   ├── shared_tools.py                     # Shared customer tools
│   ├── price_optimizer/
│   │   └── customer_agent_card.toml
│   ├── quality_seeker/
│   │   └── customer_agent_card.toml
│   ├── top_rank_buyer/
│   │   └── customer_agent_card.toml
│   └── balanced_buyer/
│       └── customer_agent_card.toml
│
├── white_agents/                            # Sample Seller Agents
│   ├── __init__.py
│   ├── shared_tools.py                     # Shared seller tools
│   ├── baseline_seller/
│   │   ├── white_agent_card.toml
│   │   └── strategy.py (optional)
│   └── aggressive_pricer/
│       ├── white_agent_card.toml
│       └── strategy.py (optional)
│
├── tests/                                   # Integration tests
│   ├── test_api.py
│   ├── test_customer_agents.py
│   └── test_full_battle.py
│
└── docs/                                    # Documentation
    ├── API_REFERENCE.md
    ├── ARCHITECTURE.md
    └── BATTLE_GUIDE.md
```

---

## Step 1: Initial Repository Setup

### 1.1 Create Repository

```bash
# Create new directory
mkdir marketarena
cd marketarena

# Initialize git
git init

# Create README
cat > README.md << 'EOF'
# MarketArena

AI agent benchmark for e-commerce marketplace competition.

## Quick Start

See SETUP.md for detailed setup instructions.

## Running a Battle

```bash
# Terminal 1: Start marketplace API
cd marketplace_api
python main.py

# Terminal 2: Start AgentBeats
cd ~/agentbeats
agentbeats deploy --dev_login

# Terminal 3: Load scenario
cd ~/agentbeats
agentbeats load_scenario /path/to/marketarena/scenario.toml
```
EOF
```

### 1.2 Create .gitignore

```bash
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
*.egg-info/
dist/
build/

# IDEs
.vscode/
.idea/
*.swp
*.swo

# Database
*.db
*.sqlite
*.sqlite3

# Environment
.env
.env.local

# Logs
*.log

# OS
.DS_Store
Thumbs.db
EOF
```

### 1.3 Create Main Requirements

```bash
cat > requirements.txt << 'EOF'
# AgentBeats SDK
agentbeats>=0.1.0

# API Framework
fastapi==0.115.0
uvicorn==0.32.0
pydantic==2.9.2

# Database
sqlalchemy==2.0.36

# HTTP Clients
httpx==0.27.0
requests==2.32.3

# Async Support
asyncio
aiofiles

# Utilities
python-dotenv==1.0.0
python-multipart==0.0.17
EOF

# Install base dependencies
pip install -r requirements.txt
```

---

## Step 2: Marketplace API Implementation

### 2.1 Create API Directory

```bash
mkdir -p marketplace_api
cd marketplace_api
```

### 2.2 Create API Requirements

```bash
cat > requirements.txt << 'EOF'
fastapi==0.115.0
uvicorn==0.32.0
sqlalchemy==2.0.36
pydantic==2.9.2
python-multipart==0.0.17
EOF
```

### 2.3 Create Main API File

```bash
cat > main.py << 'EOF'
# -*- coding: utf-8 -*-
"""
MarketArena Marketplace API

FastAPI backend for e-commerce marketplace simulation.
Run with: uvicorn main:app --host 0.0.0.0 --port 8100 --reload
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
from enum import Enum
import uuid
from datetime import datetime

app = FastAPI(
    title="MarketArena Marketplace API",
    description="E-commerce marketplace for AI agent competition",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Data Models
# ============================================================================

class PhaseEnum(str, Enum):
    EDIT = "edit"
    BUY = "buy"
    IDLE = "idle"


class OrganizationCreate(BaseModel):
    name: str


class OrganizationResponse(BaseModel):
    id: str
    name: str


class ImageData(BaseModel):
    url: str
    alternativeText: Optional[str] = None


class ProductCreate(BaseModel):
    name: str
    shortDescription: str
    longDescription: str
    price: int  # Price in cents
    image: ImageData


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    shortDescription: Optional[str] = None
    longDescription: Optional[str] = None
    price: Optional[int] = None
    image: Optional[ImageData] = None


class CompanyInfo(BaseModel):
    name: str
    id: str


class ProductSearchResult(BaseModel):
    id: str
    name: str
    company: CompanyInfo
    priceInCent: int
    currency: str = "USD"
    bestseller: bool
    shortDescription: str
    image: ImageData


class ProductDetail(ProductSearchResult):
    longDescription: str


# ============================================================================
# In-Memory Database
# ============================================================================

class InMemoryDB:
    def __init__(self):
        self.organizations: Dict[str, dict] = {}
        self.products: Dict[str, dict] = {}
        self.purchases: List[dict] = []
        self.current_phase = PhaseEnum.IDLE
        self.current_day = 0
    
    def reset(self):
        """Reset all data"""
        self.organizations.clear()
        self.products.clear()
        self.purchases.clear()
        self.current_phase = PhaseEnum.IDLE
        self.current_day = 0
    
    def calculate_bestsellers(self) -> set:
        """Mark top 20% of products by sales as bestsellers"""
        sales_count = {}
        for purchase in self.purchases:
            pid = purchase['product_id']
            sales_count[pid] = sales_count.get(pid, 0) + 1
        
        if not sales_count:
            return set()
        
        sorted_products = sorted(sales_count.items(), key=lambda x: x[1], reverse=True)
        bestseller_count = max(1, len(sorted_products) // 5)
        return {pid for pid, _ in sorted_products[:bestseller_count]}
    
    def calculate_product_rank_score(self, product_id: str) -> float:
        """Calculate ranking score (higher = better rank)"""
        product = self.products.get(product_id)
        if not product:
            return 0.0
        
        score = 0.0
        
        # Sales count (40%)
        sales = sum(1 for p in self.purchases if p['product_id'] == product_id)
        score += min(sales / 10, 1.0) * 0.4
        
        # Price competitiveness (30%)
        avg_price_cents = 5000
        price_score = max(0, 1.0 - abs(product['price'] - avg_price_cents) / avg_price_cents)
        score += price_score * 0.3
        
        # Description quality (20%)
        desc_length = len(product.get('short_description', ''))
        desc_score = min(desc_length / 200, 1.0)
        score += desc_score * 0.2
        
        # Recency (10%)
        score += 0.1
        
        return score


db = InMemoryDB()


# ============================================================================
# Helper Functions
# ============================================================================

def check_edit_phase():
    if db.current_phase != PhaseEnum.EDIT:
        raise HTTPException(
            status_code=403,
            detail=f"Cannot edit products. Current phase: {db.current_phase}"
        )


def check_buy_phase():
    if db.current_phase != PhaseEnum.BUY:
        raise HTTPException(
            status_code=403,
            detail=f"Cannot make purchases. Current phase: {db.current_phase}"
        )


# ============================================================================
# Public Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Health check"""
    return {
        "service": "MarketArena Marketplace API",
        "version": "1.0.0",
        "status": "running",
        "current_phase": db.current_phase,
        "current_day": db.current_day
    }


@app.post("/createOrganization", response_model=OrganizationResponse)
async def create_organization(org_data: OrganizationCreate):
    """Create seller organization"""
    org_id = f"org-{uuid.uuid4().hex[:8]}"
    
    db.organizations[org_id] = {
        "id": org_id,
        "name": org_data.name
    }
    
    return OrganizationResponse(id=org_id, name=org_data.name)


@app.post("/product")
async def create_product(product_data: ProductCreate):
    """Create product listing"""
    product_id = f"product-{uuid.uuid4().hex[:8]}"
    
    # TODO: Get org_id from authentication
    if not db.organizations:
        org_id = "org-default"
        db.organizations[org_id] = {"id": org_id, "name": "Default Seller"}
    else:
        org_id = list(db.organizations.keys())[0]
    
    db.products[product_id] = {
        "id": product_id,
        "name": product_data.name,
        "org_id": org_id,
        "price": product_data.price,
        "short_description": product_data.shortDescription,
        "long_description": product_data.longDescription,
        "image": product_data.image.dict(),
        "created_at": datetime.now()
    }
    
    return {"id": product_id, "message": "Product created successfully"}


@app.patch("/product/{product_id}")
async def update_product(product_id: str, updates: ProductUpdate):
    """Update product listing (only during edit phase)"""
    check_edit_phase()
    
    if product_id not in db.products:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product = db.products[product_id]
    
    if updates.name is not None:
        product['name'] = updates.name
    if updates.shortDescription is not None:
        product['short_description'] = updates.shortDescription
    if updates.longDescription is not None:
        product['long_description'] = updates.longDescription
    if updates.price is not None:
        product['price'] = updates.price
    if updates.image is not None:
        product['image'] = updates.image.dict()
    
    return {"id": product_id, "message": "Product updated successfully"}


@app.get("/search", response_model=List[ProductSearchResult])
async def search_products(q: str):
    """Search products, returns ranked list"""
    bestsellers = db.calculate_bestsellers()
    
    # Filter by query
    matching_products = [
        p for p in db.products.values()
        if q.lower() in p['name'].lower()
    ]
    
    # Calculate scores and sort
    scored_products = [
        (p, db.calculate_product_rank_score(p['id']))
        for p in matching_products
    ]
    scored_products.sort(key=lambda x: x[1], reverse=True)
    
    # Convert to response format
    results = []
    for product, score in scored_products:
        org = db.organizations.get(product['org_id'], {"id": "unknown", "name": "Unknown"})
        
        results.append(ProductSearchResult(
            id=product['id'],
            name=product['name'],
            company=CompanyInfo(name=org['name'], id=org['id']),
            priceInCent=product['price'],
            currency="USD",
            bestseller=product['id'] in bestsellers,
            shortDescription=product['short_description'],
            image=ImageData(**product['image'])
        ))
    
    return results


@app.get("/product/{product_id}", response_model=ProductDetail)
async def get_product_detail(product_id: str):
    """Get detailed product information"""
    if product_id not in db.products:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product = db.products[product_id]
    org = db.organizations.get(product['org_id'], {"id": "unknown", "name": "Unknown"})
    bestsellers = db.calculate_bestsellers()
    
    return ProductDetail(
        id=product['id'],
        name=product['name'],
        company=CompanyInfo(name=org['name'], id=org['id']),
        priceInCent=product['price'],
        currency="USD",
        bestseller=product['id'] in bestsellers,
        shortDescription=product['short_description'],
        longDescription=product['long_description'],
        image=ImageData(**product['image'])
    )


@app.post("/buy/{product_id}")
async def purchase_product(product_id: str):
    """Purchase product (only during buy phase)"""
    check_buy_phase()
    
    if product_id not in db.products:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product = db.products[product_id]
    
    purchase_record = {
        "product_id": product_id,
        "org_id": product['org_id'],
        "price": product['price'],
        "timestamp": datetime.now()
    }
    db.purchases.append(purchase_record)
    
    return {
        "success": True,
        "product_id": product_id,
        "price": product['price'],
        "message": "Purchase completed"
    }


# ============================================================================
# Admin Endpoints (Green Agent Control)
# ============================================================================

@app.post("/admin/reset")
async def admin_reset():
    """Reset marketplace"""
    db.reset()
    return {
        "success": True,
        "message": "Marketplace reset",
        "phase": db.current_phase,
        "day": db.current_day
    }


@app.post("/admin/start_edit_phase")
async def admin_start_edit_phase():
    """Start edit phase"""
    db.current_phase = PhaseEnum.EDIT
    db.current_day += 1
    return {
        "success": True,
        "phase": db.current_phase,
        "day": db.current_day,
        "message": f"Edit phase started for day {db.current_day}"
    }


@app.post("/admin/start_buy_phase")
async def admin_start_buy_phase():
    """Start buy phase"""
    db.current_phase = PhaseEnum.BUY
    return {
        "success": True,
        "phase": db.current_phase,
        "day": db.current_day,
        "message": f"Buy phase started for day {db.current_day}"
    }


@app.get("/admin/stats")
async def admin_get_stats():
    """Get revenue statistics"""
    org_stats = {}
    
    for purchase in db.purchases:
        org_id = purchase['org_id']
        if org_id not in org_stats:
            org = db.organizations.get(org_id, {"name": "Unknown"})
            org_stats[org_id] = {
                "org_id": org_id,
                "name": org['name'],
                "total_revenue": 0,
                "units_sold": 0
            }
        
        org_stats[org_id]['total_revenue'] += purchase['price']
        org_stats[org_id]['units_sold'] += 1
    
    # Calculate averages
    for stats in org_stats.values():
        if stats['units_sold'] > 0:
            stats['avg_price'] = stats['total_revenue'] // stats['units_sold']
        else:
            stats['avg_price'] = 0
    
    sellers = sorted(org_stats.values(), key=lambda x: x['total_revenue'], reverse=True)
    
    total_revenue = sum(s['total_revenue'] for s in sellers)
    total_units = sum(s['units_sold'] for s in sellers)
    
    return {
        "sellers": sellers,
        "marketplace_totals": {
            "total_revenue": total_revenue,
            "total_units_sold": total_units,
            "num_sellers": len(sellers)
        },
        "current_day": db.current_day,
        "current_phase": db.current_phase
    }


if __name__ == "__main__":
    import uvicorn
    print("Starting MarketArena Marketplace API...")
    print("API at: http://localhost:8100")
    print("Docs at: http://localhost:8100/docs")
    uvicorn.run(app, host="0.0.0.0", port=8100)
EOF
```

### 2.4 Test API

```bash
# Terminal 1: Start API
cd marketplace_api
python main.py

# Terminal 2: Test endpoints
# Health check
curl http://localhost:8100/

# Create organization
curl -X POST http://localhost:8100/createOrganization \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Corp"}'

# Should see: {"id": "org-xxxxx", "name": "Test Corp"}
```

**✅ Checkpoint:** API should be running on http://localhost:8100

---

## Step 3: Green Agent Setup

### 3.1 Create Green Agent Directory

```bash
cd .. # Back to repo root
mkdir -p green_agent
cd green_agent
```

### 3.2 Create Green Agent Card

This file defines the green agent's role and behavior.

```bash
cat > green_agent_card.toml << 'EOF'
name = "MarketArena Green Agent (Battle Host)"
description = '''
## Your Role
You are the green agent (Battle Host) in MarketArena, a simulated e-commerce marketplace competition.

## Battle Configuration
Participating agents:
- **White Agents (Sellers)**: AI agents competing to maximize revenue
- **Customer Agents**: AI agents with shopping personas who purchase products

Marketplace API: http://localhost:8100

## Your Responsibilities

### 1. Battle Initialization
At battle start, you receive:
- battle_id: Unique identifier
- white_agent_urls: List of seller agent URLs
- customer_agent_urls: List of customer URLs (http://localhost:9125, 9135, 9145, 9155)

Actions:
1. Reset marketplace: POST http://localhost:8100/admin/reset
2. Log initialization to MCP
3. Notify white agents to register and create initial products

### 2. Multi-Day Simulation Loop
For each day (recommend 5 days):

#### A. Edit Phase (120 seconds)
1. Start edit phase: POST http://localhost:8100/admin/start_edit_phase
2. Log to MCP: "Day {N} - Edit Phase Started"
3. Broadcast to white agents via A2A: "Edit phase active. Update your listings."
4. Wait 120 seconds
5. Log to MCP: "Day {N} - Edit Phase Completed"

#### B. Buy Phase (60 seconds)
1. Start buy phase: POST http://localhost:8100/admin/start_buy_phase
2. Log to MCP: "Day {N} - Buy Phase Started"
3. Broadcast to customer agents via A2A:
   "Day {N} shopping! Browse marketplace and make purchase decisions. 
   Product category: towels. Budget: $100."
4. Collect customer responses
5. Log to MCP with purchase summary

#### C. Daily Evaluation
1. Get stats: GET http://localhost:8100/admin/stats
2. Log daily leaderboard to MCP (use markdown table)

### 3. Final Evaluation & Reporting
After all days:
1. Get final stats
2. Calculate winner (highest total revenue)
3. Generate comprehensive report
4. REQUIRED: Call report_on_battle_end with winner

## Your Tools

### Marketplace Control Tools
- reset_marketplace() - Reset environment
- start_edit_phase() - Begin edit phase
- start_buy_phase() - Begin buy phase
- get_revenue_stats() - Get current statistics
- get_product_rankings() - View current rankings

### Agent Communication Tools
- talk_to_agent(query, target_url) - Send A2A message to any agent
- broadcast_to_customers(message) - Message all customer agents
- broadcast_to_sellers(message) - Message all white agents

### MCP Logging Tools
- update_battle_process(battle_id, message, reported_by, detail, markdown_content)
- report_on_battle_end(battle_id, message, winner, detail, markdown_content) 

## Important Notes
- Log every major action to MCP for transparency
- Wait for timeouts - don't rush phases
- Handle errors gracefully
- Must call report_on_battle_end to finish battle
'''
url = "http://localhost:9115/"
host = "0.0.0.0"
port = 9115
version = "1.0.0"

defaultInputModes = ["text"]
defaultOutputModes = ["text"]

[capabilities]
streaming = true

[[skills]]
id = "marketarena_host_battle"
name = "MarketArena Host Battle"
description = "Orchestrate multi-day e-commerce marketplace competition"
tags = ["host", "battle", "marketplace", "e-commerce"]
examples = ["Host 5-day marketplace battle with 3 sellers and 4 customers"]
EOF
```

### 3.3 Create Green Agent Tools

```bash
cat > tools.py << 'EOF'
# -*- coding: utf-8 -*-
"""
MarketArena Green Agent Tools
"""

import httpx
import agentbeats as ab
import requests
from uuid import uuid4
from typing import List, Dict
from a2a.client import A2AClient, A2ACardResolver
from a2a.types import (
    AgentCard, Message, Part, TextPart, Role,
    SendStreamingMessageRequest,
    SendStreamingMessageSuccessResponse,
    MessageSendParams,
    TaskArtifactUpdateEvent,
    TaskStatusUpdateEvent,
)

MARKETPLACE_URL = "http://localhost:8100"


@ab.tool
async def talk_to_agent(query: str, target_url: str) -> str:
    """
    Send A2A message to any agent (white or customer).
    
    Args:
        query: Message to send
        target_url: Agent URL (e.g., http://localhost:9125)
    
    Returns:
        Agent's response
    """
    httpx_client = httpx.AsyncClient()
    resolver = A2ACardResolver(httpx_client=httpx_client, base_url=target_url)
    card: AgentCard | None = await resolver.get_agent_card(
        relative_card_path="/.well-known/agent.json"
    )
    if card is None:
        raise RuntimeError(f"Failed to resolve agent card from {target_url}")

    client = A2AClient(httpx_client=httpx_client, agent_card=card)

    params = MessageSendParams(
        message=Message(
            role=Role.user,
            parts=[Part(TextPart(text=query))],
            messageId=uuid4().hex,
            taskId=None,
        )
    )
    req = SendStreamingMessageRequest(id=str(uuid4()), params=params)
    chunks: List[str] = []

    async for chunk in client.send_message_streaming(req):
        if not isinstance(chunk.root, SendStreamingMessageSuccessResponse):
            continue
        event = chunk.root.result
        if isinstance(event, TaskArtifactUpdateEvent):
            for p in event.artifact.parts:
                if isinstance(p.root, TextPart):
                    chunks.append(p.root.text)
        elif isinstance(event, TaskStatusUpdateEvent):
            msg = event.status.message
            if msg:
                for p in msg.parts:
                    if isinstance(p.root, TextPart):
                        chunks.append(p.root.text)

    return "".join(chunks).strip() or "No response from agent."


@ab.tool
def reset_marketplace() -> str:
    """Reset marketplace to clean state"""
    try:
        response = requests.post(f"{MARKETPLACE_URL}/admin/reset")
        response.raise_for_status()
        result = response.json()
        return f"Marketplace reset successfully. {result}"
    except Exception as e:
        return f"Error resetting marketplace: {str(e)}"


@ab.tool
def start_edit_phase() -> str:
    """Start edit phase (sellers can update listings)"""
    try:
        response = requests.post(f"{MARKETPLACE_URL}/admin/start_edit_phase")
        response.raise_for_status()
        result = response.json()
        return f"Edit phase started. Day {result.get('day')}. {result}"
    except Exception as e:
        return f"Error starting edit phase: {str(e)}"


@ab.tool
def start_buy_phase() -> str:
    """Start buy phase (customers can purchase)"""
    try:
        response = requests.post(f"{MARKETPLACE_URL}/admin/start_buy_phase")
        response.raise_for_status()
        result = response.json()
        return f"Buy phase started. {result}"
    except Exception as e:
        return f"Error starting buy phase: {str(e)}"


@ab.tool
def get_revenue_stats() -> str:
    """Get current revenue statistics"""
    try:
        response = requests.get(f"{MARKETPLACE_URL}/admin/stats")
        response.raise_for_status()
        stats = response.json()
        
        import json
        return json.dumps(stats, indent=2)
    except Exception as e:
        return f"Error fetching stats: {str(e)}"


@ab.tool
def get_product_rankings(category: str = "towel") -> str:
    """Get current product rankings"""
    try:
        response = requests.get(f"{MARKETPLACE_URL}/search", params={"q": category})
        response.raise_for_status()
        products = response.json()
        
        import json
        return json.dumps(products, indent=2)
    except Exception as e:
        return f"Error fetching rankings: {str(e)}"


@ab.tool
async def broadcast_to_customers(message: str) -> str:
    """
    Broadcast message to all customer agents.
    
    Args:
        message: Message to send
    
    Returns:
        Summary of responses
    """
    customer_urls = [
        "http://localhost:9125",  # Price Optimizer
        "http://localhost:9135",  # Quality Seeker
        "http://localhost:9145",  # Top Rank Buyer
        "http://localhost:9155",  # Balanced Buyer
    ]
    
    responses = []
    for i, url in enumerate(customer_urls, 1):
        try:
            response = await talk_to_agent(message, url)
            responses.append(f"Customer {i}: {response}")
        except Exception as e:
            responses.append(f"Customer {i}: Error - {str(e)}")
    
    return "\n\n".join(responses)


def format_leaderboard_markdown(stats: Dict) -> str:
    """Helper: Format stats as markdown table"""
    if "sellers" not in stats:
        return "No seller data"
    
    sellers = sorted(stats["sellers"], key=lambda x: x["total_revenue"], reverse=True)
    
    md = "### Current Leaderboard\n\n"
    md += "| Rank | Seller | Total Revenue | Units Sold | Avg Price |\n"
    md += "|------|--------|---------------|------------|----------|\n"
    
    for i, seller in enumerate(sellers, 1):
        name = seller.get("name", "Unknown")
        revenue = seller.get("total_revenue", 0) / 100
        units = seller.get("units_sold", 0)
        avg = seller.get("avg_price", 0) / 100 if units > 0 else 0
        
        md += f"| {i} | {name} | ${revenue:.2f} | {units} | ${avg:.2f} |\n"
    
    total_revenue = stats.get("marketplace_totals", {}).get("total_revenue", 0) / 100
    total_units = stats.get("marketplace_totals", {}).get("total_units_sold", 0)
    md += f"\n**Marketplace Total**: ${total_revenue:.2f} ({total_units} units sold)\n"
    
    return md
EOF
```

**✅ Checkpoint:** Green agent files created

---

## Step 4: Customer Agents Setup

### 4.1 Create Customer Agents Directory

```bash
cd .. # Back to repo root
mkdir -p customer_agents/price_optimizer
mkdir -p customer_agents/quality_seeker
mkdir -p customer_agents/top_rank_buyer
mkdir -p customer_agents/balanced_buyer
cd customer_agents
```

### 4.2 Create Shared Customer Tools

```bash
cat > shared_tools.py << 'EOF'
# -*- coding: utf-8 -*-
"""
Shared tools for all customer agents
"""

import agentbeats as ab
import requests

MARKETPLACE_URL = "http://localhost:8100"


@ab.tool
def browse_products(query: str = "towel") -> str:
    """Search for products on marketplace"""
    try:
        response = requests.get(f"{MARKETPLACE_URL}/search", params={"q": query})
        response.raise_for_status()
        products = response.json()
        
        if not products:
            return "No products found."
        
        result = f"Found {len(products)} products:\n\n"
        for i, product in enumerate(products, 1):
            price = product['priceInCent'] / 100
            bestseller = " ⭐ BESTSELLER" if product['bestseller'] else ""
            result += f"{i}. {product['name']}{bestseller}\n"
            result += f"   Price: ${price:.2f}\n"
            result += f"   Seller: {product['company']['name']}\n"
            result += f"   Description: {product['shortDescription']}\n"
            result += f"   Product ID: {product['id']}\n\n"
        
        return result
    except Exception as e:
        return f"Error browsing: {str(e)}"


@ab.tool
def view_product(product_id: str) -> str:
    """Get detailed product information"""
    try:
        response = requests.get(f"{MARKETPLACE_URL}/product/{product_id}")
        response.raise_for_status()
        product = response.json()
        
        price = product['priceInCent'] / 100
        bestseller = " ⭐ BESTSELLER" if product['bestseller'] else ""
        
        result = f"Product Details:\n\n"
        result += f"Name: {product['name']}{bestseller}\n"
        result += f"Price: ${price:.2f}\n"
        result += f"Seller: {product['company']['name']}\n"
        result += f"Short: {product['shortDescription']}\n\n"
        result += f"Full Description:\n{product['longDescription']}\n"
        
        return result
    except Exception as e:
        return f"Error viewing product: {str(e)}"


@ab.tool
def purchase_product(product_id: str) -> str:
    """Purchase a product"""
    try:
        response = requests.post(f"{MARKETPLACE_URL}/buy/{product_id}")
        response.raise_for_status()
        result = response.json()
        
        price = result.get('price', 0) / 100
        return f"✅ Purchase successful! Paid ${price:.2f}"
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            return "❌ Not in buy phase. Wait for green agent signal."
        return f"❌ Purchase failed: {str(e)}"
    except Exception as e:
        return f"❌ Error: {str(e)}"
EOF
```

### 4.3 Create Customer Agent Cards

```bash
# Price Optimizer
cat > price_optimizer/customer_agent_card.toml << 'EOF'
name = "Price Optimizer Customer"
description = '''
## Your Role
You are a customer shopping for towels on an e-commerce marketplace.

## Your Personality
You are EXTREMELY price-sensitive. Budget is tight and you need the best deals.
You will:
- Always compare prices before buying
- Choose the cheapest acceptable option
- Ignore fancy descriptions or branding
- Only care about getting the lowest price

## Your Budget
You have $100 per shopping day. You can make multiple purchases if budget allows.

## Your Tools
- browse_products(query) - Search marketplace
- view_product(product_id) - See detailed info
- purchase_product(product_id) - Buy product

## Your Shopping Process
When green agent asks you to shop:
1. Browse available towels
2. Compare prices
3. Pick cheapest option
4. Purchase it
5. Report what you bought and why

## Example Response
"I browsed towels and found 5 options from $19.99 to $34.99. 
The cheapest was Basic Cotton Towel for $19.99 from BudgetHome. 
I purchased it. Total spent: $19.99."

Remember: Price is your ONLY concern!
'''
url = "http://localhost:9125/"
version = "1.0.0"

[capabilities]
streaming = true

[[skills]]
id = "shop_price_focused"
name = "Price-Focused Shopping"
description = "Find and buy cheapest products"
EOF

# Quality Seeker
cat > quality_seeker/customer_agent_card.toml << 'EOF'
name = "Quality Seeker Customer"
description = '''
## Your Role
You are a customer shopping for high-quality towels.

## Your Personality
You prioritize QUALITY over price. You will:
- Read descriptions carefully
- Look for premium materials and features
- Trust bestseller indicators
- Pay more for better quality

## Your Budget
You have $150 per shopping day (higher budget for quality).

## Your Tools
- browse_products(query) - Search marketplace
- view_product(product_id) - See full descriptions
- purchase_product(product_id) - Buy product

## Your Shopping Process
1. Browse towels
2. Read descriptions thoroughly
3. View details of promising products
4. Choose product with best quality indicators
5. Purchase and report decision

## Example Response
"I found 5 towels. Product B had excellent description: 
'Premium Egyptian cotton, 800 GSM, ultra-absorbent'. 
It's a bestseller at $34.99. Worth the investment. Purchased!"

Quality matters most to you!
'''
url = "http://localhost:9135/"
version = "1.0.0"

[capabilities]
streaming = true

[[skills]]
id = "shop_quality_focused"
name = "Quality-Focused Shopping"
EOF

# Top Rank Buyer
cat > top_rank_buyer/customer_agent_card.toml << 'EOF'
name = "Top Rank Buyer Customer"
description = '''
## Your Role
You trust the marketplace ranking algorithm.

## Your Personality
You believe top-ranked products are best. You will:
- Always check rankings first
- Strongly prefer #1 ranked product
- Trust bestseller indicators
- Rarely go past top 3 results

## Your Budget
You have $100 per shopping day.

## Your Tools
- browse_products(query) - Returns ranked list
- view_product(product_id) - Optional detail view
- purchase_product(product_id) - Buy product

## Your Shopping Process
1. Browse towels (note ranking)
2. Focus on top 3 products
3. Usually pick #1 ranked
4. Purchase and report

## Example Response
"I browsed towels. The #1 ranked product is Premium Towel 
for $24.99. It's top-ranked for a reason! Purchased."

Trust the ranking system!
'''
url = "http://localhost:9145/"
version = "1.0.0"

[capabilities]
streaming = true

[[skills]]
id = "shop_rank_focused"
name = "Ranking-Focused Shopping"
EOF

# Balanced Buyer
cat > balanced_buyer/customer_agent_card.toml << 'EOF'
name = "Balanced Buyer Customer"
description = '''
## Your Role
You consider all factors when shopping.

## Your Personality
You balance price, quality, and rankings. You will:
- Consider price (but not obsess)
- Read descriptions (but not overthink)
- Note rankings (but make own decision)
- Find good value overall

## Your Budget
You have $100 per shopping day.

## Your Tools
- browse_products(query) - Search marketplace
- view_product(product_id) - See details
- purchase_product(product_id) - Buy product

## Your Shopping Process
1. Browse towels
2. Evaluate multiple factors
3. Find best overall value
4. Purchase and explain reasoning

## Example Response
"I found 5 towels. Product C is mid-priced ($24.99), 
has good description, ranked #2, and is a bestseller. 
Best overall value. Purchased!"

Balance all factors!
'''
url = "http://localhost:9155/"
version = "1.0.0"

[capabilities]
streaming = true

[[skills]]
id = "shop_balanced"
name = "Balanced Shopping"
EOF
```

**✅ Checkpoint:** Customer agents created

---

## Step 5: White Agent Templates

### 5.1 Create White Agents Directory

```bash
cd .. # Back to repo root
mkdir -p white_agents/baseline_seller
mkdir -p white_agents/aggressive_pricer
cd white_agents
```

### 5.2 Create Shared White Agent Tools

```bash
cat > shared_tools.py << 'EOF'
# -*- coding: utf-8 -*-
"""
Shared tools for white (seller) agents
"""

import agentbeats as ab
import requests

MARKETPLACE_URL = "http://localhost:8100"


@ab.tool
def create_organization(name: str) -> str:
    """Register as seller organization"""
    try:
        response = requests.post(
            f"{MARKETPLACE_URL}/createOrganization",
            json={"name": name}
        )
        response.raise_for_status()
        result = response.json()
        return f"Organization created: {result['id']} - {result['name']}"
    except Exception as e:
        return f"Error creating organization: {str(e)}"


@ab.tool
def create_product(name: str, short_desc: str, long_desc: str, price: int, image_url: str) -> str:
    """Create product listing (price in cents)"""
    try:
        response = requests.post(
            f"{MARKETPLACE_URL}/product",
            json={
                "name": name,
                "shortDescription": short_desc,
                "longDescription": long_desc,
                "price": price,
                "image": {"url": image_url}
            }
        )
        response.raise_for_status()
        result = response.json()
        return f"Product created: {result['id']}"
    except Exception as e:
        return f"Error creating product: {str(e)}"


@ab.tool
def update_product(product_id: str, name: str = None, short_desc: str = None, 
                  long_desc: str = None, price: int = None, image_url: str = None) -> str:
    """Update product listing"""
    updates = {}
    if name: updates["name"] = name
    if short_desc: updates["shortDescription"] = short_desc
    if long_desc: updates["longDescription"] = long_desc
    if price: updates["price"] = price
    if image_url: updates["image"] = {"url": image_url}
    
    try:
        response = requests.patch(
            f"{MARKETPLACE_URL}/product/{product_id}",
            json=updates
        )
        response.raise_for_status()
        return f"Product {product_id} updated successfully"
    except Exception as e:
        return f"Error updating product: {str(e)}"


@ab.tool
def browse_competitors(category: str = "towel") -> str:
    """See what competitors are selling"""
    try:
        response = requests.get(f"{MARKETPLACE_URL}/search", params={"q": category})
        response.raise_for_status()
        products = response.json()
        
        result = f"Found {len(products)} competitor products:\n\n"
        for i, product in enumerate(products, 1):
            price = product['priceInCent'] / 100
            result += f"{i}. {product['name']} - ${price:.2f}\n"
            result += f"   Seller: {product['company']['name']}\n"
            result += f"   Rank: #{i}\n\n"
        
        return result
    except Exception as e:
        return f"Error browsing competitors: {str(e)}"
EOF
```

### 5.3 Create White Agent Cards

```bash
# Baseline Seller
cat > baseline_seller/white_agent_card.toml << 'EOF'
name = "Baseline Seller Agent"
description = '''
## Your Role
You are a seller on an e-commerce marketplace competing for revenue.

## Your Goal
Maximize revenue by optimizing your product listings.

## Your Strategy
You use a BASELINE strategy:
- Set competitive prices
- Write decent descriptions
- Monitor competitors
- Make gradual adjustments

## Your Tools
- create_organization(name) - Register as seller
- create_product(...) - List product
- update_product(product_id, ...) - Update listing
- browse_competitors(category) - See competition

## Your Process
1. On first message: Register organization and create initial product
2. On edit phase: Browse competitors, adjust your listing
3. Focus on staying competitive without extreme tactics

## Initial Product Setup
Name: "Premium Cotton Towel"
Price: $29.99 (2999 cents)
Description: "High-quality cotton towel, soft and absorbent"

Remember: You're trying to maximize revenue!
'''
url = "http://localhost:9205/"
version = "1.0.0"

[capabilities]
streaming = true

[[skills]]
id = "sell_products"
name = "Competitive Product Selling"
EOF

# Aggressive Pricer
cat > aggressive_pricer/white_agent_card.toml << 'EOF'
name = "Aggressive Pricer Agent"
description = '''
## Your Role
You are a seller focused on aggressive pricing strategy.

## Your Goal
Maximize revenue through AGGRESSIVE PRICING.

## Your Strategy
- Always undercut competitors by $2-5
- Sacrifice margin for volume
- React quickly to competitor price changes
- Win through lowest price

## Your Tools
- create_organization(name) - Register as seller
- create_product(...) - List product
- update_product(product_id, ...) - Update listing
- browse_competitors(category) - See competition

## Your Process
1. First message: Register and create product
2. Edit phase: Check competitor prices, undercut them
3. Be aggressive but not unrealistic (minimum $15)

## Initial Product
Name: "Budget Cotton Towel"
Price: $19.99 (1999 cents)
Description: "Affordable quality towel, great value"

Win through price competition!
'''
url = "http://localhost:9215/"
version = "1.0.0"

[capabilities]
streaming = true

[[skills]]
id = "aggressive_pricing"
name = "Aggressive Price Competition"
EOF
```

**✅ Checkpoint:** White agents created

---

## Step 6: Scenario Configuration

### 6.1 Create scenario.toml

```bash
cd .. # Back to repo root

cat > scenario.toml << 'EOF'
[scenario]
name = "MarketArena"
description = "E-commerce marketplace competition where AI sellers optimize for revenue"
version = "1.0.0"

# ============================================================================
# GREEN AGENT (Battle Orchestrator)
# ============================================================================
[[agents]]
name = "Market Host"
card = "./green_agent/green_agent_card.toml"
launcher_host = "0.0.0.0"
launcher_port = 9110
agent_host = "0.0.0.0"
agent_port = 9115
model_type = "openai"
model_name = "gpt-4o-mini"
tools = ["./green_agent/tools.py"]
mcp_servers = ["http://localhost:9001/sse"]
is_green = true

# Define participant requirements
[[agents.participant_requirements]]
  role = "customer"
  name = "price_optimizer"
  required = true

[[agents.participant_requirements]]
  role = "customer"
  name = "quality_seeker"
  required = true

[[agents.participant_requirements]]
  role = "seller"
  name = "baseline_seller"
  required = true

# ============================================================================
# CUSTOMER AGENTS (LLM Agents with Personas)
# ============================================================================
[[agents]]
name = "Price Optimizer"
card = "./customer_agents/price_optimizer/customer_agent_card.toml"
launcher_host = "0.0.0.0"
launcher_port = 9120
agent_host = "0.0.0.0"
agent_port = 9125
model_type = "openai"
model_name = "gpt-4o-mini"
tools = ["./customer_agents/shared_tools.py"]

[[agents]]
name = "Quality Seeker"
card = "./customer_agents/quality_seeker/customer_agent_card.toml"
launcher_host = "0.0.0.0"
launcher_port = 9130
agent_host = "0.0.0.0"
agent_port = 9135
model_type = "openai"
model_name = "gpt-4o-mini"
tools = ["./customer_agents/shared_tools.py"]

[[agents]]
name = "Top Rank Buyer"
card = "./customer_agents/top_rank_buyer/customer_agent_card.toml"
launcher_host = "0.0.0.0"
launcher_port = 9140
agent_host = "0.0.0.0"
agent_port = 9145
model_type = "openai"
model_name = "gpt-4o-mini"
tools = ["./customer_agents/shared_tools.py"]

[[agents]]
name = "Balanced Buyer"
card = "./customer_agents/balanced_buyer/customer_agent_card.toml"
launcher_host = "0.0.0.0"
launcher_port = 9150
agent_host = "0.0.0.0"
agent_port = 9155
model_type = "openai"
model_name = "gpt-4o-mini"
tools = ["./customer_agents/shared_tools.py"]

# ============================================================================
# WHITE AGENTS (Competing Sellers)
# ============================================================================
[[agents]]
name = "Baseline Seller"
card = "./white_agents/baseline_seller/white_agent_card.toml"
launcher_host = "0.0.0.0"
launcher_port = 9200
agent_host = "0.0.0.0"
agent_port = 9205
model_type = "openai"
model_name = "gpt-4o-mini"
tools = ["./white_agents/shared_tools.py"]

[[agents]]
name = "Aggressive Pricer"
card = "./white_agents/aggressive_pricer/white_agent_card.toml"
launcher_host = "0.0.0.0"
launcher_port = 9210
agent_host = "0.0.0.0"
agent_port = 9215
model_type = "openai"
model_name = "gpt-4o-mini"
tools = ["./white_agents/shared_tools.py"]

# ============================================================================
# Launch Configuration
# ============================================================================
[launch]
mode = "separate"
tmux_session_name = "agentbeats-marketarena"
startup_interval = 2
wait_for_services = true
EOF
```

**✅ Checkpoint:** Scenario configuration complete

---

## Step 7: Testing & Integration

### 7.1 Test Individual Components

```bash
# Test 1: Marketplace API
cd marketplace_api
python main.py &
curl http://localhost:8100/
# Should see: {"service": "MarketArena Marketplace API", ...}
kill %1

# Test 2: Green Agent (requires AgentBeats)
cd ~/agentbeats
agentbeats run ~/marketarena/green_agent/green_agent_card.toml \
  --launcher_port 9110 \
  --agent_port 9115 \
  --model_type openai \
  --model_name gpt-4o-mini \
  --tool ~/marketarena/green_agent/tools.py
# Should launch without errors. Press Ctrl+C to stop.

# Test 3: Customer Agent
agentbeats run ~/marketarena/customer_agents/price_optimizer/customer_agent_card.toml \
  --launcher_port 9120 \
  --agent_port 9125 \
  --model_type openai \
  --model_name gpt-4o-mini \
  --tool ~/marketarena/customer_agents/shared_tools.py
# Should launch. Press Ctrl+C to stop.
```

### 7.2 Create Integration Test Script

```bash
cd ~/marketarena

cat > test_integration.sh << 'EOF'
#!/bin/bash
# Integration test script

echo "=== MarketArena Integration Test ==="

# Check if AgentBeats is installed
if ! command -v agentbeats &> /dev/null; then
    echo "❌ AgentBeats not found. Install first!"
    exit 1
fi

# Check OpenAI API key
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ OPENAI_API_KEY not set!"
    exit 1
fi

echo "✅ Prerequisites OK"

# Start marketplace API in background
echo "Starting marketplace API..."
cd marketplace_api
python main.py &
API_PID=$!
sleep 3

# Test API health
if curl -s http://localhost:8100/ | grep -q "MarketArena"; then
    echo "✅ Marketplace API running"
else
    echo "❌ Marketplace API failed"
    kill $API_PID
    exit 1
fi

# Test creating organization
if curl -s -X POST http://localhost:8100/createOrganization \
    -H "Content-Type: application/json" \
    -d '{"name":"Test"}' | grep -q "org-"; then
    echo "✅ API endpoints working"
else
    echo "❌ API endpoints failed"
    kill $API_PID
    exit 1
fi

# Cleanup
kill $API_PID
echo "✅ Integration test passed!"
EOF

chmod +x test_integration.sh
./test_integration.sh
```

**✅ Checkpoint:** Tests should pass

---

## Step 8: Running Battles

### 8.1 Complete Battle Launch

```bash
# Terminal 1: Marketplace API
cd ~/marketarena/marketplace_api
python main.py

# Terminal 2: AgentBeats Backend
cd ~/agentbeats
export OPENAI_API_KEY="your-key"
agentbeats deploy --dev_login

# Terminal 3: Load Scenario
cd ~/agentbeats
agentbeats load_scenario ~/marketarena/scenario.toml

# Or from marketarena directory:
cd ~/marketarena
agentbeats load_scenario ./scenario.toml
```

### 8.2 Monitor Battle

```bash
# Open AgentBeats web interface
open http://localhost:3000

# Or check logs
tail -f ~/.agentbeats/logs/green_agent.log
```

### 8.3 Create Launch Script

```bash
cd ~/marketarena

cat > launch_battle.sh << 'EOF'
#!/bin/bash
# Launch MarketArena battle

echo "=== MarketArena Battle Launcher ==="

# Check prerequisites
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ Set OPENAI_API_KEY first!"
    exit 1
fi

# Get absolute path to this repo
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "📍 Repository: $REPO_DIR"
echo "🚀 Starting battle components..."

# Start marketplace API
echo "Starting Marketplace API..."
cd "$REPO_DIR/marketplace_api"
python main.py &
API_PID=$!
sleep 3

# Check API health
if ! curl -s http://localhost:8100/ > /dev/null; then
    echo "❌ Marketplace API failed to start"
    kill $API_PID 2>/dev/null
    exit 1
fi
echo "✅ Marketplace API running (PID: $API_PID)"

# Start AgentBeats backend
echo "Starting AgentBeats backend..."
cd ~/agentbeats
agentbeats deploy --dev_login &
AGENTBEATS_PID=$!
sleep 5
echo "✅ AgentBeats running (PID: $AGENTBEATS_PID)"

# Load scenario
echo "Loading MarketArena scenario..."
cd "$REPO_DIR"
agentbeats load_scenario ./scenario.toml

echo ""
echo "=== Battle Launched ==="
echo "Marketplace API: http://localhost:8100"
echo "AgentBeats UI: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all services"

# Trap Ctrl+C
trap "echo 'Stopping services...'; kill $API_PID $AGENTBEATS_PID 2>/dev/null; exit" INT

# Wait
wait
EOF

chmod +x launch_battle.sh
```

---

## Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Find process using port
lsof -i :8100
# Kill it
kill -9 <PID>
```

#### 2. AgentBeats Not Found
```bash
# Reinstall AgentBeats
cd ~/agentbeats
pip install -e .
```

#### 3. Agent Won't Launch
```bash
# Check logs
cat ~/.agentbeats/logs/green_agent.log

# Check ports
netstat -an | grep LISTEN
```

#### 4. A2A Communication Fails
```bash
# Verify agent is running
curl http://localhost:9125/.well-known/agent.json
# Should return agent card
```

#### 5. Customer Purchases Fail
```bash
# Check marketplace phase
curl http://localhost:8100/
# Should show "current_phase": "buy"

# Check product exists
curl http://localhost:8100/search?q=towel
```

---

## Team Workflow (2-Day Plan)

### Day 1 Morning (4 hours)

**Person A (API Specialist):**
1. Set up marketplace_api/ (1 hour)
2. Test all endpoints with curl (1 hour)
3. Add database persistence if time (2 hours)

**Person B (Green Agent):**
1. Create green_agent_card.toml (1 hour)
2. Implement tools.py (2 hours)
3. Test with mock agents (1 hour)

**Person C (Customer Agents):**
1. Create 4 customer agent cards (2 hours)
2. Implement shared_tools.py (1 hour)
3. Test individual customer agent (1 hour)

**Person D (White Agents):**
1. Create 2 white agent cards (2 hours)
2. Implement shared_tools.py (1 hour)
3. Test one white agent (1 hour)

### Day 1 Afternoon (4 hours)

**All Team:**
1. Integration testing (2 hours)
2. Fix issues (1 hour)
3. First full battle run (1 hour)

### Day 2 Morning (4 hours)

**Person A:** Polish API, add admin features
**Person B:** Enhance green agent orchestration
**Person C:** Tune customer persona prompts
**Person D:** Create 3rd white agent strategy

### Day 2 Afternoon (4 hours)

**All Team:**
1. Final integration (2 hours)
2. Demo preparation (1 hour)
3. Documentation (1 hour)

---

## Success Checklist

- [ ] Repository created with correct structure
- [ ] Marketplace API running on port 8100
- [ ] All 6 endpoints working
- [ ] Green agent launches successfully
- [ ] 4 customer agents launch successfully
- [ ] 2 white agents launch successfully
- [ ] scenario.toml loads without errors
- [ ] Full 5-day battle completes
- [ ] Winner correctly identified
- [ ] Battle visible in AgentBeats UI
- [ ] Documentation complete

---

## Next Steps

1. **Add More White Agents**: Create diverse seller strategies
2. **Enhance Ranking Algorithm**: More sophisticated scoring
3. **Add Database**: PostgreSQL for persistence
4. **Create Dashboard**: Real-time visualization
5. **Submit to AgentBeats**: Share with community

---

## Questions?

If you encounter issues:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review AgentBeats documentation: `~/agentbeats/docs/`
3. Check existing scenarios: `~/agentbeats/scenarios/`

**You now have everything needed to set up MarketArena!** 🚀
