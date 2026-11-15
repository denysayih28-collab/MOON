import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/main-api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/main-api/, '/api'),
      },
      '/simulation-api': {
        target: 'http://127.0.0.1:8001',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/simulation-api/, '/api'),
      },
      '/main-health': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        rewrite: () => '/api/health',
      },
      '/simulation-health': {
        target: 'http://127.0.0.1:8001',
        changeOrigin: true,
        rewrite: () => '/health',
      },
    },
  },
})
