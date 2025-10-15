# Starting MarketArena Battles - Complete Guide

## ✅ Current Status
Your setup is complete and agents are loaded! Here's what's running:

- ✅ Marketplace API: http://localhost:8100
- ✅ AgentBeats Backend: http://localhost:9000
- ✅ AgentBeats Frontend: http://localhost:5173
- ✅ 7 Agents in tmux session: `agentbeats-marketarena`

## 🎮 How to Actually Start a Battle

AgentBeats has two modes:

### **Mode 1: load_scenario** (What you did)
- Loads agents and waits
- Agents are in standby
- **Need to manually trigger through UI**

### **Mode 2: run_scenario** (Automatic)
- Loads agents AND starts battle automatically
- Green agent begins immediately

## 🚀 Option A: Use run_scenario (Recommended)

This will automatically start everything:

```bash
# First, kill current session
tmux kill-session -t agentbeats-marketarena

# Make sure marketplace API is running
# (Check Terminal 2)

# Make sure AgentBeats backend is running  
# (Check Terminal 3)

# Then run the scenario (this auto-starts battle)
agentbeats run_scenario /Users/pauld/Github/Rede_Labs
```

## 🎯 Option B: Start Through UI

1. Open AgentBeats UI:
   ```bash
   open http://localhost:5173
   ```

2. In the UI:
   - Look for "Scenarios" or "Agents" section
   - Find "Market Host" (Green Agent)
   - Click on it
   - Look for "Start" or "Send Message" button
   - Send: "Begin the MarketArena battle with 5 days of competition"

## 🔧 Option C: Direct Green Agent Communication

Since agents use A2A protocol, we need to send properly formatted messages.

### Method 1: Through AgentBeats Chat Interface

The green agent should have a chat interface in the UI at:
- http://localhost:5173 → Find "Market Host" → Chat with it

### Method 2: Direct A2A Message (Advanced)

Check the green agent's actual message endpoint:

```bash
# Get agent card to see available endpoints
curl -s http://localhost:9115/.well-known/agent-card.json | jq '.capabilities'
```

## 📊 Monitor Battle Progress

Once started (by any method), monitor with:

```bash
# Watch green agent
tail -f ~/.agentbeats/logs/Market\ Host.log

# Check marketplace
curl http://localhost:8100/ | jq

# Overall status
./monitor_battle.sh
```

## 🎬 Recommended: Try run_scenario

This is the easiest way:

```bash
# Terminal 4 (new terminal)
cd /Users/pauld/Github/Rede_Labs

# Kill existing agents
tmux kill-session -t agentbeats-marketarena

# Run scenario (auto-starts battle)
agentbeats run_scenario /Users/pauld/Github/Rede_Labs

# Then in another terminal, watch:
tail -f ~/.agentbeats/logs/Market\ Host.log
```

## 🐛 What's Happening Now

Your agents are loaded but waiting for a battle initialization message. 

The `load_scenario` command:
- ✅ Starts all agents
- ❌ Doesn't send the battle start signal

You need to either:
1. Use `run_scenario` instead (auto-starts)
2. Manually trigger from UI
3. Send A2A message to green agent

## 📝 Next Steps

Try this:
1. Keep current terminals running (API + Backend)
2. In a new terminal: `tmux kill-session -t agentbeats-marketarena`
3. Run: `agentbeats run_scenario /Users/pauld/Github/Rede_Labs`
4. Watch: `tail -f ~/.agentbeats/logs/Market\ Host.log`

This should auto-start the battle! 🚀
