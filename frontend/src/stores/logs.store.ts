import { logsService, type Log } from '@/services/logs.service'
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useLogsStore = defineStore('logs', () => {
  // State
  const logs = ref<Log[]>([])

  // Actions
  const fetchLogs = async (): Promise<void> => {
    logs.value = await logsService.getLogs()
  }

  return {
    // State
    logs,

    // Actions
    fetchLogs,
  }
})
