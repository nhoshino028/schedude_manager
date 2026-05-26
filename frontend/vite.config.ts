import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  // ホットリロードを確実に動かすための設定追加
  server: {
    host: true,
    strictPort: true,
    watch: {
      usePolling: true,
    },
  },
})
