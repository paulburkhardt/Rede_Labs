#!/bin/bash
# Simple MarketArena Battle Launcher

echo "=== MarketArena Battle Setup ==="

# Check prerequisites
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ Error: OPENAI_API_KEY not set!"
    echo "Please run: export OPENAI_API_KEY='your-key-here'"
    exit 1
fi

# Set OPENROUTER_API_KEY (AgentBeats requirement)
export OPENROUTER_API_KEY="$OPENAI_API_KEY"

echo "✅ API keys configured"
echo ""
echo "📋 Instructions:"
echo ""
echo "Open 3 separate terminal windows and run these commands:"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Terminal 1: Marketplace API"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "cd /Users/pauld/Github/Rede_Labs/marketplace_api"
echo "python main.py"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Terminal 2: AgentBeats Backend"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "export OPENROUTER_API_KEY=\"\$OPENAI_API_KEY\""
echo "cd ~/Github/agentbeats"
echo "agentbeats deploy"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Terminal 3: Load Scenario"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "agentbeats load_scenario /Users/pauld/Github/Rede_Labs"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Monitor URLs:"
echo "  - Marketplace API: http://localhost:8100"
echo "  - API Docs: http://localhost:8100/docs"
echo "  - AgentBeats UI: http://localhost:5173 (or 3000)"
echo ""
