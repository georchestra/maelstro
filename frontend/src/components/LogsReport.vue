<script setup lang="ts">
import type { Log } from '@/services/synchronize.service'

defineProps<{ logs: Log[] }>()

const logClass = (service_type: string) => {
  switch (service_type) {
    case 'geoserver':
      return 'log-info'
    case 'geonetwork':
      return 'log-warning'
  }
  // return {
  //   'log-info': level === 'info',
  //   'log-warning': level === 'warning',
  //   'log-error': level === 'error',
  // }

  // return {
  //   'log-info': level === 'info',
  //   'log-warning': level === 'warning',
  //   'log-error': level === 'error',
  // }
}

// const logClass = (service_type: string) => {
//   switch (service_type) {
//     case 'geonetwork':
//       return 'log-info'
//     case 'geoserver':
//       return 'log-warning'
//     case 'geoserver_style':
//       return 'log-error'
//     default:
//       return 'log-info'
//   }
// }
</script>

<template>
  <div v-for="(log, index) in logs" :key="index" :class="logClass(log.service_type)">
    {{ log.operation }}
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

.log-warning {
  background-color: #fff3cd; /* Jaune */
  border-left: 5px solid #ffa000;
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
