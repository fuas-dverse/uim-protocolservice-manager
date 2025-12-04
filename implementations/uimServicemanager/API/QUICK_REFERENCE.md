# API + AQS Merge - Quick Reference

## 📦 Files to Download

All files are available in `/mnt/user-data/outputs/`:

1. **MERGE_GUIDE.md** - Complete implementation guide (READ THIS FIRST!)
2. **StartupService.py** - New startup script (goes in `UIMservicemanager/`)
3. **main.py** - Updated FastAPI app (replaces `API/main.py`)
4. **queryController.py** - New controller (goes in `API/Presentation/Controller/`)
5. **queryViewmodel.py** - New viewmodel (goes in `API/Presentation/Viewmodel/`)
6. **queryLogic.py** - New logic layer (goes in `API/logicLayer/Logic/`)
7. **requirements.txt** - Updated dependencies (replaces `API/requirements.txt`)
8. **test_merge.py** - Test script to verify everything works

## 🚀 Quick Start (5 minutes)

```bash
# 1. Download all files from outputs/

# 2. Copy files to your project
cd /path/to/UIMservicemanager

# Root level
cp ~/Downloads/StartupService.py ./

# API files
cp ~/Downloads/main.py ./API/
cp ~/Downloads/queryController.py ./API/Presentation/Controller/
cp ~/Downloads/queryViewmodel.py ./API/Presentation/Viewmodel/
cp ~/Downloads/queryLogic.py ./API/logicLayer/Logic/
cp ~/Downloads/requirements.txt ./API/

# 3. Install dependencies
cd API
pip install faststream[nats] nats-py loguru --break-system-packages

# 4. Start Docker (for NATS)
docker run -d --name dverse-nats -p 4222:4222 -p 8222:8222 nats:latest

# 5. Start the service
cd ..
python StartupService.py

# 6. Test it
python test_merge.py
```

## 🎯 What Changed

### New Endpoints
- `POST /query` - Natural language queries (keyword mode by default)
- `GET /query/health` - Check query service status

### Enhanced Endpoints
- `GET /` - Now shows service status and available features
- `GET /health` - Shows NATS connection status

### Existing Endpoints (Unchanged)
- `GET/POST/PUT/DELETE /services` - Same as before
- `GET/POST/PUT/DELETE /intents` - Same as before
- `GET/POST/PUT/DELETE /uimprotocol` - Same as before

## 📝 Testing Checklist

After starting the service:

```bash
# Basic health check
curl http://localhost:8000/health

# Test query endpoint
curl -X POST http://localhost:8000/query/ \
  -H "Content-Type: application/json" \
  -d '{"query": "Find weather services", "use_ai": false}'

# Run full test suite
python test_merge.py

# Or use the browser
open http://localhost:8000/docs
```

## 🔧 Configuration

### Required
- MongoDB running on port 27017
- Docker running (for NATS)

### Optional
Create `API/.env` for AI mode:
```env
OPENAI_API_KEY=sk-your-key-here
```

## ⚡ Key Features

### Keyword Mode (Default)
- ✅ No API keys needed
- ✅ Fast response
- ✅ Good for simple queries
- Example: `"Find me weather services"`

### AI Mode (Optional)
- ✅ Better natural language understanding
- ✅ Context-aware responses
- ❌ Requires OPENAI_API_KEY
- Example: `"I need a service that can send automated emails"`

## 🐛 Common Issues

| Issue | Fix |
|-------|-----|
| "NATS connection failed" | `docker start dverse-nats` |
| "Module not found: faststream" | `pip install faststream[nats] --break-system-packages` |
| "No services found" | Make sure database is seeded |
| "Port 8000 in use" | Stop other FastAPI instances |

## 📚 Documentation

- **Full guide:** `MERGE_GUIDE.md`
- **API docs:** http://localhost:8000/docs (when running)
- **NATS monitor:** http://localhost:8222 (when running)

## ✅ Success Criteria

You'll know it worked when:
1. Startup script runs without errors
2. `curl http://localhost:8000/health` returns `{"status": "healthy"}`
3. `curl http://localhost:8000/services` returns your services
4. `POST /query` returns relevant results
5. All 7 tests in `test_merge.py` pass

## 🎉 What You Gain

- ✅ Single unified service (easier to deploy)
- ✅ Natural language query interface
- ✅ Both HTTP and NATS messaging support
- ✅ Cleaner architecture
- ✅ Better startup management
- ✅ Extensible for future AI features

## 📞 Need Help?

Check these in order:
1. Read `MERGE_GUIDE.md` (comprehensive guide)
2. Run `test_merge.py` (automated testing)
3. Check console logs for errors
4. Verify Docker is running
5. Check MongoDB is accessible

---

**Version:** 2.0.0
**Last Updated:** December 4, 2024
**Merged:** API + Agent Query Service
