# UIM Catalogue Frontend

A Solid.js web application for browsing UIM services and intents.

## Prerequisites

- Node.js (v18 or higher)
- npm (comes with Node.js)
- FastAPI backend running on `http://localhost:8000`

## Project Structure

```
Demo-Frontend/
├── index.html              # Entry HTML file
├── vite.config.js          # Vite configuration
├── package.json            # Dependencies and scripts
└── src/
    ├── index.jsx           # Application entry point
    └── App.jsx             # Main application component
```

## Installation

1. **Navigate to the frontend directory:**
   ```bash
   cd Demo-Frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

## Running the Application

1. **Make sure your FastAPI backend is running on port 8000:**
  
2. **Start the development server:**
   ```bash
   npm run dev
   ```

3. **Open your browser:**
   ```
   http://localhost:5173
   ```

## Available Scripts

- `npm run dev` - Start development server with hot reload
- `npm run build` - Build for production
- `npm run preview` - Preview production build locally

## Troubleshooting

### "React is not defined" error

If you see this error, your `src/index.jsx` file has incorrect code. It should be:

```jsx
import { render } from 'solid-js/web';
import App from './App';

render(() => <App />, document.getElementById('root'));
```

**NOT:**
```jsx
render(() => React.createElement(App, null), document.getElementById('root'));
```

**Fix:**
1. Stop the dev server (Ctrl+C)
2. Delete `node_modules/.vite/` folder
3. Run `npm run dev` again
4. Hard refresh browser (Ctrl+Shift+R)

### Blank screen with no errors

1. Check browser console (F12) for errors
2. Verify backend is running: `curl http://localhost:8000/services`
3. Check that all files are in correct locations (see Project Structure)

### Failed to fetch services/intents

- Ensure FastAPI backend is running on port 8000
- Check CORS settings on your backend
- Verify API endpoints return correct JSON format

### Port already in use

If port 5173 is occupied, Vite will automatically use the next available port (5174, 5175, etc.)

## API Endpoints Used

The frontend expects these endpoints:

- `GET http://localhost:8000/services` - Returns array of service objects
- `GET http://localhost:8000/intents` - Returns array of intent objects

### Expected Response Format

**Services:**
```json
[
  {
    "name": "service-name",
    "description": "Service description",
    "service_URL": "http://example.com"
  }
]
```

**Intents:**
```json
[
  {
    "name": "IntentName",
    "description": "Intent description",
    "tags": ["tag1", "tag2"],
    "rateLimit": 1000,
    "price": 0
  }
]
```

## Technologies Used

- **Solid.js** - Reactive UI framework
- **Vite** - Build tool and dev server
- **Tailwind CSS** (CDN) - Styling

## Notes

- The Tailwind CSS CDN warning in the console is normal for development
- For production, you should set up proper Tailwind configuration
- The app uses a single-page design with tab switching (no router)