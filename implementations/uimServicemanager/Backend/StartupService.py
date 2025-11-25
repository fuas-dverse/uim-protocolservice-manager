import subprocess
import time
import os

# --- Paths ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Backend folder
MONGO_PATH = os.path.join(BASE_DIR, "DAL", "mongoDB-Configs", "bin", "mongod.exe")
DB_PATH = os.path.join(BASE_DIR, "DAL", "mongoDB-Configs", "data")
LOG_PATH = os.path.join(BASE_DIR, "DAL", "mongoDB-Configs", "log", "mongod.log")
MONGO_PORT = "27017"

# --- Kill any existing MongoDB process ---
print("🧹 Checking for existing MongoDB processes...")
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
print("⚙️ Starting FastAPI service...")
try:
    subprocess.run(["python", "-m", "uvicorn", "main:app", "--reload"])
except KeyboardInterrupt:
    print("\n🛑 Shutting down services...")
    mongo_process.terminate()
    mongo_process.wait()
    print("✅ MongoDB stopped.")
