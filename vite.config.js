import {fileURLToPath, URL} from 'node:url'

import {defineConfig} from 'vite'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'
//import vueDevTools from 'vite-plugin-vue-devtools'
// 导入自动导入插件
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'

// https://vite.dev/config/
export default defineConfig({
    // logLevel: 'debug',
    logLevel: 'info',
    plugins: [
        vue(),
        vueJsx(),
//    vueDevTools(),
        AutoImport({
            resolvers: [ElementPlusResolver()],
            imports: ['vue'], // 自动导入 Vue 的 ref、reactive 等
            dts: './auto-imports.d.ts', // 仍需生成，供 WebStorm 识别
        }),
        Components({
            resolvers: [ElementPlusResolver({ importStyle: 'css' })],
            dts: './components.d.ts', // 仍需生成，供 WebStorm 识别
        }),
    ],
    build: {
      sourcemap: false,
    },
    resolve: {
        alias: {
            '@': fileURLToPath(new URL('./src', import.meta.url))
        },
    },

    server: {
        // 1. 必须监听 0.0.0.0 才能让外部访问
        host: '0.0.0.0',
        // 2. 动态获取端口：如果是 HF 环境则使用 7860，本地默认 5173
        port: process.env.PORT || 7860,
        // 3. 允许所有 HF 的域名访问，否则会报 "Invalid Host header"
        allowedHosts: [
            'data.xiaodu1234.xyz',
            'jokkad-danmu.hf.space',
            'jokkad-danmu-api.hf.space',
            '.xiaodu1234.xyz',
            '.hf.space',       // 允许所有 Hugging Face 子域名
            '.huggingface.co'  // 允许所有 Hugging Face 主站域名
        ],

    }
})
