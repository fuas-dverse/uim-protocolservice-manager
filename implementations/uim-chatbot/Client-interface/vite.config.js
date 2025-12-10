import { defineConfig } from 'vite';
import solidPlugin from 'vite-plugin-solid';

export default defineConfig({
  plugins: [solidPlugin()],
  server: {
    port: 3001,  // Different port from API frontend (which uses 3000)
  },
  build: {
    target: 'esnext',
  },
});
