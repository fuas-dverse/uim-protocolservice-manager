<div align="center">
  <h1>DVerse UIM Catalogue Service</h1>
  <p><strong>A Level 2 UIM Implementation for Intelligent Service Discovery and Invocation</strong></p>
  <p>
    <em>Enabling AI agents to discover and use external REST APIs through standardized intent definitions</em>
  </p>
</div>

---

## What is UIM?

The **Unified Intent Mediator (UIM)** protocol is a standardized framework that enables AI agents to interact with web services through well-defined *intents*. Instead of hardcoding API integrations, UIM allows agents to dynamically discover services and understand how to use them through metadata.

An **intent** defines a specific action or goal (e.g., "search papers", "get weather") by describing *what* should happen rather than *how*. This creates a clean abstraction layer between agents and the diverse world of REST APIs.

### The Problem UIM Solves

Traditional API integrations require developers to:
- Write custom code for each API
- Handle different authentication methods manually
- Parse various response formats
- Update code when APIs change

UIM provides a **translation layer** where services register their capabilities as intents with standardized metadata. Agents query a catalogue, discover relevant services, and invoke them dynamically - no hardcoded integrations required.

### Level 2 Implementation

This project implements a **Level 2 UIM system**, meaning it provides UIM benefits (intelligent discovery, metadata-driven invocation, scalability) while working with **existing non-UIM-compliant REST APIs**. The catalogue acts as a bridge between natural language queries and traditional REST endpoints.

---

## System Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                         DVerse Platform                              │
│                                                                      │
│  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐ │
│  │   Chatbot       │     │   Catalogue     │     │   External      │ │
│  │   Frontend      │────▶│   API           │────▶│   APIs          │ │
│  │   (SolidJS)     │     │   (FastAPI)     │     │   (REST)        │ │
│  └─────────────────┘     └────────┬────────┘     └─────────────────┘ │
│                                   │                                  │
│                          ┌────────▼────────┐                         │
│                          │    MongoDB      │                         │
│                          │    Catalogue    │                         │
│                          └─────────────────┘                         │
│                                                                      │
│  ┌─────────────────┐     ┌─────────────────┐                         │
│  │   Discovery     │     │   Service       │                         │
│  │   Agent         │────▶│   Invoker       │                         │
│  │   (Pydantic AI) │     │   (Template)    │                         │
│  └─────────────────┘     └─────────────────┘                         │
└──────────────────────────────────────────────────────────────────────┘
```

### Request Flow

1. **User Query** → User asks a natural language question (e.g., "Find papers about transformers")
2. **Discovery** → LLM-powered agent searches the catalogue for matching services
3. **Selection** → Best-matching service and intent are selected based on semantic similarity
4. **Invocation** → Generic service invoker builds and executes the HTTP request using metadata
5. **Formatting** → Template-based formatter structures the response for readability
6. **Response** → User receives formatted results

---

## Components

### Backend API (`implementations/uimServicemanager/API/`)

A FastAPI application providing REST endpoints for the UIM catalogue.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/services` | GET/POST | List or register services |
| `/intents` | GET/POST | List or register intents |
| `/query` | POST | Natural language catalogue queries (keyword mode) |
| `/discover` | POST | LLM-based service discovery |
| `/health` | GET | Service health status |
| `/docs` | GET | Swagger API documentation |

**Architecture:**
- **Presentation Layer**: Controllers handle HTTP requests and response formatting
- **Logic Layer**: Business logic for service discovery and query processing
- **Data Access Layer (DAL)**: MongoDB operations with Pydantic models

### Chatbot Service (`implementations/uim-chatbot/`)

An AI-powered conversational interface that discovers and invokes services.

**Key Components:**
- **Discovery Agent** (`agent.py`): Uses Pydantic AI with Ollama (llama3.2) for service selection
- **Generic Service Invoker** (`service_invoker.py`): Metadata-driven HTTP request construction
- **Fast System** (`fast_system.py`): Template-based response formatting (replaced LLM formatting due to 40% failure rate)

**Endpoints:**
- `POST /chat/discover` - Returns which service will handle the query
- `POST /chat/invoke` - Executes the service call and returns results
- `GET /` - Service health check

### Frontends

**Catalogue Browser** (`implementations/uimServicemanager/Client-Interface/`)
- SolidJS web application
- Browse registered services and intents
- Visual interface for the catalogue

**Chatbot Interface** (`implementations/uim-chatbot/Client-interface/`)
- SolidJS chat application
- Natural language interaction with the system
- Real-time service discovery and invocation feedback

### Integrated External APIs

The catalogue is pre-seeded with these services:

| Service | Description | Auth Type |
|---------|-------------|-----------|
| **arXiv API** | Academic paper search | None |
| **OpenWeather** | Current weather and forecasts | API Key |
| **News API** | News article search | API Key |
| **GitHub API** | Repository and user data | Bearer Token |
| **Spotify API** | Music search and metadata | Bearer Token |
| **OpenAI API** | Text generation and analysis | Bearer Token |

---

## Technology Stack

| Component | Technology |
|-----------|------------|
| Backend Framework | FastAPI |
| Database | MongoDB |
| Frontend Framework | SolidJS |
| LLM Integration | Pydantic AI + Ollama (llama3.2) |
| Messaging | NATS.io (optional) |
| Data Validation | Pydantic |
| HTTP Client | httpx |
| Containerization | Docker |

---

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- Docker Desktop
- MongoDB (via Docker or local installation)
- Ollama with llama3.2 model (for AI features)

### Installation

**1. Clone the repository:**
```bash
git clone https://github.com/[repository]/dverse-uim.git
cd dverse-uim
```

**2. Start MongoDB:**
```bash
docker run -d --name mongodb -p 27017:27017 mongo:latest
```

**3. Start NATS (optional, for messaging features):**
```bash
docker run -d --name nats-server -p 4222:4222 -p 8222:8222 nats:latest
```

**4. Install Ollama and pull the model:**
```bash
# Install Ollama from https://ollama.ai
ollama pull llama3.2
```

**5. Set up the Backend API:**
```bash
cd implementations/uimServicemanager/API
pip install -r requirements.txt --break-system-packages
cd ..
python StartupService.py
```

**6. Seed the database (first run):**
The startup script automatically seeds the database with demo services if empty.

**7. Start the Chatbot Service:**
```bash
cd implementations/uim-chatbot
pip install -r requirements.txt --break-system-packages
python main.py
```

**8. Start the Frontends:**

Catalogue Browser:
```bash
cd implementations/uimServicemanager/Client-Interface
npm install
npm run dev
```

Chatbot Interface:
```bash
cd implementations/uim-chatbot/Client-interface
npm install
npm run dev
```

### Ports Overview

| Service | Port | URL |
|---------|------|-----|
| Backend API | 8000 | http://localhost:8000 |
| Chatbot Service | 8001 | http://localhost:8001 |
| Catalogue Frontend | 3000 | http://localhost:3000 |
| Chatbot Frontend | 3001 | http://localhost:3001 |
| MongoDB | 27017 | mongodb://localhost:27017 |
| NATS | 4222 | nats://localhost:4222 |
| NATS Monitor | 8222 | http://localhost:8222 |

### Quick Test

```bash
# Test Backend API
curl http://localhost:8000/health

# Test query endpoint
curl -X POST http://localhost:8000/query/ \
  -H "Content-Type: application/json" \
  -d '{"query": "Find weather services", "use_ai": false}'

# View API documentation
open http://localhost:8000/docs
```

---

## Usage Examples

### Using the Chatbot

Try these queries in the chatbot interface:

- "Find papers about neural networks"
- "What's the weather in London?"
- "Search for news about AI"
- "Find repositories about machine learning"

### Using the API Directly

**List all services:**
```bash
curl http://localhost:8000/services
```

**Query the catalogue:**
```bash
curl -X POST http://localhost:8000/query/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "weather forecast",
    "agent_id": "my-agent",
    "use_ai": false
  }'
```

**Register a new service:**
```bash
curl -X POST http://localhost:8000/services \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Service",
    "description": "A custom service",
    "service_url": "https://api.example.com/v1",
    "auth_type": "api_key"
  }'
```

---

## Testing

The project includes comprehensive test suites covering all components.

### Run All Tests

```bash
cd implementations/uim-chatbot/Tests
python run_all_tests.py
```

### Test Suites

| Suite | Description | Tests |
|-------|-------------|-------|
| API Endpoint Tests | Backend REST endpoints | 7 |
| Service Invoker | Metadata-driven invocation | 3 |
| End-to-End | Complete workflow | 5 |
| Chatbot HTTP | Chat interface | 5 |
| Discovery LLM | Service selection | 5 |
| Safety | Input validation, error handling | 3 |
| Reliability | Stability, recovery | 4 |

**Total: 32 tests**

### Quick Test (Core Only)

```bash
python run_all_tests.py --quick
```

### Skip LLM Tests

```bash
python run_all_tests.py --skip-llm
```

---

## Architecture Decisions

Key technical decisions are documented as Architecture Decision Records (ADRs):

| ADR | Decision | Rationale |
|-----|----------|-----------|
| Database | MongoDB | Schema flexibility, JSON-native, Python integration |
| Backend Framework | FastAPI | Async support, type validation, auto-documentation |
| Frontend Framework | SolidJS | Fine-grained reactivity, small bundle size, JSX syntax |
| LLM Framework | Pydantic AI | Native Pydantic integration, tool calling support |
| LLM Model | llama3.2 (Ollama) | Local inference, no API costs, reliable tool calling |
| Data Validation | Pydantic | Type enforcement, FastAPI integration |
| Service Merge | Unified API | Eliminated HTTP overhead, simplified deployment |
| Response Formatting | Templates | 100% reliability vs 60% with LLM formatting |

Full ADR documents available in `implementations/uimServicemanager/Docs/ADRS/`

---

## Repository Structure

```
dverse-uim/
├── implementations/
│   ├── uimServicemanager/           # Backend API & Catalogue
│   │   ├── API/
│   │   │   ├── Presentation/        # Controllers & ViewModels
│   │   │   ├── logicLayer/          # Business logic
│   │   │   ├── DAL/                 # Data access layer
│   │   │   │   ├── seed_data.json   # Pre-configured services
│   │   │   │   └── seed_database.py # Database seeding script
│   │   │   ├── main.py              # FastAPI application
│   │   │   └── ARCHITECTURE.md      # System architecture docs
│   │   ├── Client-Interface/        # Catalogue browser (SolidJS)
│   │   │   ├── src/
│   │   │   │   ├── App.jsx          # Main application component
│   │   │   │   └── index.jsx        # Entry point
│   │   │   ├── package.json
│   │   │   └── vite.config.js
│   │   ├── Docs/
│   │   │   ├── ADRS/                # Architecture Decision Records
│   │   │   └── Tests Report.md      # Test documentation
│   │   ├── StartupService.py        # Backend startup script
│   │   └── test_API.py              # API test suite
│   │
│   └── uim-chatbot/                 # Chatbot service
│       ├── main.py                  # FastAPI chatbot server
│       ├── agent.py                 # Pydantic AI discovery agent
│       ├── service_invoker.py       # Generic HTTP invoker
│       ├── fast_system.py           # Template-based formatting
│       ├── models.py                # Pydantic data models
│       ├── Client-interface/        # Chat UI (SolidJS)
│       │   ├── src/
│       │   │   ├── App.jsx          # Chat component
│       │   │   └── index.jsx        # Entry point
│       │   └── package.json
│       └── Tests/                   # Comprehensive test suites
│           ├── run_all_tests.py     # Test runner
│           ├── test_service_invoker.py
│           ├── test_e2e.py
│           ├── test_chatbot.py
│           ├── test_discovery_llm.py
│           ├── test_safety.py
│           └── test_reliability.py
│
├── uim-docs/                        # UIM protocol documentation
└── README.md                        # This file
```

---

## Configuration

### Environment Variables

```bash
# API Keys for external services (optional)
OPENWEATHER_API_KEY=your_key_here
NEWS_API_KEY=your_key_here
GITHUB_TOKEN=your_token_here
SPOTIFY_CLIENT_ID=your_id_here
SPOTIFY_CLIENT_SECRET=your_secret_here

# MongoDB connection
MONGODB_URI=mongodb://localhost:27017

# Ollama configuration
OLLAMA_HOST=http://localhost:11434
```

### Database Seeding

The catalogue is automatically seeded with demo services on first startup. To re-seed:

```bash
cd implementations/uimServicemanager/API
python -c "from DAL.seed_data import seed_database; seed_database()"
```

---

## Research Context

This project was developed as part of the **DVerse Research Program** at Fontys ICT, exploring how the UIM protocol can enable intelligent agent-service communication in distributed systems.

**Key Research Questions:**
1. How can UIM enhance agent-service communication within the DVerse platform?
2. What are the strengths and limitations of UIM compared to traditional API integration?
3. How can conversational interfaces improve service discovery?

**Key Findings:**
- Template-based formatting significantly outperforms LLM-based approaches for reliability
- Level 2 UIM implementations can bridge the gap between the protocol's vision and real-world API diversity
- Metadata-driven invocation eliminates the need for hardcoded API integrations

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- **DVerse Research Program** - Fontys ICT
- **UIM Protocol** - SynaptiAI
- **Ollama** - Local LLM inference
- **Pydantic AI** - Agent framework