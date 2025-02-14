<script setup lang="ts">
import type { LogDetail } from '@/services/logs.service'

defineProps<{ logs: LogDetail[] }>()

const logClass = (log: LogDetail) => {
  if (log.status_code) {
    if (log.status_code >= 200 && log.status_code < 300) {
      return 'log-success'
    } else {
      return 'log-error'
    }
  }
  return 'log-info'
}

const logMessage = (log: LogDetail) => {
  if (log.message) {
    return log.message
  }
  if (log.operation) {
    return log.operation
  }
  if (log.method) {
    return log.method + ' ' + log.url
  }
  return JSON.stringify(log)
}
</script>

<template>
  <div class="my-5 font-semibold">{{ $t('Details') }}</div>
  <div v-for="(log, index) in logs" :key="index">
    <div :class="logClass(log)">{{ logMessage(log) }}</div>
  </div>
</template>

<style scoped>
.log-info {
  background-color: #e0f7fa; /* Bleu clair */
  border-left: 5px solid #039be5;
  padding: 10px;
  margin-bottom: 5px;
  border-radius: 5px;
}

.log-success {
  background-color: #e8f5e9; /* Vert pâle */
  border-left: 5px solid #43a047; /* Bordure vert plus foncé */
  padding: 10px;
  margin-bottom: 5px;
  border-radius: 5px;
}

.log-error {
  background-color: #ffebee; /* Rouge clair */
  border-left: 5px solid #d32f2f;
  padding: 10px;
  margin-bottom: 5px;
  border-radius: 5px;
}
</style>
