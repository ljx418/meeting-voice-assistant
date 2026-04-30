import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../pages/HomePage.vue'
import AuthPage from '../pages/AuthPage.vue'
import MeetingPage from '../pages/MeetingPage.vue'
import MeetingConsolePage from '../pages/MeetingConsolePage.vue'
import GraphRAGPage from '../pages/GraphRAGPage.vue'
import WikiPage from '../pages/WikiPage.vue'
import WikiDetailPage from '../pages/WikiDetailPage.vue'
import WikiEditorPage from '../pages/WikiEditorPage.vue'
import KnowledgePage from '../pages/KnowledgePage.vue'
import InterviewPage from '../pages/InterviewPage.vue'
import InterviewSimulatePage from '../pages/InterviewSimulatePage.vue'
import InterviewReviewPage from '../pages/InterviewReviewPage.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomePage,
    },
    {
      path: '/auth',
      name: 'auth',
      component: AuthPage,
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
      path: '/interview',
      name: 'interview',
      component: InterviewPage,
    },
    {
      path: '/interview/simulate',
      name: 'interview-simulate',
      component: InterviewSimulatePage,
    },
    {
      path: '/interview/review',
      name: 'interview-review',
      component: InterviewReviewPage,
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
