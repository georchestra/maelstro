<script setup lang="ts">
import type { LogDetail } from '@/services/logs.service'

defineProps<{ logs: LogDetail[] }>()

const logClass = (status_code: number) => {
  if (status_code >= 200 && status_code < 300) {
    return 'log-success'
  } else {
    return 'log-error'
  }
}
</script>

<template>
  <div class="mb-4 font-semibold">Details</div>
  <div v-for="(log, index) in logs" :key="index">
    <div v-if="['POST', 'PUT'].includes(log.method!)" :class="logClass(log.status_code!)">
      {{ log.method }} {{ log.url }}
    </div>
    <div v-if="log.operation" class="log-info">{{ log.operation }}</div>
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
