import { createRouter, createWebHistory } from 'vue-router'
import FormView from '../views/FormView.vue'
import BaseLayout from '@/layouts/BaseLayout.vue'
import { useConfigStore } from '@/stores/config.store'
import LogsView from '@/views/LogsView.vue'
import { useLogsStore } from '@/stores/logs.store'
import { useToastStore } from '@/stores/toast.store'
import i18n from '@/plugins/i18n'

const { t } = i18n.global

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
            try {
              await useConfigStore().fetchConfig()
            } catch {
              const toastStore = useToastStore()
              toastStore.addToast({
                severity: 'error',
                summary: t('Error'),
                detail: t('Failed to fetch configuration'),
                life: undefined,
              })
            }
          },
        },
        {
          path: 'logs',
          name: 'logs',
          component: LogsView,
          beforeEnter: async () => {
            try {
              await useLogsStore().fetchLogs()
            } catch {
              const toastStore = useToastStore()
              toastStore.addToast({
                severity: 'error',
                summary: t('Error'),
                detail: t('Failed to fetch logs'),
                life: undefined,
              })
            }
          },
        },
      ],
    },
  ],
})

export default router
