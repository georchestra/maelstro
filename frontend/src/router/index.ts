import { createRouter, createWebHistory } from 'vue-router'
import FormView from '../views/FormView.vue'
import BaseLayout from '@/layouts/BaseLayout.vue'
import { useConfigStore } from '@/stores/config.store'
import LogsView from '@/views/LogsView.vue'
import { useLogsStore } from '@/stores/logs.store'

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
          beforeEnter: async () => {
            await useConfigStore().fetchConfig()
          },
        },
        {
          path: 'logs',
          name: 'logs',
          component: LogsView,
          beforeEnter: async () => {
            await useLogsStore().fetchLogs()
          },
        },
      ],
    },
  ],
})

export default router
