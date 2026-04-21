import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../pages/HomePage.vue'
import MeetingPage from '../pages/MeetingPage.vue'
import MeetingConsolePage from '../pages/MeetingConsolePage.vue'
import GraphRAGPage from '../pages/GraphRAGPage.vue'
import WikiPage from '../pages/WikiPage.vue'
import WikiDetailPage from '../pages/WikiDetailPage.vue'
import WikiEditorPage from '../pages/WikiEditorPage.vue'
import KnowledgePage from '../pages/KnowledgePage.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomePage,
    },
    {
      path: '/meeting',
      name: 'meeting',
      component: MeetingPage,
    },
    {
      path: '/console',
      name: 'console',
      component: MeetingConsolePage,
    },
    {
      path: '/console/:sessionId',
      name: 'console-session',
      component: MeetingConsolePage,
    },
    {
      path: '/knowledge',
      name: 'knowledge',
      component: KnowledgePage,
    },
    {
      path: '/graphrag',
      name: 'graphrag',
      component: GraphRAGPage,
    },
    {
      path: '/wiki',
      name: 'wiki',
      component: WikiPage,
    },
    {
      path: '/wiki/new',
      name: 'wiki-new',
      component: WikiEditorPage,
    },
    {
      path: '/wiki/:id',
      name: 'wiki-detail',
      component: WikiDetailPage,
    },
    {
      path: '/wiki/:id/edit',
      name: 'wiki-edit',
      component: WikiEditorPage,
    },
  ],
})

export default router
