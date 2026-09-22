import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite' // Добавлен импорт

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(), // Добавлен вызов плагина
  ],
  // ... (остальные настройки, если они были, оставляем без изменений)
})
