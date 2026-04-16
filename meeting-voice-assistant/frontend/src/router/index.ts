import { createRouter, createWebHistory } from 'vue-router'
import MeetingPage from '../pages/MeetingPage.vue'
import MeetingConsolePage from '../pages/MeetingConsolePage.vue'
import GraphRAGPage from '../pages/GraphRAGPage.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'meeting',
      component: MeetingPage,
    },
    {
      path: '/console',
      name: 'console',
      component: MeetingConsolePage,
    },
    {
      path: '/graphrag',
      name: 'graphrag',
      component: GraphRAGPage,
    },
  ],
})

export default router
