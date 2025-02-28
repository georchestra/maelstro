import { logsService, type Log } from '@/services/logs.service'
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useLogsStore = defineStore('logs', () => {
  // State
  const logs = ref<Log[]>([])
  const total = ref(50)
  const limit = ref(20)
  const offset = ref(0)

  // Actions
  const fetchLogs = async (): Promise<void> => {
    const logsWithCount = await logsService.getLogs(limit.value, offset.value)
    total.value = logsWithCount.total
    logs.value = logsWithCount.logs
  }

  return {
    // State
    logs,
    total,
    limit,
    offset,

    // Actions
    fetchLogs,
  }
})
