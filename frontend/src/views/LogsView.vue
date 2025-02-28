<script setup lang="ts">
import LogsReport from '@/components/LogsReport.vue'
import type { Log } from '@/services/logs.service'
import { useLogsStore } from '@/stores/logs.store'
import { Column, DataTable, Paginator, Tag } from 'primevue'
import { ref } from 'vue'

const logsStore = useLogsStore()

const getSeverity = (log: Log) => {
  if (log.status_code >= 200 && log.status_code < 300) {
    return 'success'
  } else {
    return 'danger'
  }
}

const onFirstChange = (value: number) => {
  logsStore.offset = value
  logsStore.fetchLogs()
}

const onRowsChange = (value: number) => {
  logsStore.limit = value
  logsStore.fetchLogs()
}

const expandedRows = ref({})
</script>

<template>
  <Paginator
    :rows="logsStore.limit"
    :totalRecords="120"
    :rowsPerPageOptions="[10, 20, 50, 100]"
    @update:rows="onRowsChange"
    @update:first="onFirstChange"
  ></Paginator>
  <DataTable
    :value="logsStore.logs"
    tableStyle="min-width: 50rem"
    size="small"
    selectionMode="single"
    v-model:expandedRows="expandedRows"
    dataKey="id"
  >
    <Column expander field="id" :header="$t('id')"></Column>
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
</template>
