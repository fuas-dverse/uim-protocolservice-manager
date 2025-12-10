# DVerse Chatbot Frontend

A Solid.js chat interface for interacting with the DVerse chatbot agent.

## Prerequisites

- Node.js (v18 or higher)
- npm (comes with Node.js)
- Chatbot backend running on `http://localhost:8001`

## Project Structure

```
chatbot-frontend/
├── index.html              # Entry HTML file
├── vite.config.js          # Vite configuration
├── package.json            # Dependencies and scripts
└── src/
    ├── index.jsx           # Application entry point
    └── App.jsx             # Main chat component
```

## Installation

1. **Navigate to the chatbot frontend directory:**
   ```bash
   cd chatbot-frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

## Running the Application

1. **Make sure your chatbot backend is running on port 8001:**
   ```bash
   cd ../uim-chatbot
   python main.py
   ```

2. **Start the development server:**
   ```bash
   npm run dev
   ```

3. **Open your browser:**
   ```
   http://localhost:3001
   ```

## Available Scripts

- `npm run dev` - Start development server with hot reload
- `npm run build` - Build for production
- `npm run preview` - Preview production build locally

## Features

- 💬 **Real-time Chat Interface** - Natural conversation with the AI agent
- 🔍 **Service Discovery** - Bot discovers and invokes services from the catalogue
- 📊 **Service Information** - See which services were used to answer queries
- 🎨 **Clean UI** - Modern, responsive design with Tailwind CSS
- ⚡ **Fast** - Built with Solid.js for optimal performance

## Usage Examples

Try asking the chatbot:

- "Find papers about neural networks"
- "Search arXiv for machine learning research"
- "What weather services are available?"
- "Get the latest AI news"

The bot will:
1. Understand your query
2. Discover relevant services from the catalogue
3. Invoke those services with appropriate parameters
4. Return formatted results in natural language

## API Endpoints Used

The frontend communicates with:

- `POST http://localhost:8001/chat` - Send chat messages

### Request Format

```json
{
  "user_id": "user-123",
  "message": "Find papers about AI",
  "context": {}
}
```

### Response Format

```json
{
  "user_id": "user-123",
  "message": "I found 5 papers about AI...",
  "query": "Find papers about AI",
  "services_discovered": ["arXiv API"],
  "service_invocation": {
    "service_name": "arXiv API",
    "intent_name": "search_papers",
    "success": true,
    "data": {...}
  },
  "success": true,
  "timestamp": "2025-12-10T10:00:00Z"
}
```

## Troubleshooting

### "Failed to connect to chatbot"

1. Verify chatbot backend is running: `curl http://localhost:8001/`
2. Check CORS settings on the backend
3. Make sure Ollama is running (required by the chatbot agent)

### Blank screen with no errors

1. Check browser console (F12) for errors
2. Verify all files are in correct locations
3. Try clearing browser cache and hard refresh (Ctrl+Shift+R)

### Port already in use

If port 3001 is occupied, Vite will automatically use the next available port (3002, 3003, etc.)

### Messages not appearing

1. Check that the chatbot backend is actually running
2. Look at the browser network tab (F12 → Network) to see if requests are being sent
3. Check chatbot backend logs for errors

## Technologies Used

- **Solid.js** - Reactive UI framework
- **Vite** - Build tool and dev server
- **Tailwind CSS** (CDN) - Styling
- **FastAPI Backend** - Chatbot service

## Notes

- The chat history is stored in memory and will be cleared on page refresh
- Each session gets a unique user ID (timestamp-based)
- The Tailwind CSS CDN warning in console is normal for development
- For production, set up proper Tailwind configuration

## Architecture

```
User Browser (port 3001)
    ↓ HTTP POST
Chatbot Agent (port 8001)
    ↓ Discovers services via
Backend API (port 8000)
    ↓ Returns service info
Chatbot Agent
    ↓ Invokes discovered service
External APIs (arXiv, etc.)
    ↓ Returns data
Chatbot Agent
    ↓ Formats response
User Browser
```

## Development Tips

- Messages are stored in a Solid.js signal: `messages()`
- Auto-scrolling is handled via `createEffect` watching message changes
- Loading state prevents duplicate submissions
- Press Enter to send, Shift+Enter for new lines

## Related Documentation

- Main README: `../README.md`
- Backend API docs: `http://localhost:8000/docs`
- Chatbot API docs: `http://localhost:8001/docs`
