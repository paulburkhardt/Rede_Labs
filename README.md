# MarketArena: E-Commerce Marketplace Simulation

![Banner](images/banner.jpg)

A FastAPI-based marketplace backend with PostgreSQL database for managing sellers, products, and purchases. This is the backend infrastructure for **MarketArena**, a benchmark that evaluates AI agents' ability to maximize profit through strategic product optimization in competitive e-commerce settings.

## 📚 Documentation

**→ [GREEN_AGENT_DOCUMENTATION.md](GREEN_AGENT_DOCUMENTATION.md)** - Complete technical documentation covering:
- Task introduction and environment structure
- Agent actions and evaluation methodology
- Concrete examples and quantitative results
- Visual diagrams and architecture details

## Project Structure

```
Rede_Labs/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration settings
│   ├── database.py          # Database connection and session
│   ├── models/              # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── seller.py
│   │   ├── product.py
│   │   └── purchase.py
│   ├── schemas/             # Pydantic schemas for request/response
│   │   ├── __init__.py
│   │   ├── seller.py
│   │   ├── product.py
│   │   └── purchase.py
│   └── routers/             # API route handlers
│       ├── __init__.py
│       ├── sellers.py
│       ├── products.py
│       ├── search.py
│       └── purchases.py
├── alembic/                 # Database migrations
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
├── pyproject.toml           # Project dependencies (uv)
├── docker-compose.yml       # PostgreSQL + Backend containers
├── Dockerfile               # Backend container definition
├── run.py                   # Development server runner
└── README.md
```

## Prerequisites

- Docker and Docker Compose
- Python 3.11+ and [uv](https://github.com/astral-sh/uv) for local development

## Setup Instructions

#### 1. Install dependencies

```bash
uv sync
```

#### 2. Create .env file

Copy the example environment file and adjust if needed:

```bash
cp .env.example .env
```

#### 3. Start Database & Backend

```bash
docker-compose up -d
```

This will start:
- **PostgreSQL** container:
  - User: `marketplace_user`
  - Password: `marketplace_pass`
  - Database: `marketplace_db`
  - Port: `5432`
- **Backend API** container:
  - FastAPI application
  - Port: `8000`
  - Auto-reloads on code changes
  - Interactive Docs: http://localhost:8000/docs
  - ReDoc: http://localhost:8000/redoc

#### 4. Run Database Migrations

```bash
# Run migrations
docker-compose exec backend alembic upgrade head

# Create image descriptions
uv run images/create_image_descriptions.py
```

#### 5. Install AgentBeats

1. Clone repository: `git clone https://github.com/agentbeats/agentbeats.git`
2. Navigate to the directory: `cd agentbeats`
3. Create a virtual environment: `python3 -m venv venv`
4. Source the virtual environment: `source venv/bin/activate`
5. Install AgentBeats: `pip install -e .`
6. Add virtual environment to PATH:
```
BIN_PATH=$(pwd)/venv/bin
echo "export PATH=$BIN_PATH:$PATH" >> ~/.zshrc
source ~/.zshrc
```
(The 6th step is necessary because our scripts require the `agentbeats` CLI to be available in the PATH)

#### 6. Start Buyer and Seller Agents (White Agents)

```bash
uv run tools/start_agents.py --num-buyers 10 --num-sellers 10
```

This will start 10 buyer and 10 seller agents. The main task of other teams will be to implement their own seller agent. However, they can use our basic seller agent as reference.

In `tools/scenario.toml` are the ports and hosts of the agents. Expand the following section to see the default ports and hosts.

<details>
<summary>Default ports and hosts</summary>

### 🧩 Green Agent (Orchestrator)
- **Agent:** `http://0.0.0.0:9110`  
- **Launcher:** `http://0.0.0.0:9115`  
- **Tools:** `/agents/green_agent/green_agent_tools.py`

### 🛒 Buyer Agents

| Buyer | Personality | Agent Port | Launcher Port | Tools |
|--------|--------------|-------------|----------------|--------|
| Buyer 1 | price_conscious | `9200` | `9300` | `/agents/buyer/shared_tools.py` |
| Buyer 2 | price_conscious | `9201` | `9301` | `/agents/buyer/shared_tools.py` |
| Buyer 3 | quality_seeker | `9202` | `9302` | `/agents/buyer/shared_tools.py` |
| Buyer 4 | confused_overchoice | `9203` | `9303` | `/agents/buyer/shared_tools.py` |
| Buyer 5 | confused_overchoice | `9204` | `9304` | `/agents/buyer/shared_tools.py` |
| Buyer 6 | hedonistic_shopper | `9205` | `9305` | `/agents/buyer/shared_tools.py` |
| Buyer 7 | hedonistic_shopper | `9206` | `9306` | `/agents/buyer/shared_tools.py` |
| Buyer 8 | brand_conscious | `9207` | `9307` | `/agents/buyer/shared_tools.py` |
| Buyer 9 | brand_conscious | `9208` | `9308` | `/agents/buyer/shared_tools.py` |
| Buyer 10 | brand_conscious | `9209` | `9309` | `/agents/buyer/shared_tools.py` |

---

### 💰 Seller Agents

| Seller | Strategy | Agent Port | Launcher Port | Tools |
|---------|------------|-------------|----------------|--------|
| Seller 1 | budget_king | `10000` | `10100` | `/agents/seller/shared_tools.py` |
| Seller 2 | budget_king | `10001` | `10101` | `/agents/seller/shared_tools.py` |
| Seller 3 | budget_king | `10002` | `10102` | `/agents/seller/shared_tools.py` |
| Seller 4 | dynamic_optimizer | `10003` | `10103` | `/agents/seller/shared_tools.py` |
| Seller 5 | dynamic_optimizer | `10004` | `10104` | `/agents/seller/shared_tools.py` |
| Seller 6 | dynamic_optimizer | `10005` | `10105` | `/agents/seller/shared_tools.py` |
| Seller 7 | premium_player | `10006` | `10106` | `/agents/seller/shared_tools.py` |
| Seller 8 | premium_player | `10007` | `10107` | `/agents/seller/shared_tools.py` |
| Seller 9 | premium_player | `10008` | `10108` | `/agents/seller/shared_tools.py` |

</details>

\
You can kill the agents with:
```bash
uv run tools/kill_agents.py
```

## Deployment

To deploy this project so that you can use the agents on https://agentbeats.org, you need to:

1. Create a VM (we used Hetzner)
2. Follow setup instructions from above. Use for `agentbeats` in the steps above not https://github.com/agentbeats/agentbeats.git but https://github.com/nilsreder/agentbeats.git (a fork that fixes the issues that AgentBeats always uses http://localhost:9000 as backend_url). Also use `online` branch of this repository.
3. Use `uv run tools/start_agents.py --num-buyers 5 --num-sellers 3 --online`
4. Install `cloudflared`
5. Get `~/.cloudflared/e12b9afa-5ce5-424f-9181-04a4db4746cf.json` from @nilsreichardt
6. Run `tmux new -s cloudflare` and then `cd Rede_Labs && cloudflared --config ./cloudflared.yml tunnel run redelabs-nils`, then `ctrl + b` and `d`

## Development

### Running Tests

```bash
uv run pytest
```

### Database Management

```bash
# Create a new migration
uv run alembic revision --autogenerate -m "Description"

# Apply migrations
uv run alembic upgrade head

# Rollback one migration
uv run alembic downgrade -1

# View migration history
uv run alembic history
```

### Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove data volumes
docker-compose down -v

# View logs
docker-compose logs -f backend
docker-compose logs -f postgres
```

## Testing

The API includes comprehensive integration tests that clear and seed the database before each test.

### Run All Tests

```bash
uv run pytest tests/ -v
```

### Run Specific Test File

```bash
uv run pytest tests/test_products.py -v
```

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Migrations**: Alembic
- **Validation**: Pydantic
- **Package Manager**: uv
- **Server**: Uvicorn
- **Testing**: pytest + httpx TestClient
- **AI**: OpenAI

## Tmux Setup

To view the logs of the agents, you can use tmux. This is optional and only needed for debugging.

### Enable logs

Add this to your `~/.tmux.conf`:

```conf
# Ensure the log directory exists
run-shell "mkdir -p ~/tmux-logs"

# Start logging for panes created by splitting
set-hook -g after-split-window  'run-shell "tmux pipe-pane -o -t #{pane_id} \"cat >> ~/tmux-logs/#{session_name}_#{window_index}_#{pane_index}.log\" "'

# Start logging for the initial pane of new windows
set-hook -g after-new-window    'run-shell "tmux pipe-pane -o -t #{pane_id} \"cat >> ~/tmux-logs/#{session_name}_#{window_index}_#{pane_index}.log\" "'

# Also cover panes that already exist when a client attaches (first session, restarts, etc.)
set-hook -g client-attached 'run-shell "for p in $(tmux list-panes -a -F \"#{pane_id}\"); do tmux pipe-pane -o -t \"$p\" \"cat >> ~/tmux-logs/#{session_name}_#{window_index}_#{pane_index}.log\"; done"'
```

Run `tmux source-file ~/.tmux.conf` to apply the changes.

The logs are stored in `~/tmux-logs`.

### Enable scrolling

Add this to your `~/.tmux.conf`:

```conf
set -g mouse on
```

Run `tmux source-file ~/.tmux.conf` to apply the changes.
