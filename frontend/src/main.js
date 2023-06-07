import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
// import { createPinia } from 'pinia'
import router from './router'

import VueApexCharts from "vue3-apexcharts";

// const pinia = createPinia()
const app = createApp(App)

// app.use(pinia)
app.use(router)
app.use(VueApexCharts);
app.mount('#app')
