# API + AQS Merge - Implementation Guide

This guide walks you through merging the Agent Query Service into your API API.

## Overview

**What we're doing:** Combining the separate `agent-query-service` and `API` into a single unified API that supports:
- ✅ All existing REST API endpoints (`/services`, `/intents`, `/uimprotocol`)
- ✅ New natural language query endpoint (`/query`)
- ✅ Optional NATS messaging for agent-to-agent communication
- ✅ Both keyword-based and AI-powered query modes

## Files You Need to Update/Add

### 1. Root Level Files

**File:** `UIMservicemanager/StartupService.py`
- **Action:** CREATE NEW (replaces `API/StartupService.py`)
- **What it does:** Starts MongoDB, NATS (Docker), API API, and optionally Frontend
- **Location:** `/mnt/user-data/outputs/StartupService.py`

### 2. API Files

**File:** `API/main.py`
- **Action:** REPLACE ENTIRE FILE
- **What changed:** Added NATS lifespan management, query controller route
- **Location:** `/mnt/user-data/outputs/main.py`

**File:** `API/Presentation/Controller/queryController.py`
- **Action:** CREATE NEW
- **What it does:** HTTP endpoint for `/query` - handles natural language queries
- **Location:** `/mnt/user-data/outputs/queryController.py`

**File:** `API/Presentation/Viewmodel/queryViewmodel.py`
- **Action:** CREATE NEW
- **What it does:** Pydantic models for QueryRequest and QueryResponse
- **Location:** `/mnt/user-data/outputs/queryViewmodel.py`

**File:** `API/logicLayer/Logic/queryLogic.py`
- **Action:** CREATE NEW
- **What it does:** Business logic for keyword and AI query processing
- **Location:** `/mnt/user-data/outputs/queryLogic.py`

**File:** `API/requirements.txt`
- **Action:** UPDATE (add new dependencies)
- **Location:** `/mnt/user-data/outputs/requirements.txt`

## Step-by-Step Implementation

### Step 1: Backup Your Current Code

```bash
cd /path/to/UIMservicemanager
git add .
git commit -m "Backup before AQS merge"
git push origin dev
```

### Step 2: Update Dependencies

```bash
cd API
pip install -r requirements.txt --break-system-packages
```

**New dependencies added:**
- `faststream[nats]` - NATS messaging
- `nats-py` - NATS client
- `loguru` - Better logging

**Optional (for AI mode):**
- `pydantic-ai` - AI-powered query processing
- `openai` - OpenAI API access

### Step 3: Add New Files

```bash
# From UIMservicemanager directory

# 1. Move new startup script to root
cp /path/to/downloaded/StartupService.py ./StartupService.py

# 2. Update API main.py
cp /path/to/downloaded/main.py ./API/main.py

# 3. Add query controller
cp /path/to/downloaded/queryController.py ./API/Presentation/Controller/queryController.py

# 4. Add query viewmodel
cp /path/to/downloaded/queryViewmodel.py ./API/Presentation/Viewmodel/queryViewmodel.py

# 5. Add query logic
cp /path/to/downloaded/queryLogic.py ./API/logicLayer/Logic/queryLogic.py

# 6. Update requirements
cp /path/to/downloaded/requirements.txt ./API/requirements.txt
```

### Step 4: Install Dependencies

```bash
cd API
pip install faststream[nats] nats-py loguru --break-system-packages

# Optional: If you want AI mode
# pip install pydantic-ai openai --break-system-packages
```

### Step 5: Start Docker (for NATS)

```bash
# Make sure Docker Desktop is running, then:
docker run -d --name dverse-nats -p 4222:4222 -p 8222:8222 nats:latest

# Verify it's running:
curl http://localhost:8222/healthz
```

### Step 6: Test the Merge

```bash
# From UIMservicemanager directory
python StartupService.py

# Choose 'n' for no frontend (to test backend first)
```

**Expected output:**
```
🚀 Starting MongoDB...
✅ MongoDB started
🚀 Starting NATS server...
✅ NATS server started on ports 4222, 8222
⚙️  Starting FastAPI API...
✅ API starting on http://localhost:8000

📋 Service Status:
   • MongoDB:     Running on port 27017
   • NATS:        Running on ports 4222 (client), 8222 (monitoring)
   • API API: http://localhost:8000
```

### Step 7: Verify Everything Works

**Test 1: Check health endpoint**
```bash
curl http://localhost:8000/health
```

Expected:
```json
{
  "status": "healthy",
  "nats_connected": true
}
```

**Test 2: Check root endpoint**
```bash
curl http://localhost:8000/
```

Expected:
```json
{
  "message": "UIM Service Manager API",
  "version": "2.0.0",
  "features": {
    "rest_api": true,
    "nats_messaging": true,
    "query_interface": true
  }
}
```

**Test 3: Test query endpoint (keyword mode)**
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Find me weather services",
    "use_ai": false
  }'
```

Expected response with services matching "weather".

**Test 4: Check existing endpoints still work**
```bash
curl http://localhost:8000/services
curl http://localhost:8000/intents
```

## What Got Removed

You can now **delete** these files/folders (they're no longer needed):

- `agent-query-service/` entire folder
- `API/StartupService.py` (moved to root level)

## Configuration

### Environment Variables

Create a `.env` file in the `API` directory (optional):

```env
# NATS Configuration
NATS_URL=nats://localhost:4222

# AI Mode (Optional - only if you want AI-powered queries)
OPENAI_API_KEY=sk-your-api-key-here
```

**Note:** If you don't set `OPENAI_API_KEY`, the system will work fine in keyword mode only.

## Architecture Changes

### Before:
```
agent-query-service (separate service)
├── NATS subscriber
├── Pydantic AI
└── HTTP client → calls API API

API (separate service)
├── REST API
└── MongoDB
```

### After:
```
API (unified service)
├── REST API
│   ├── /services
│   ├── /intents
│   ├── /uimprotocol
│   └── /query (NEW!)
├── NATS integration (optional)
│   ├── Subscribe: uim.catalogue.query
│   └── Publish: uim.catalogue.response
├── Query Logic (NEW!)
│   ├── Keyword mode (default)
│   └── AI mode (optional)
└── MongoDB
```

## Usage Examples

### HTTP Query (Keyword Mode)

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Find payment processing services",
    "agent_id": "web-app",
    "use_ai": false
  }'
```

### HTTP Query (AI Mode)

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "I need a service that can send automated emails",
    "agent_id": "web-app",
    "use_ai": true
  }'
```

### Query via FastAPI Docs

1. Go to http://localhost:8000/docs
2. Find `POST /query`
3. Click "Try it out"
4. Enter your query
5. Execute

## Troubleshooting

### "NATS connection failed"

**Cause:** Docker not running or NATS container not started

**Fix:**
```bash
docker start dverse-nats
# or
docker run -d --name dverse-nats -p 4222:4222 -p 8222:8222 nats:latest
```

**Note:** Even if NATS fails, the REST API will work fine. Only NATS messaging will be unavailable.

### "Module not found: faststream"

**Fix:**
```bash
pip install faststream[nats] --break-system-packages
```

### "Module not found: loguru"

**Fix:**
```bash
pip install loguru --break-system-packages
```

### "AI mode not working"

**Check:**
1. Is `OPENAI_API_KEY` set in `.env`?
2. Is `pydantic-ai` installed?
```bash
pip install pydantic-ai openai --break-system-packages
```

### Query returns no results

**Check:**
1. Is your database seeded with data?
2. Try a broader search term
3. Check logs for errors

## Testing Checklist

- [ ] MongoDB starts successfully
- [ ] NATS starts successfully (or gracefully degrades)
- [ ] API API starts on port 8000
- [ ] `/health` endpoint returns healthy status
- [ ] `/services` endpoint returns services
- [ ] `/intents` endpoint returns intents
- [ ] `/query` endpoint works in keyword mode
- [ ] (Optional) `/query` endpoint works in AI mode
- [ ] API docs accessible at `/docs`
- [ ] Frontend can connect (if you start it)

## What's Next?

After verifying everything works:

1. **Commit your changes:**
```bash
git add .
git commit -m "Merge AQS into API - unified query interface"
git push origin dev
```

2. **Update your documentation** to reflect the new unified API

3. **Delete the old agent-query-service folder:**
```bash
rm -rf agent-query-service/
git add .
git commit -m "Remove old agent-query-service folder"
git push origin dev
```

## Questions?

If you encounter issues:
1. Check the console logs for detailed error messages
2. Verify all files are in the correct locations
3. Ensure Docker is running if you want NATS support
4. Test endpoints one by one using curl or the `/docs` interface

## Summary

✅ **What you gained:**
- Single unified service
- Cleaner architecture
- Query interface via HTTP REST API
- Optional NATS messaging for agents
- Both keyword and AI query modes
- Better startup script

✅ **What stayed the same:**
- All existing REST API endpoints
- MongoDB database structure
- Frontend integration
- Three-layer architecture

🎉 **Result:** A more maintainable, feature-rich API with query capabilities!
