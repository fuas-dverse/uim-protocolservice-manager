import subprocess
import time
import os
import sys

# --- Paths ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Backend folder
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "Demo-Frontend")  # Frontend folder
MONGO_PATH = os.path.join(BASE_DIR, "DAL", "mongoDB-Configs", "bin", "mongod.exe")
DB_PATH = os.path.join(BASE_DIR, "DAL", "mongoDB-Configs", "data")
LOG_PATH = os.path.join(BASE_DIR, "DAL", "mongoDB-Configs", "log", "mongod.log")
MONGO_PORT = "27017"

# --- Ask user if they want to start frontend ---
print("=" * 50)
print("DVerse Catalogue Startup")
print("=" * 50)
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

# --- Wait a few seconds to let Mongo start ---
print("⏳ Waiting for MongoDB to initialize...")
time.sleep(5)

# --- Start FastAPI ---
print("⚙️ Starting FastAPI service on http://localhost:8000...")
fastapi_process = subprocess.Popen(
    ["python", "-m", "uvicorn", "main:app", "--reload"],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)

# Give FastAPI time to start before launching frontend
print("⏳ Waiting for FastAPI to initialize...")
time.sleep(3)

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
            print("⏳ Waiting for Vite to initialize...")
            time.sleep(5)
            print("✅ Frontend starting on http://localhost:3000")
        except Exception as e:
            print(f"⚠️  Failed to start frontend: {e}")
            print("   Continuing without frontend...")

# --- All services running ---
print("\n" + "=" * 50)
print("All services started! Press Ctrl+C to stop.")
print("=" * 50 + "\n")

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
    print("⚙️ Stopping FastAPI...")
    fastapi_process.terminate()
    try:
        fastapi_process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        fastapi_process.kill()
    print("✅ FastAPI stopped.")

    # Stop MongoDB
    print("🗄️  Stopping MongoDB...")
    mongo_process.terminate()
    mongo_process.wait()
    print("✅ MongoDB stopped.")

    print("\n👋 All services shut down successfully!")
    sys.exit(0)