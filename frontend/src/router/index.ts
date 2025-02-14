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
      ],
    },
  ],
})

export default router
