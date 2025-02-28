<script setup lang="ts">
import type { LogDetail } from '@/services/logs.service'
import { Message } from 'primevue'
import { useI18n } from 'vue-i18n'

defineProps<{ logs: LogDetail[] }>()

useI18n()

const severity = (log: LogDetail) => {
  if (log.status_code) {
    if (log.status_code >= 200 && log.status_code < 400) {
      return 'success'
    } else {
      return 'error'
    }
  }
  return 'info'
}

const logMessage = (log: LogDetail) => {
  if (log.message) {
    return log.message
  }
  if (log.method) {
    return `${log.method} [${log.status_code}] ${log.url}`
  }
  return JSON.stringify(log)
}
</script>

<template>
  <div v-for="(log, index) in logs" :key="index">
    <Message :severity="severity(log)" class="my-2">{{ logMessage(log) }}</Message>
  </div>
</template>
