# AQS: AI Options & Getting Started Without API Keys

**Current Situation:** The AQS can work in multiple modes depending on available resources.

---

## Quick Decision Guide

**Have OpenAI API key?**
→ Use `main_ai.py` (full AI mode)

**Want to test without API key?**
→ Use `main_keyword.py` (keyword matching)

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
python main_keyword.py
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


## Key Point

**The core AQS architecture is 100% complete.**

The only difference between versions is **how queries are interpreted:**

- **Simple**: Split query into keywords → search
- **AI**: Understand intent → choose best search strategy

Everything else (NATS, FastStream, catalogue integration, message schemas) is identical.