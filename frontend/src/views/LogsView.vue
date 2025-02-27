<script setup lang="ts">
import LogsReport from '@/components/LogsReport.vue'
import type { Log } from '@/services/logs.service'
import { useLogsStore } from '@/stores/logs.store'
import { Column, DataTable, Tag } from 'primevue'
import { ref } from 'vue'

const logsStore = useLogsStore()

const getSeverity = (log: Log) => {
  if (log.status_code >= 200 && log.status_code < 300) {
    return 'success'
  } else {
    return 'danger'
  }
}

const expandedRows = ref({})
</script>

<template>
  <div class="flex flex-col">
    <DataTable
      :value="logsStore.logs"
      tableStyle="min-width: 50rem"
      size="small"
      selectionMode="single"
      v-model:expandedRows="expandedRows"
      dataKey="id"
    >
      <Column expander></Column>
      <Column field="id" :header="$t('id')"></Column>
      <Column field="start_time" :header="$t('Start time')">
        <template #body="slotProps">
          {{
            slotProps.data.start_time.toLocaleString('fr-FR', {
              dateStyle: 'short',
              timeStyle: 'short',
            })
          }}
        </template>
      </Column>
      <!--<Column field="end_time" header="End time"></Column>-->
      <Column field="start_time" :header="$t('User')">
        <template #body="slotProps">
          {{ slotProps.data.first_name }}
          {{ slotProps.data.last_name }}
        </template>
      </Column>
      <Column field="status_code" :header="$t('Status code')">
        <template #body="slotProps">
          <Tag :value="slotProps.data.status_code" :severity="getSeverity(slotProps.data)">{{
            slotProps.data.status_code
          }}</Tag>
        </template>
      </Column>
      <Column field="src_name" :header="$t('Source')"></Column>
      <Column field="dst_name" :header="$t('Destination')"></Column>
      <Column field="src_title" :header="$t('Source title')">
        <template #body="slotProps">
          <div
            class="max-w-60 overflow-hidden text-ellipsis whitespace-nowrap"
            :title="slotProps.data.src_title"
          >
            {{ slotProps.data.src_title }}
          </div>
        </template>
      </Column>
      <!--<Column field="src_title" :header="$t('Destination title')"></Column>-->
      <Column field="copy_meta" :header="$t('Metadata')"></Column>
      <Column field="copy_layers" :header="$t('Layers')"></Column>
      <Column field="copy_styles" :header="$t('Styles')"></Column>
      <template #expansion="slotProps">
        <div class="p-4">
          <LogsReport :logs="slotProps.data.details" />
        </div>
      </template>
    </DataTable>
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
