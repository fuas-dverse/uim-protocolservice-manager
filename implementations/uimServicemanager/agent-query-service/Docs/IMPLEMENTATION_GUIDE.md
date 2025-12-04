# AQS Build Guide

### 1. `models.py` - Message Schemas
**What:** Defines the structure of messages agents send/receive
**Why:** Type-safe communication between agents and AQS

```python
class QueryMessage(BaseModel):
    agent_id: str      # Who's asking
    message: str       # "Find weather services"
    context: Dict      # Optional context
    timestamp: datetime

class ResponseMessage(BaseModel):
    agent_id: str
    response: str      # Natural language answer
    services_found: List[ServiceInfo]
    intents_found: List[IntentInfo]
    success: bool
```

**Key decision:** Used Pydantic because:
- Automatic validation (wrong types = error immediately)
- JSON serialization built-in
- Self-documenting (model = schema)

---

### 2. `catalogue_client.py` - HTTP Client
**What:** Talks to the FastAPI backend to search services/intents
**Why:** AI agent needs a way to query the catalogue

```python
class CatalogueClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.AsyncClient()
    
    async def search_services(self, query: str):
        response = await self.client.get(
            f"{self.base_url}/services",
            params={"search": query}
        )
        return response.json()
    
    # + get_service_by_id()
    # + get_service_intents()
    # + search_intents()
```

**Key decision:** Used `httpx` (not `requests`) because:
- Async support (non-blocking)
- Works with FastAPI's async patterns

---

### 3. `agent.py` - Pydantic AI Agent
**What:** The "brain" - interprets natural language and calls the right functions
**Why:** Converts "Find weather services" into actual API calls

```python
# Define what the agent needs access to
@dataclass
class AgentDependencies:
    catalogue_client: CatalogueClient
    agent_id: str
    query_context: Dict

# Create the AI agent
catalogue_agent = Agent(
    'openai:gpt-4o-mini',  # AI model
    deps_type=AgentDependencies,
    system_prompt="You help agents discover services..."
)

# Give the agent tools it can use
@catalogue_agent.tool
async def search_services(ctx, query: str) -> List[Dict]:
    """Search for services in the catalogue"""
    client = ctx.deps.catalogue_client
    return await client.search_services(query)

# Similar tools for:
# - get_service_intents()
# - search_intents()
# - get_service_details()
```

**How it works:**
1. Agent receives: "Find weather services"
2. Agent thinks: "I should use the search_services tool"
3. Agent calls: `search_services(query="weather")`
4. Tool queries your API
5. Agent formats response: "I found 2 weather services..."

**Key decision:** Tools = functions the AI can call
- Without tools: AI only generates text
- With tools: AI can actually do things (query APIs, etc.)

---

### 4. `main.py` - FastStream Service
**What:** Connects NATS messaging with the AI agent
**Why:** Receives messages from agents, processes them, sends responses back

```python
from faststream import FastStream
from faststream.nats import NatsBroker

# Connect to NATS
broker = NatsBroker("nats://localhost:4222")
app = FastStream(broker)

# Initialize on startup
@app.on_startup
async def on_startup():
    global catalogue_client
    catalogue_client = CatalogueClient("http://localhost:8000")

# Handle incoming queries
@broker.subscriber("uim.catalogue.query")    # Listen here
@broker.publisher("uim.catalogue.response")  # Reply here
async def handle_agent_query(msg: QueryMessage) -> ResponseMessage:
    try:
        # Create dependencies
        deps = AgentDependencies(
            catalogue_client=catalogue_client,
            agent_id=msg.agent_id,
            query_context=msg.context
        )
        
        # Run AI agent
        result = await catalogue_agent.run(msg.message, deps=deps)
        
        # Return structured response
        return ResponseMessage(
            agent_id=msg.agent_id,
            response=result.data.summary,
            services_found=result.data.services,
            intents_found=result.data.intents,
            success=True
        )
    except Exception as e:
        # Never crash - always respond
        return ResponseMessage(
            agent_id=msg.agent_id,
            response=f"Error: {str(e)}",
            success=False
        )
```

**Key decision:** FastStream decorators handle all the plumbing:
- Subscribes to NATS topic
- Deserializes JSON to `QueryMessage`
- Validates with Pydantic
- Serializes response back to JSON
- Publishes to response topic

**Without FastStream** you'd manually do all of that.

---

### 5. `test_agent.py` - Test Script
**What:** Simulates an agent sending a query
**Why:** Test the system without building a real agent

```python
async def test_agent_query():
    nc = NATS()
    await nc.connect("nats://localhost:4222")
    
    # Create query
    query = {
        "agent_id": "test-agent-001",
        "message": "Find me weather services",
        "context": {},
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Subscribe to response first
    async def response_handler(msg):
        data = json.loads(msg.data.decode())
        print(json.dumps(data, indent=2))
    
    await nc.subscribe("uim.catalogue.response", cb=response_handler)
    
    # Publish query
    await nc.publish("uim.catalogue.query", json.dumps(query).encode())
    
    # Wait for response
    await asyncio.sleep(5)
```



## The Flow in Simple Terms

```
1. Test agent publishes to NATS:
   Topic: "uim.catalogue.query"
   Message: {"agent_id": "test", "message": "Find weather services"}

2. FastStream receives message:
   - Deserializes to QueryMessage
   - Validates with Pydantic
   - Calls handle_agent_query()

3. Handler runs AI agent:
   - Creates dependencies (client, context)
   - Calls: catalogue_agent.run("Find weather services")

4. AI agent processes:
   - Reads query: "Find weather services"
   - Decides: "I should use search_services tool"
   - Calls: search_services(query="weather")

5. Tool executes:
   - Uses catalogue_client
   - Makes HTTP request: GET /services?search=weather
   - Returns: [{"id": "123", "name": "OpenWeather", ...}]

6. AI agent formats result:
   - "I found 2 weather services with forecasting..."
   - Structures data into CatalogueQueryResult

7. Handler builds response:
   - Creates ResponseMessage
   - Includes services_found, intents_found

8. FastStream publishes response:
   - Serializes ResponseMessage to JSON
   - Publishes to "uim.catalogue.response"

9. Test agent receives response:
   - Prints structured result
```

---

## Key Technologies & Why

| Technology | Purpose | Why This Choice |
|------------|---------|-----------------|
| **Pydantic** | Validation | Type-safe, self-documenting, used throughout your project |
| **FastStream** | NATS messaging | FastAPI-like decorators, less boilerplate than raw NATS |
| **Pydantic AI** | AI framework | Built by Pydantic team, type-safe, lightweight |
| **httpx** | HTTP client | Async support (works with FastAPI patterns) |
| **NATS** | Message broker | DVerse platform standard, async messaging |

---

## How to Replicate This Pattern

**Use this pattern when you have:**
- Multiple services/agents communicating
- Need for async messaging (not HTTP requests)
- Natural language interface requirements
- Existing APIs to integrate with

**Recipe:**
1. Define message schemas (what goes in/out)
2. Build API client (how to talk to your backend)
3. Create AI agent with tools (what can the AI do)
4. Wire up messaging (connect NATS to agent)
5. Test end-to-end (validate it works)

**Example: Task Assignment System**
```python
# 1. Messages
class TaskRequest(BaseModel):
    agent_id: str
    message: str  # "Assign me a data processing task"

# 2. Client
class TaskAPI:
    async def get_available_tasks(self): ...

# 3. Agent tools
@agent.tool
async def search_tasks(ctx): ...

# 4. Handler
@broker.subscriber("tasks.request")
async def handle_task_request(msg: TaskRequest): ...
```

---

## What Each File Actually Does

```
models.py
├─ Defines QueryMessage (what agents send)
├─ Defines ResponseMessage (what agents receive)
└─ Defines ServiceInfo, IntentInfo (data structures)

catalogue_client.py
├─ Wraps your FastAPI backend
├─ search_services() → GET /services
├─ get_service_intents() → GET /services/{id}/intents
└─ Error handling, logging

agent.py
├─ Creates Pydantic AI agent
├─ Defines tools (functions AI can call):
│  ├─ search_services()
│  ├─ get_service_intents()
│  ├─ search_intents()
│  └─ get_service_details()
└─ System prompt (tells AI what to do)

main.py
├─ FastStream app setup
├─ NATS broker connection
├─ Startup: initialize catalogue_client
├─ Handler: process queries with AI
└─ Publish responses back to agents

test_agent.py
├─ Simulates an agent
├─ Publishes query to NATS
└─ Prints response
```

---

## Common Customizations

### Change AI Model
In `agent.py`:
```python
catalogue_agent = Agent(
    'openai:gpt-4o',  # More capable (but expensive)
    # or
    'anthropic:claude-3-5-sonnet-20241022',  # Alternative
)
```

### Add New Tool
In `agent.py`:
```python
@catalogue_agent.tool
async def my_new_capability(ctx, param: str) -> Any:
    """What this tool does - AI reads this description"""
    client = ctx.deps.catalogue_client
    # Your logic
    return result
```

### Change NATS Topics
In `main.py`:
```python
@broker.subscriber("my.custom.topic")  # Input topic
@broker.publisher("my.response.topic")  # Output topic
async def handle_agent_query(msg: QueryMessage):
    ...
```

### Adjust System Prompt
In `agent.py`:
```python
catalogue_agent = Agent(
    'openai:gpt-4o-mini',
    system_prompt="""Your custom instructions here.
    Tell the AI what to do, when to use tools, etc."""
)
```
---

## Troubleshooting Quick Reference

| Issue | Solution |
|-------|----------|
| "Failed to connect to NATS" | Start NATS: `docker run -p 4222:4222 nats:latest` |
| "OPENAI_API_KEY not set" | Create `.env` file with your API key |
| "Catalogue API health check failed" | Start your FastAPI backend on port 8000 |
| "No response from test" | Check all 3 services running (NATS, Backend, AQS) |
