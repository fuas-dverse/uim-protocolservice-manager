# Agent Query Service - Two Versions

The AQS comes in **two versions** that you can choose based on your needs:

---

## 🔑 Version 1: Keyword-Based (`main_keyword.py`)

**Use when:**
- You don't have an AI API key
- You want zero external dependencies
- You need fast, predictable responses
- You're in development/testing mode

**How it works:**
1. Extracts keywords from the query
2. Searches catalogue with those keywords
3. Returns matching services/intents

**Example:**
```
Query: "Find me weather services with forecasting"
→ Keywords: ["weather", "services", "forecasting"]
→ Searches catalogue for these terms
→ Returns: Weather services found
```

**Requirements:**
- ✅ None! Works immediately
- ✅ No API keys
- ✅ No AI setup

**Run it:**
```bash
python main_keyword.py
```

---

## 🤖 Version 2: AI-Powered (`main_ai.py`)

**Use when:**
- You have an OpenAI API key (or Ollama setup)
- You need natural language understanding
- You want context-aware responses
- Complex queries are important

**How it works:**
1. AI understands the query intent
2. AI decides which tools to call
3. AI formats a natural response
4. Returns structured results

**Example:**
```
Query: "Find me weather services with forecasting"
→ AI understands: User wants weather services with forecast capability
→ AI calls: search_services("weather") + get_service_intents()
→ AI responds: "I found 2 weather services with forecasting capabilities..."
→ Returns: Structured ServiceInfo and IntentInfo
```

**Requirements:**
- ⚠️ OpenAI API key in `.env`, OR
- ⚠️ Ollama running locally

**Run it:**
```bash
python main_ai.py
```

---



## 🎯 Which Should You Use?

### Start with Keyword-Based if:
- ✅ You're just testing the architecture
- ✅ You don't have AI access yet
- ✅ Your queries are simple (1-3 words)
- ✅ You want zero setup time

### Upgrade to AI-Powered when:
- ✅ You get an API key or install Ollama
- ✅ Your agents send complex queries
- ✅ You need better query understanding
- ✅ You want natural language responses

---

## 🔄 Switching Between Versions

**The architecture is identical** - only the query processing differs.

```bash
# Use keyword version
python main_keyword.py

# Stop it (Ctrl+C)

# Use AI version (once you have a key)
python main_ai.py
```

**Everything else stays the same:**
- ✅ Same NATS topics
- ✅ Same message formats
- ✅ Same catalogue integration
- ✅ Same test scripts
- ✅ Same deployment approach

---

## 🔧 Customization

### Keyword Version
Edit `main_keyword.py` → `extract_keywords()` function:
```python
def extract_keywords(text: str) -> list[str]:
    # Add your custom logic here
    # Example: add domain-specific stop words
    # Example: handle synonyms
```

### AI Version
Edit `agent.py` → system prompt or tools:
```python
# Change the AI model
catalogue_agent = Agent('openai:gpt-4o', ...)  # More capable

# Or use Ollama
catalogue_agent = Agent('ollama:llama3.2', ...)  # Free local
```

---

## ❓ FAQ

**Q: Can I run both at the same time?**
A: No, they both use the same NATS topics. Pick one.

**Q: What if OpenAI changes their API?**
A: Pydantic AI abstracts the provider - just change the model string.

**Q: Can I switch back and forth?**
A: Yes! They're completely interchangeable. Same interface, different internals.

**Q: Does the test script work with both?**
A: Yes! `test_agent.py` works identically with both versions.
