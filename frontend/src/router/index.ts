import { createRouter, createWebHistory } from 'vue-router'
import FormView from '../views/FormView.vue'
import BaseLayout from '@/layouts/BaseLayout.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      component: BaseLayout,
      children: [
        {
          path: '',
          redirect() {
            return {
              name: 'synchronize',
            }
          },
        },
        {
          path: 'synchronize',
          name: 'synchronize',
          component: FormView,
        },
        {
          path: 'about',
          name: 'about',
          // route level code-splitting
          // this generates a separate chunk (About.[hash].js) for this route
          // which is lazy-loaded when the route is visited.
          component: () => import('../views/AboutView.vue'),
        },
      ],
    },
  ],
})

export default router
