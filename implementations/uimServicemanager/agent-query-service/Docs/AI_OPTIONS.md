# AQS: AI Options & Getting Started Without API Keys

**Current Situation:** The AQS can work in multiple modes depending on available resources.

---

## Quick Decision Guide

**Have OpenAI API key?**
→ Use `main.py` (full AI mode)

**Want to test without API key?**
→ Use `main_simple.py` (keyword matching)

**Want free local AI?**
→ Install Ollama, use `main.py` with `'ollama:llama3.2'`

---

## Available Files

### 1. `main_ai.py` - Full AI Version
**Requires:** OpenAI API key (or Ollama setup)
**Intelligence:** High - understands natural language
**Cost:** ~$1-10/month (OpenAI) or Free (Ollama)

```bash
# Setup
cp .env.example .env
# Add OPENAI_API_KEY=sk-... to .env

# Run
python main_ai.py
```

### 2. `main_keyword.py` - Keyword-Based Version ⭐ Start Here!
**Requires:** Nothing! Works immediately
**Intelligence:** Basic - keyword matching only
**Cost:** Free

```bash
# No setup needed - just run!
python main_simple.py
```

**What it does:**
- Extracts keywords from queries
- Searches catalogue with those keywords
- Returns services and intents
- No AI, no API keys, no costs

**Example:**
```
Query: "Find me weather services with forecasting"
→ Extracts: ["weather", "services", "forecasting"]
→ Searches: services matching "weather services forecasting"
→ Returns: List of weather services
```

---

## Comparison

| Feature | `main_ai.py` (AI) | `main_keyword.py` (Keyword) |
|---------|----------------|--------------------------|
| **Setup** | Needs API key or Ollama | No setup |
| **Cost** | $1-10/month or Free | Free |
| **Intelligence** | High | Basic |
| **Query Understanding** | "Find services for checking weather" → Understands intent | "weather check" → Searches keywords |
| **Complex Queries** | ✅ Yes | ❌ Limited |
| **Simple Queries** | ✅ Yes | ✅ Yes |
| **Dependencies** | OpenAI/Ollama | None |

---

## Testing Right Now (No API Key Needed)

### Step 1: Use Keyword-Based Version

```bash
cd agent-query-service

# Run keyword version
python main_keyword.py
```

### Step 2: Test It

```bash
# In another terminal
python test_agent.py
```

**Expected result:**
```
📨 Received query from test-agent-001: 'Find me weather services'
🔍 Extracted keywords: ['weather', 'services']
📦 Found 2 services
📤 Sending response
```

---

## What Works Without AI

✅ **These work perfectly:**
- NATS messaging
- FastStream integration
- Catalogue API queries
- Message validation
- Service/intent discovery
- Structured responses

⏳ **This is limited:**
- Query understanding (just keyword matching)

---

## Getting AI Working Later

### Option A: OpenAI (When You Get API Key)

1. Add to `.env`:
```bash
OPENAI_API_KEY=sk-your-key-here
```

2. Switch to AI version:
```bash
python main_ai.py  # Uses AI automatically
```

### Option B: Ollama (Free Local AI)

1. Install Ollama:
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.2
ollama serve
```

2. Modify `agent.py` line 33:
```python
# Change from:
catalogue_agent = Agent('openai:gpt-4o-mini', ...)

# To:
catalogue_agent = Agent('ollama:llama3.2', ...)
```

3. Run AI version:
```bash
python main_ai.py  # Now uses local Ollama
```

---

## Questions to Ask Your Boss

### Option 1: Request OpenAI Access
"The AQS works best with OpenAI's GPT-4o-mini. Costs are minimal (~€5-10/month for testing). Do we have a company API key I can use?"

### Option 2: Request Ollama Permission
"Alternatively, I can use Ollama (free local AI). It requires ~8GB RAM but has no ongoing costs. Can I install it on my dev machine?"

### Option 3: Start with Keywords
"For now, I've implemented a keyword-based version that works without AI. Can I use this for the initial demo and add AI later?"

---

## Email Template for Your Boss

```
Subject: AQS Implementation - AI Provider Decision Needed

Hi [Boss],

The Agent Query Service is ready except for one decision: which AI approach to use.

**Current Status:**
I've built two versions:
1. Keyword-based version - works now, no dependencies
2. AI-powered version - needs API key or local setup

**Keyword Version Demo:**
I can demo this immediately. It works through NATS messaging and searches 
the catalogue, just with basic keyword matching instead of AI understanding.

**AI Version Options:**
- OpenAI GPT-4o-mini: ~€5-10/month, best quality
- Ollama (local): Free, requires 8GB RAM, decent quality

**My recommendation:**
Start with the keyword-based version for the initial demo. If we need better 
query understanding, we can add OpenAI or Ollama later.

**What I need from you:**
1. Approval to demo the keyword-based version, or
2. An OpenAI API key, or
3. Permission to install Ollama locally

Let me know which approach you prefer!

Thanks,
Rik
```

---

## Development Roadmap

### Phase 1: Now (No AI) ✅
- Build core AQS architecture
- NATS messaging integration
- Catalogue API integration
- Simple keyword-based search
- **Demo-ready!**

### Phase 2: Add AI (When Approved)
- Get API key or install Ollama
- Switch from `main_simple.py` to `main.py`
- Better query understanding
- Natural language responses

### Phase 3: Optimize (Future)
- Add caching
- Multi-turn conversations
- Query analytics
- Cost optimization

---

## Key Point

**The core AQS architecture is 100% complete.**

The only difference between versions is **how queries are interpreted:**

- **Simple**: Split query into keywords → search
- **AI**: Understand intent → choose best search strategy

Everything else (NATS, FastStream, catalogue integration, message schemas) is identical.

---

## Which File to Use Right Now?

```bash
# Start here (no dependencies):
python main_keyword.py

# Upgrade to this later (when you have AI):
python main_ai.py
```

**Bottom line:** You can build and test the entire system right now without any AI API key!
