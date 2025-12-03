import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'

// Element Plus 样式
import 'element-plus/dist/index.css'
// Element Plus 图标
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

// 全局样式
import './styles/index.scss'

// 修复mousewheel事件监听器的passive选项问题
import './utils/passiveEventListenerFix'

const app = createApp(App)
const pinia = createPinia()

// 注册Element Plus图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(pinia)
app.use(router)

app.mount('#app')