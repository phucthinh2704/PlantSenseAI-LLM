import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      "@app": "/src/app",
      "@assets": "/src/assets",
      "@components": "/src/components",
      "@configs": "/src/configs",
      "@hooks": "/src/hooks",
      "@layouts": "/src/layouts",
      "@pages": "/src/pages",
      "@services": "/src/services",
      "@tools": "/src/tools",
      "@redux": "/src/redux",
      "@utils": "/src/utils",

    }
  },
  server: {
    open: '/',
    port: 5173
  }
})
