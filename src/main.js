import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import './style.css'

const EmptyRoute = { render: () => null }
const router = createRouter({
  history: createWebHistory(),
  scrollBehavior: () => ({ top: 0 }),
  routes: [
    { path: '/:pathMatch(.*)*', component: EmptyRoute },
  ],
})

createApp(App).use(router).mount('#app')
