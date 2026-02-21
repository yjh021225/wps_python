import { createApp } from 'vue'
import App from './App.vue'
import router from './router' // 引入我们写好的路由
import ElementPlus from 'element-plus' // 引入 UI 组件库
import 'element-plus/dist/index.css' // 引入 UI 组件库的样式
import * as ElementPlusIconsVue from '@element-plus/icons-vue' // 引入图标库

const app = createApp(App)

// 注册 Element Plus 的所有图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 最关键的一步：告诉 Vue 使用路由和 Element Plus
app.use(router)
app.use(ElementPlus)

app.mount('#app')