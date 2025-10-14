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
