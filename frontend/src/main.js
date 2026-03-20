/** 前端入口：Pinia、路由、Element Plus 与全局样式。 */
import { createApp } from "vue";
import { createPinia } from "pinia";
import router from "./router";
import App from "./App.vue";

import "element-plus/dist/index.css";
import "element-plus/theme-chalk/dark/css-vars.css";
import * as ElementPlusIconsVue from "@element-plus/icons-vue";

import "./styles/index.scss";
import "./utils/passiveEventListenerFix";

const app = createApp(App);
const pinia = createPinia();

for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component);
}

app.use(pinia);
app.use(router);

app.mount("#app");
