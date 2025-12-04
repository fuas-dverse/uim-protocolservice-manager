# Architecture Diagram - Merged System

## Before Merge
```
┌─────────────────────────────┐        ┌─────────────────────────────┐
│   Agent Query Service       │        │         API API         │
│                             │        │                             │
│  ┌────────────────────┐     │        │  ┌────────────────────┐     │
│  │  NATS Subscriber   │     │        │  │   REST Endpoints   │     │
│  │  uim.catalogue.*   │     │  HTTP  │  │   /services        │     │
│  └─────────┬──────────┘     │───────▶│  │   /intents         │     │
│            │                │        │  │   /uimprotocol     │     │
│  ┌─────────▼──────────┐     │        │  └─────────┬──────────┘     │
│  │  Pydantic AI       │     │        │            │                │
│  │  Keyword/AI Query  │     │        │  ┌─────────▼──────────┐     │
│  └────────────────────┘     │        │  │  Service Logic     │     │
│                             │        │  │  Intent Logic      │     │
└─────────────────────────────┘        │  └─────────┬──────────┘     │
                                       │            │                │
                                       │  ┌─────────▼──────────┐     │
                                       │  │    MongoDB DAL     │     │
                                       │  └────────────────────┘     │
                                       └─────────────────────────────┘
```

## After Merge
```
┌──────────────────────────────────────────────────────────────────────┐
│                    Unified API API                                │
│                                                                        │
│  ┌─────────────────────────┐       ┌─────────────────────────┐      │
│  │   NATS Integration      │       │   REST API Endpoints    │      │
│  │   (Optional)            │       │                         │      │
│  │                         │       │  GET/POST /services     │      │
│  │  Subscribe:             │       │  GET/POST /intents      │      │
│  │  uim.catalogue.query    │       │  GET/POST /uimprotocol  │      │
│  │                         │       │  POST /query ◄────NEW   │      │
│  │  Publish:               │       │  GET /health            │      │
│  │  uim.catalogue.response │       │  GET /                  │      │
│  └────────────┬────────────┘       └──────────┬──────────────┘      │
│               │                               │                      │
│               │    ┌──────────────────────────▼─────────────┐       │
│               └───▶│       Query Controller                 │       │
│                    │  (handles both HTTP & NATS queries)    │       │
│                    └──────────────────┬─────────────────────┘       │
│                                       │                              │
│                    ┌──────────────────▼─────────────────────┐       │
│                    │        Query Logic Layer               │       │
│                    │                                         │       │
│                    │  ┌────────────────┐ ┌───────────────┐ │       │
│                    │  │ Keyword Mode   │ │   AI Mode     │ │       │
│                    │  │ (Default)      │ │  (Optional)   │ │       │
│                    │  └────────────────┘ └───────────────┘ │       │
│                    └──────────────────┬─────────────────────┘       │
│                                       │                              │
│  ┌──────────────────┬─────────────────▼────────────────┬──────────┐│
│  │ Service Logic    │  Intent Logic   │  Protocol Logic │          ││
│  └──────────────────┴─────────────────┴─────────────────┘          ││
│                                       │                              │
│  ┌────────────────────────────────────▼──────────────────────────┐ │
│  │                        DAL Layer                               │ │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐  │ │
│  │  │ Service DAL  │ │ Intent DAL   │ │ UIM Protocol DAL     │  │ │
│  │  └──────────────┘ └──────────────┘ └──────────────────────┘  │ │
│  └─────────────────────────────────┬───────────────────────────┘  │
│                                     │                               │
│                        ┌────────────▼──────────────┐                │
│                        │       MongoDB             │                │
│                        │  ┌────────┐  ┌────────┐  │                │
│                        │  │Services│  │Intents │  │                │
│                        │  └────────┘  └────────┘  │                │
│                        └───────────────────────────┘                │
└────────────────────────────────────────────────────────────────────┘
```

## Request Flow Examples

### HTTP Query Request Flow
```
1. HTTP Client
   │
   ▼
2. POST /query {"query": "Find weather services"}
   │
   ▼
3. queryController (Presentation Layer)
   │
   ▼
4. queryLogic.process_query() (Logic Layer)
   │
   ├─ Extract keywords: ["weather", "services"]
   │
   ▼
5. serviceDAL.getServicesByName("weather services") (DAL)
   │
   ▼
6. MongoDB query: services.find({name: {$regex: /weather/i}})
   │
   ▼
7. Return services with populated intents
   │
   ▼
8. queryLogic formats response
   │
   ▼
9. QueryResponse returned to client
```

### NATS Message Flow (Optional)
```
1. External Agent
   │
   ▼
2. Publish to: uim.catalogue.query
   NATS Message: {
     "agent_id": "weather-agent",
     "message": "Find weather services"
   }
   │
   ▼
3. NATS Broker forwards to API
   │
   ▼
4. queryLogic.process_query() (same as HTTP)
   │
   ▼
5. Response built
   │
   ▼
6. Publish to: uim.catalogue.response
   NATS Message: {
     "agent_id": "weather-agent",
     "services_found": [...],
     "response": "Found 2 services..."
   }
   │
   ▼
7. External Agent receives response
```

## File Structure After Merge

```
UIMservicemanager/
├── StartupService.py ◄────────────── NEW (moved from API/)
├── API/
│   ├── main.py ◄─────────────────── MODIFIED (added NATS lifespan)
│   ├── requirements.txt ◄──────────── MODIFIED (new dependencies)
│   │
│   ├── Presentation/
│   │   ├── Controller/
│   │   │   ├── servicesController.py
│   │   │   ├── intentsController.py
│   │   │   ├── uimProtocolController.py
│   │   │   └── queryController.py ◄──── NEW
│   │   │
│   │   └── Viewmodel/
│   │       ├── serviceViewmodel.py
│   │       ├── intentViewmodel.py
│   │       ├── uimProtocolViewmodel.py
│   │       └── queryViewmodel.py ◄──── NEW
│   │
│   ├── logicLayer/
│   │   ├── Logic/
│   │   │   ├── serviceLogic.py
│   │   │   ├── intentLogic.py
│   │   │   ├── uimProtocolLogic.py
│   │   │   └── queryLogic.py ◄──── NEW
│   │   │
│   │   └── Interface/
│   │       ├── IserviceDAL.py
│   │       └── IintentDAL.py
│   │
│   └── DAL/
│       ├── serviceDAL.py
│       ├── intentDAL.py
│       └── uimprotocolDAL.py
│
├── Demo-Frontend/  (unchanged)
│
└── agent-query-service/ ◄──── DELETE THIS FOLDER (no longer needed)
```

## Dependency Graph

```
┌─────────────────┐
│  FastAPI App    │
│   (main.py)     │
└────────┬────────┘
         │
         ├──────────────────────────────┐
         │                              │
         ▼                              ▼
┌────────────────┐            ┌─────────────────┐
│  Controllers   │            │  NATS Broker    │
│  (Presentation)│            │  (FastStream)   │
└────────┬───────┘            └─────────────────┘
         │
         ▼
┌────────────────┐
│  Logic Layer   │◄───── queryLogic uses:
│                │       • serviceDAL
└────────┬───────┘       • intentDAL
         │
         ▼
┌────────────────┐
│   DAL Layer    │
│                │
└────────┬───────┘
         │
         ▼
┌────────────────┐
│    MongoDB     │
└────────────────┘
```

## Component Responsibilities

### Query Controller
- Receives HTTP POST requests at `/query`
- Validates QueryRequest
- Calls QueryLogic
- Returns QueryResponse

### Query Logic
- Extracts keywords from natural language
- Searches services using serviceDAL
- Extracts intents from found services
- Formats natural language response
- Supports both keyword and AI modes

### Service DAL
- Queries MongoDB services collection
- Populates intents from intent_ids
- Returns services with full intent data

### Intent DAL
- Queries MongoDB intents collection
- Provides intent data for services

## Key Differences from Old Architecture

### Old Way (Separate Services)
❌ Two services to deploy/manage
❌ HTTP calls between AQS → API (network overhead)
❌ Duplicate NATS connection logic
❌ Two separate startup scripts
❌ Query logic couldn't directly access DAL

### New Way (Merged)
✅ Single service to deploy
✅ Direct DAL access (no HTTP overhead)
✅ Single NATS connection (if enabled)
✅ One startup script
✅ Query logic directly uses serviceDAL/intentDAL
✅ Cleaner dependency injection
```

---
**Diagram Version:** 2.0
**Architecture:** Three-Layer with Query Integration
**Deployment:** Single Unified Service
