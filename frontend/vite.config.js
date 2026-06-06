import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [vue()],
    server: {
        port: 5173,
        proxy: {
            // 代理 API 请求到后端
            '/api': {
                target: 'http://localhost:8000',
                changeOrigin: true
            },
            '/outputs': {
                target: 'http://localhost:8000',
                changeOrigin: true
            }
        }
    }
})
