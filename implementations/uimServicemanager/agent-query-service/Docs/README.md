# Agent Query Service (AQS)

A conversational interface for the UIM Catalogue, allowing AI agents to discover services and intents using natural language queries via NATS messaging.

## Architecture

```
Agent → NATS (uim.catalogue.query) → AQS → Pydantic AI → Catalogue API
                                      ↓
Agent ← NATS (uim.catalogue.response) ←
```

## Features

- **Natural Language Queries**: Agents can ask questions like "Find me weather services" instead of crafting structured API queries
- **NATS-Based Messaging**: Fully integrated with DVerse platform's messaging infrastructure
- **Pydantic AI**: Uses Pydantic AI framework for reliable, type-safe LLM interactions
- **Tool-Based Discovery**: AI agent uses tools to search services and intents in the catalogue
- **Structured Responses**: Returns well-defined Pydantic models with service and intent information

## Prerequisites

- Python 3.10+
- NATS server running (via Docker or locally)
- UIM Catalogue API running (FastAPI backend)
- OpenAI API key (or alternative LLM provider)

## Installation

1. **Install dependencies:**

```bash
pip install -r requirements.txt --break-system-packages
```

2. **Configure environment:**

```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

3. **Verify NATS is running:**

```bash
# If using Docker:
docker run -p 4222:4222 -p 8222:8222 nats:latest

# Check health:
curl http://localhost:8222/healthz
```

4. **Verify Catalogue API is running:**

```bash
curl http://localhost:8000/health
```

## Usage

### Running the Service

```bash
## 🚀 Quick Start

### Option 1: Keyword-Based (Start Here!)

```bash
# No setup needed - just run!
python main_keyword.py

# Test it
python test_agent.py
```

### Option 2: AI-Powered

```bash
# Setup: Add API key to .env
cp .env.example .env
# Edit .env and add: OPENAI_API_KEY=sk-...

# Run
python main_ai.py

# Test it
python test_agent.py
```
```

The service will:
- Connect to NATS at `nats://localhost:4222`
- Subscribe to `uim.catalogue.query` topic
- Publish responses to `uim.catalogue.response` topic

### Testing with a Mock Agent

You can test the AQS by publishing messages to NATS. Here's an example using Python:

```python
import asyncio
import json
from nats.aio.client import Client as NATS
from datetime import datetime

async def test_query():
    nc = NATS()
    await nc.connect("nats://localhost:4222")
    
    # Create query message
    query = {
        "agent_id": "test-agent-001",
        "message": "Find me weather services with forecasting capability",
        "context": {"location": "Europe"},
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Publish query
    await nc.publish(
        "uim.catalogue.query",
        json.dumps(query).encode()
    )
    
    # Subscribe to response
    async def message_handler(msg):
        data = json.loads(msg.data.decode())
        print(f"Response: {json.dumps(data, indent=2)}")
    
    await nc.subscribe("uim.catalogue.response", cb=message_handler)
    
    # Wait for response
    await asyncio.sleep(5)
    await nc.close()

asyncio.run(test_query())
```

### Message Format

**Query Message** (published to `uim.catalogue.query`):
```json
{
  "agent_id": "agent-123",
  "message": "Find me weather services",
  "context": {
    "location": "Europe",
    "previous_services": ["openweather"]
  },
  "timestamp": "2025-12-02T10:30:00Z"
}
```

**Response Message** (received from `uim.catalogue.response`):
```json
{
  "agent_id": "agent-123",
  "query": "Find me weather services",
  "response": "I found 2 weather services with forecasting capabilities...",
  "services_found": [
    {
      "id": "service-123",
      "name": "OpenWeather API",
      "description": "Global weather data service",
      "base_url": "https://api.openweathermap.org",
      "metadata": {}
    }
  ],
  "intents_found": [
    {
      "id": "intent-456",
      "name": "get_forecast",
      "description": "Get weather forecast for a location",
      "service_id": "service-123",
      "parameters": {
        "location": {"type": "string", "required": true},
        "days": {"type": "integer", "default": 5}
      }
    }
  ],
  "success": true,
  "error": null,
  "timestamp": "2025-12-02T10:30:01Z"
}
```

## Project Structure

```
agent-query-service/
├── main.py                 # FastStream app with NATS handlers
├── agent.py                # Pydantic AI agent configuration
├── catalogue_client.py     # HTTP client for Catalogue API
├── models.py               # Pydantic models for messages
├── requirements.txt        # Python dependencies
├── .env.example           # Environment configuration template
└── README.md              # This file
```

## Configuration

### Environment Variables

- `NATS_URL`: NATS server URL (default: `nats://localhost:4222`)
- `CATALOGUE_URL`: UIM Catalogue API URL (default: `http://localhost:8000`)
- `OPENAI_API_KEY`: OpenAI API key for Pydantic AI
- `LOG_LEVEL`: Logging level (default: `INFO`)

### Customizing the Agent

The Pydantic AI agent is configured in `agent.py`. You can:

1. **Change the model:**
   ```python
   catalogue_agent = Agent('openai:gpt-4o')  # More capable model
   ```

2. **Add custom tools:**
   ```python
   @catalogue_agent.tool
   async def my_custom_tool(ctx: RunContext[AgentDependencies]) -> Any:
       # Your logic here
       pass
   ```

3. **Modify system prompt:**
   Edit the `system_prompt` parameter in `agent.py`

## Health Check

The AQS provides a health check endpoint via NATS:

```python
# Publish to health check topic
await nc.publish("uim.aqs.health", b'{}')

# Response on "uim.aqs.health.response":
{
  "status": "healthy",
  "service": "agent-query-service",
  "catalogue_connected": true,
  "nats_connected": true
}
```

## Development
### Debugging

Enable debug logging:

```bash
export LOG_LEVEL=DEBUG
python main.py
```
## Troubleshooting

### AQS won't start

- Check NATS is running: `curl http://localhost:8222/healthz`
- Check Catalogue API is running: `curl http://localhost:8000/health`
- Verify environment variables in `.env`

### No response from queries

- Check logs for errors
- Verify AI API key is valid
- Check NATS topics are correct
- Ensure Catalogue API has seeded data

### High latency

- Check network latency to AI API
- Monitor Catalogue API response times


## License

Part of the DVerse project - Fontys University
