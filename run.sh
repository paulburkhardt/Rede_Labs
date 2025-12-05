#!/bin/bash

# Green Agent Startup Script
# Runs all infrastructure and agents with unified output

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Marketplace Benchmark Startup${NC}"
echo -e "${BLUE}========================================${NC}"

# Cleanup function
cleanup() {
    echo -e "\n${YELLOW}Shutting down...${NC}"
    pkill -f "agentbeats" 2>/dev/null || true
    tmux kill-session -t agentbeats-marketplace 2>/dev/null || true
    docker-compose down 2>/dev/null || true
    echo -e "${GREEN}Cleanup complete${NC}"
    exit 0
}
trap cleanup SIGINT SIGTERM EXIT

# Step 1: Docker
echo -e "\n${BLUE}[1/5] Building Docker images...${NC}"
docker-compose build --quiet

echo -e "\n${BLUE}[2/5] Starting Docker services...${NC}"
docker-compose up -d

# Step 2: Wait for database
echo -e "\n${BLUE}[3/5] Waiting for database...${NC}"
for i in {1..30}; do
    if docker-compose exec -T postgres pg_isready -U marketplace_user -d marketplace_db > /dev/null 2>&1; then
        echo -e "${GREEN}Database ready!${NC}"
        break
    fi
    echo -e "${YELLOW}Waiting... (${i}/30)${NC}"
    sleep 2
done

# Step 3: Migrations
echo -e "\n${BLUE}[4/5] Running migrations...${NC}"
docker-compose exec -T backend /opt/venv/bin/alembic upgrade head 2>&1 || \
    docker-compose exec -T backend /opt/venv/bin/alembic stamp head 2>&1 || true

# Step 4: Image descriptions (skip errors)
echo -e "\n${BLUE}[5/5] Preparing data...${NC}"
uv run images/create_image_descriptions.py 2>/dev/null || true

# Step 5: Start agents with unified output
echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}Starting Agents${NC}"
echo -e "${GREEN}========================================${NC}"

exec uv run main.py
