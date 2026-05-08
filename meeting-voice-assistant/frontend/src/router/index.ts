import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../pages/HomePage.vue'
import AuthPage from '../pages/AuthPage.vue'
import MeetingPage from '../pages/MeetingPage.vue'
import MeetingConsolePage from '../pages/MeetingConsolePage.vue'
import InterviewPage from '../pages/InterviewPage.vue'
import InterviewSimulatePage from '../pages/InterviewSimulatePage.vue'
import InterviewReviewPage from '../pages/InterviewReviewPage.vue'

const KNOWLEDGE_CONSOLE_URL = import.meta.env.VITE_DATA_SERVICE_CONSOLE_URL || 'http://127.0.0.1:8003/knowledge'
const ExternalRedirectPage = { template: '' }

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
      component: ExternalRedirectPage,
      beforeEnter: () => {
        window.location.href = KNOWLEDGE_CONSOLE_URL
        return false
      },
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
  ],
})

export default router
