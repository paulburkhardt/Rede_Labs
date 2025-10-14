#!/bin/bash
# Launch MarketArena battle

echo "=== MarketArena Battle Launcher ==="

# Check prerequisites
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ Set OPENAI_API_KEY first!"
    exit 1
fi

# Set OPENROUTER_API_KEY to bypass AgentBeats requirement
# (We're using OpenAI, but AgentBeats checks for this)
if [ -z "$OPENROUTER_API_KEY" ]; then
    export OPENROUTER_API_KEY="$OPENAI_API_KEY"
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
cd ~/Github/agentbeats
agentbeats deploy &
AGENTBEATS_PID=$!
sleep 5
echo "✅ AgentBeats running (PID: $AGENTBEATS_PID)"

# Load scenario
echo "Loading MarketArena scenario..."
agentbeats load_scenario "$REPO_DIR"

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
