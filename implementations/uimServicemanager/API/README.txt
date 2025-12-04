# API + AQS Merge - Installation Package

## 📦 What's in This Package

This zip contains everything you need to merge the Agent Query Service into your API.

### 📄 Files Included:

**Documentation**
- `QUICK_REFERENCE.md` - **START HERE!** 5-minute quick start guide
- `MERGE_GUIDE.md` - Complete step-by-step implementation guide  
- `ARCHITECTURE.md` - Visual diagrams of the merged system

**Code Files**
- `StartupService.py` - New startup script
- `main.py` - Updated FastAPI app
- `queryController.py` - Query endpoint controller
- `queryViewmodel.py` - Request/Response models
- `queryLogic.py` - Query processing logic
- `requirements.txt` - Updated dependencies

**Testing**
- `test_merge.py` - Automated test script

---

## 🚀 Quick Install (5 minutes)

```bash
# 1. Unzip the package
unzip backend-aqs-merge.zip -d merge-files

# 2. Navigate to your project
cd /path/to/UIMservicemanager

# 3. Copy files to correct locations

# Root level
cp merge-files/StartupService.py ./

# API directory
cp merge-files/main.py ./API/
cp merge-files/queryController.py ./API/Presentation/Controller/
cp merge-files/queryViewmodel.py ./API/Presentation/Viewmodel/
cp merge-files/queryLogic.py ./API/logicLayer/Logic/
cp merge-files/requirements.txt ./API/

# Copy test script
cp merge-files/test_merge.py ./

# 4. Install dependencies
cd API
pip install faststream[nats] nats-py loguru --break-system-packages

# 5. Start Docker (for NATS)
docker run -d --name dverse-nats -p 4222:4222 -p 8222:8222 nats:latest

# 6. Start the service
cd ..
python StartupService.py

# 7. Test it works
python test_merge.py
```

---

## 📋 File Locations

```
UIMservicemanager/
├── StartupService.py                                    ← NEW
├── test_merge.py                                        ← NEW (optional)
└── API/
    ├── main.py                                          ← REPLACE
    ├── requirements.txt                                 ← REPLACE
    ├── Presentation/
    │   ├── Controller/
    │   │   └── queryController.py                       ← NEW
    │   └── Viewmodel/
    │       └── queryViewmodel.py                        ← NEW
    └── logicLayer/
        └── Logic/
            └── queryLogic.py                            ← NEW
```

---

## ✅ What You're Getting

### New Endpoints
- `POST /query` - Natural language queries
- `GET /query/health` - Query service health check

### Enhanced Endpoints  
- `GET /` - Now shows service status
- `GET /health` - Shows NATS connection status

### Existing Endpoints (Unchanged)
- `GET/POST/PUT/DELETE /services`
- `GET/POST/PUT/DELETE /intents`
- `GET/POST/PUT/DELETE /uimprotocol`

---

## 🎯 Testing Checklist

After installation:

```bash
# Basic health check
curl http://localhost:8000/health

# Test query endpoint
curl -X POST http://localhost:8000/query/ \
  -H "Content-Type: application/json" \
  -d '{"query": "Find weather services", "use_ai": false}'

# Run full test suite
python test_merge.py

# Or use browser
open http://localhost:8000/docs
```

---

## 📚 Documentation

1. **QUICK_REFERENCE.md** - Start here for fast setup
2. **MERGE_GUIDE.md** - Detailed implementation guide
3. **ARCHITECTURE.md** - System architecture diagrams

---

## 🔧 Requirements

- Python 3.10+
- MongoDB running on port 27017
- Docker (for NATS messaging)
- Existing DVerse API project

---

## 💡 Key Features

### Keyword Mode (Default)
✅ No API keys needed
✅ Fast response  
✅ Works immediately

### AI Mode (Optional)
✅ Better understanding
✅ Context-aware
❌ Requires OPENAI_API_KEY

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| "NATS connection failed" | `docker start dverse-nats` |
| "Module not found" | `pip install faststream[nats] loguru --break-system-packages` |
| "No services found" | Seed your database |

---

## 📞 Need Help?

1. Read `QUICK_REFERENCE.md`
2. Run `test_merge.py`  
3. Check console logs
4. Verify Docker is running

---

**Version:** 2.0.0  
**Package Date:** December 4, 2024  
**Merged:** API + Agent Query Service

**Note:** All file paths have been updated to use "API" instead of "Backend" to match your renamed directory structure.
