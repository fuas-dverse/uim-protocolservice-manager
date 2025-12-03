# Startup Steps

## Prerequisites
- Docker Desktop running
- Python environment set up
- FastStream installed with NATS support

## Startup Sequence

### 1. Start NATS Server (Docker)
Open a terminal and run:
```bash
docker run --name nats-server --rm -p 4222:4222 -p 8222:8222 nats:latest
```

**Expected output:**
```
[1] [INF] Starting nats-server version X.X.X
[1] [INF] Starting http monitor on 0.0.0.0:8222
[1] [INF] Listening for client connections on 0.0.0.0:4222
[1] [INF] Server is ready
```

**Keep this terminal open** - the NATS server needs to run while you're developing.

---

### 2. Start FastAPI Backend and Optional Frontend (UIM Catalogue)
Open a **new terminal** and navigate to your backend directory:
```bash
cd implementations/uimServicemanager/Backend
python StartupService.py
#2nd expected output if started with Frontend
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
```

**Expected output:**
```
VITE vX.X.X  ready in XXX ms
➜  Local:   http://localhost:5173/
```

---

### 4. Start Chatbot Service
Open a **new terminal** and navigate to your chatbot directory:
```bash
cd /implemenation/uimServicemanager/agent-query-sevice
python main_keyword.py
```

---

## Shutdown Sequence

1. **Stop Chatbot Service**: `Ctrl+C` in chatbot terminal
2. **Stop Frontend** (if running): `Ctrl+C` in frontend terminal
3. **Stop Backend**: `Ctrl+C` in backend terminal
4. **Stop NATS Server**: `Ctrl+C` in NATS terminal (container auto-removes with `--rm` flag)

---

## Ports Overview

| Service          | Port | URL                          |
|------------------|------|------------------------------|
| NATS (client)    | 4222 | `nats://localhost:4222`      |
| NATS (monitor)   | 8222 | `http://localhost:8222`      |
| FastAPI Backend  | 8000 | `http://localhost:8000`      |
| Frontend         | 5173 | `http://localhost:5173`      |

---

## Quick Checks

### Verify NATS is running:
Open browser: `http://localhost:8222`
- Should show NATS server monitoring page

### Verify Backend is running:
Open browser: `http://localhost:8000/docs`
- Should show FastAPI Swagger documentation

### Verify Frontend is running:
Open browser: `http://localhost:5173`
- Should show your Solid.js application

---

## Troubleshooting

**Port already in use?**
```bash
# Find what's using the port (example for 4222)
lsof -i :4222
# Kill the process if needed
kill -9 <PID>
```

**NATS won't start?**
- Make sure Docker Desktop is running
- Check if port 4222 is already in use
- Try pulling the image again: `docker pull nats:latest`

**Can't connect to NATS from Python?**
- Verify NATS server is running: `http://localhost:8222`
- Check connection URL is `nats://localhost:4222` (not `http://`)