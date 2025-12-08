import subprocess
import time
import os
import sys

# --- Paths ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # UIMservicemanager folder
API_DIR = os.path.join(BASE_DIR, "API")
FRONTEND_DIR = os.path.join(BASE_DIR, "Client-Interface")
MONGO_PATH = os.path.join(API_DIR, "DAL", "mongoDB-Configs", "bin", "mongod.exe")
DB_PATH = os.path.join(API_DIR, "DAL", "mongoDB-Configs", "data")
LOG_PATH = os.path.join(API_DIR, "DAL", "mongoDB-Configs", "log", "mongod.log")
MONGO_PORT = "27017"

# --- Print startup banner ---
print("=" * 60)
print("DVerse UIM Service Manager - Startup")
print("=" * 60)

# --- Ask user if they want to start frontend ---
response = input("\n🎨 Do you want to start the frontend? (y/n): ").strip().lower()
start_frontend = response in ['y', 'yes']

# --- Kill any existing MongoDB process ---
print("\n🧹 Checking for existing MongoDB processes...")
subprocess.run(["taskkill", "/F", "/IM", "mongod.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# --- Ensure log directory exists ---
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

# --- Start MongoDB ---
print("🚀 Starting MongoDB...")
mongo_process = subprocess.Popen(
    [MONGO_PATH, "--dbpath", DB_PATH, "--logpath", LOG_PATH, "--port", MONGO_PORT],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)

# --- Wait for MongoDB to initialize ---
print("⏳ Waiting for MongoDB to initialize (5 seconds)...")
time.sleep(5)

# --- Start NATS Server (Docker) ---
print("🚀 Starting NATS server (Docker)...")
print("   Note: Requires Docker to be running. If Docker is not available,")
print("         NATS messaging will not work, but REST API will still function.")

nats_process = None
try:
    # Check if NATS container already exists
    existing_nats = subprocess.run(
        ["docker", "ps", "-a", "-q", "-f", "name=dverse-nats"],
        capture_output=True,
        text=True
    )
    
    if existing_nats.stdout.strip():
        print("   ℹ️  NATS container already exists, restarting...")
        subprocess.run(["docker", "start", "dverse-nats"], check=True)
    else:
        print("   ℹ️  Creating new NATS container...")
        subprocess.run([
            "docker", "run", "-d",
            "--name", "dverse-nats",
            "-p", "4222:4222",
            "-p", "8222:8222",
            "nats:latest"
        ], check=True)
    
    print("✅ NATS server started on ports 4222 (client) and 8222 (monitoring)")
    nats_process = "docker"  # Flag that NATS is running
    
except subprocess.CalledProcessError:
    print("⚠️  Failed to start NATS (Docker might not be running)")
    print("   REST API will work, but NATS messaging will be unavailable")
except FileNotFoundError:
    print("⚠️  Docker not found - NATS messaging will be unavailable")
    print("   REST API will work normally")

time.sleep(2)

# --- Start FastAPI API (now includes NATS integration) ---
print("⚙️  Starting FastAPI API on http://localhost:8000...")
print("   ℹ️  API now includes Agent Query Service functionality")

fastapi_process = subprocess.Popen(
    ["python", "-m", "uvicorn", "main:app", "--reload"],
    cwd=API_DIR,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)

# Give FastAPI time to start
print("⏳ Waiting for FastAPI to initialize (5 seconds)...")
time.sleep(5)

# --- Start Frontend (if requested) ---
frontend_process = None
if start_frontend:
    print("🎨 Starting Frontend (Vite dev server)...")
    if not os.path.exists(FRONTEND_DIR):
        print(f"⚠️  Warning: Frontend directory not found at {FRONTEND_DIR}")
        print("   Continuing without frontend...")
    else:
        try:
            frontend_process = subprocess.Popen(
                ["npm", "run", "dev"],
                cwd=FRONTEND_DIR,
                shell=True
            )
            print("⏳ Waiting for Vite to initialize (5 seconds)...")
            time.sleep(5)
            print("✅ Frontend available at http://localhost:3000")
        except Exception as e:
            print(f"⚠️  Failed to start frontend: {e}")
            print("   Continuing without frontend...")

# --- All services started ---
print("\n" + "=" * 60)
print("🎉 All services started successfully!")
print("=" * 60)
print("\n📋 Service Status:")
print(f"   • MongoDB:     Running on port {MONGO_PORT}")
if nats_process:
    print(f"   • NATS:        Running on ports 4222 (client), 8222 (monitoring)")
else:
    print(f"   • NATS:        ⚠️  Not available (Docker required)")
print(f"   • API API: http://localhost:8000")
print(f"   • API API Docs: http://localhost:8000/docs")
if frontend_process:
    print(f"   • Frontend:    http://localhost:3000")

print("\n📖 Available Endpoints:")
print("   REST API:")
print("     - GET/POST/PUT/DELETE /services")
print("     - GET/POST/PUT/DELETE /intents")
print("     - GET/POST/PUT/DELETE /uimprotocol")
print("     - POST /query (Natural language queries)")
if nats_process:
    print("\n   NATS Messaging:")
    print("     - Subscribe: uim.catalogue.query")
    print("     - Publish:   uim.catalogue.response")

print("\n⌨️  Press Ctrl+C to stop all services.")
print("=" * 60 + "\n")

try:
    # Keep script running and wait for keyboard interrupt
    fastapi_process.wait()
except KeyboardInterrupt:
    print("\n🛑 Shutting down services...")

    # Stop Frontend
    if frontend_process:
        print("🎨 Stopping Frontend...")
        frontend_process.terminate()
        try:
            frontend_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            frontend_process.kill()
        print("✅ Frontend stopped.")

    # Stop FastAPI
    print("⚙️  Stopping FastAPI API...")
    fastapi_process.terminate()
    try:
        fastapi_process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        fastapi_process.kill()
    print("✅ API stopped.")

    # Stop NATS (Docker container)
    if nats_process:
        print("🛑 Stopping NATS server...")
        try:
            subprocess.run(["docker", "stop", "dverse-nats"], timeout=10)
            print("✅ NATS stopped.")
        except Exception as e:
            print(f"⚠️  Error stopping NATS: {e}")

    # Stop MongoDB
    print("🗄️  Stopping MongoDB...")
    mongo_process.terminate()
    mongo_process.wait()
    print("✅ MongoDB stopped.")

    print("\n👋 All services shut down successfully!")
    sys.exit(0)
