import { createRouter, createWebHistory } from 'vue-router'
import ContextList from '@/views/ContextList.vue'
import ContextDetail from '@/views/ContextDetail.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'context-list',
      component: ContextList
    },
    {
      path: '/context/:id',
      name: 'context-detail',
      component: ContextDetail,
      props: true
    }
  ]
})

export default router
