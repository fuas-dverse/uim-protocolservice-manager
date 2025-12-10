"""
DVerse Chatbot Startup Service

Starts:
1. Chatbot Backend (FastAPI + Pydantic AI + Ollama) on port 8001
2. Chatbot Frontend (Vite/Solid.js) on port 3001 (optional)

Prerequisites:
- Ollama running with llama3.2 model
- Backend API running on port 8000 (for service discovery)
- Node.js installed (for frontend)
"""
import subprocess
import time
import os
import sys

# --- Paths ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # uim-chatbot folder
FRONTEND_DIR = os.path.join(BASE_DIR, "Client-interface")

# --- Print startup banner ---
print("=" * 70)
print("DVerse Chatbot Service - Startup")
print("=" * 70)

# --- Ask user if they want to start frontend ---
response = input("\n🎨 Do you want to start the frontend? (y/n): ").strip().lower()
start_frontend = response in ['y', 'yes']

# --- Check prerequisites ---
print("\n🔍 Checking prerequisites...")

# Check if Ollama is running
try:
    import httpx

    result = subprocess.run(
        ["curl", "-s", "http://localhost:11434/api/version"],
        capture_output=True,
        text=True,
        timeout=3
    )
    if result.returncode == 0:
        print("✅ Ollama is running on port 11434")
    else:
        print("⚠️  Warning: Could not verify Ollama is running")
        print("   Make sure Ollama is started and llama3.2 model is available")
        print("   Run: ollama run llama3.2")
except Exception as e:
    print("⚠️  Warning: Could not check Ollama status")
    print("   Make sure Ollama is started: ollama run llama3.2")

# Check if Backend API is reachable
try:
    result = subprocess.run(
        ["curl", "-s", "http://localhost:8000/"],
        capture_output=True,
        text=True,
        timeout=3
    )
    if result.returncode == 0:
        print("✅ Backend API is accessible on port 8000")
    else:
        print("⚠️  Warning: Backend API not reachable on port 8000")
        print("   The chatbot needs the Backend API for service discovery")
except Exception:
    print("⚠️  Warning: Could not verify Backend API status")

print()

# --- Start Chatbot Backend (FastAPI) ---
print("🤖 Starting Chatbot Backend on http://localhost:8001...")

chatbot_process = subprocess.Popen(
    ["python", "-m", "uvicorn", "main:app", "--reload", "--port", "8001"],
    cwd=BASE_DIR,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1
)

# Give FastAPI time to start and capture initial output
print("⏳ Waiting for Chatbot Backend to initialize...")
time.sleep(3)

# Check if process is still running
if chatbot_process.poll() is not None:
    print("❌ Error: Chatbot Backend failed to start!")
    print("\nPlease check:")
    print("  1. All dependencies installed: pip install -r requirements.txt")
    print("  2. Ollama is running: ollama run llama3.2")
    print("  3. No other service using port 8001")
    sys.exit(1)

print("✅ Chatbot Backend started on http://localhost:8001")

# --- Start Frontend (if requested) ---
frontend_process = None
if start_frontend:
    print("\n🎨 Starting Chatbot Frontend...")

    if not os.path.exists(FRONTEND_DIR):
        print(f"⚠️  Warning: Frontend directory not found at {FRONTEND_DIR}")
        print("   Continuing without frontend...")
    else:
        # Check if node_modules exists
        node_modules_path = os.path.join(FRONTEND_DIR, "node_modules")
        if not os.path.exists(node_modules_path):
            print("⚠️  Warning: node_modules not found. Running npm install first...")
            print("   This may take a minute...")

            install_process = subprocess.run(
                ["npm", "install"],
                cwd=FRONTEND_DIR,
                capture_output=True
            )

            if install_process.returncode != 0:
                print("❌ Error: npm install failed!")
                print("   Please run 'npm install' manually in the Client-interface folder")
                print("   Continuing without frontend...")
            else:
                print("✅ Dependencies installed")

        try:
            frontend_process = subprocess.Popen(
                ["npm", "run", "dev"],
                cwd=FRONTEND_DIR,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )

            print("⏳ Waiting for Vite to initialize...")
            time.sleep(5)

            # Check if frontend process is still running
            if frontend_process.poll() is not None:
                print("⚠️  Warning: Frontend failed to start")
                print("   Check the error above and try starting it manually")
                frontend_process = None
            else:
                print("✅ Frontend available at http://localhost:3001")

        except Exception as e:
            print(f"⚠️  Failed to start frontend: {e}")
            print("   Continuing without frontend...")
            frontend_process = None

# --- All services started ---
print("\n" + "=" * 70)
print("🎉 Chatbot services started successfully!")
print("=" * 70)

print("\n📋 Service Status:")
print(f"   • Chatbot Backend:  http://localhost:8001")
print(f"   • API Docs:         http://localhost:8001/docs")
if frontend_process:
    print(f"   • Frontend:         http://localhost:3001")
else:
    print(f"   • Frontend:         Not started")

print("\n⚠️  Important:")
print("   • Make sure Ollama is running: ollama run llama3.2")
print("   • Make sure Backend API is running on port 8000")

print("\n⌨️  Press Ctrl+C to stop all services.")
print("=" * 70 + "\n")

try:
    # Keep script running and wait for keyboard interrupt
    # Print chatbot output in real-time
    for line in chatbot_process.stdout:
        print(f"[Chatbot] {line.rstrip()}")

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

    # Stop Chatbot Backend
    print("🤖 Stopping Chatbot Backend...")
    chatbot_process.terminate()
    try:
        chatbot_process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        chatbot_process.kill()
    print("✅ Chatbot Backend stopped.")

    print("\n👋 All chatbot services shut down successfully!")
    sys.exit(0)