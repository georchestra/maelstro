import { logsService, type Log } from '@/services/logs.service'
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useLogsStore = defineStore('logs', () => {
  // State
  const logs = ref<Log[]>([])
  const limit = ref(100)
  const offset = ref(0)

  // Actions
  const fetchLogs = async (): Promise<void> => {
    logs.value = await logsService.getLogs(limit.value, offset.value)
  }

  return {
    // State
    logs,
    limit,
    offset,

    // Actions
    fetchLogs,
  }
})
