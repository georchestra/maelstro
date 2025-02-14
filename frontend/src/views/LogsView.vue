<script setup lang="ts">
import LogsReport from '@/components/LogsReport.vue'
import type { Log } from '@/services/logs.service'
import { useLogsStore } from '@/stores/logs.store'
import { Column, DataTable, Tag } from 'primevue'
import { ref } from 'vue'

const logsStore = useLogsStore()

const selectedLog = ref<Log | null>(null)

const getSeverity = (log: Log) => {
  if (log.status_code >= 200 && log.status_code < 300) {
    return 'success'
  } else {
    return 'danger'
  }
}
</script>

<template>
  <div class="flex flex-col gap-5 items-center">
    <DataTable
      :value="logsStore.logs"
      tableStyle="min-width: 50rem"
      size="small"
      selectionMode="single"
      v-model:selection="selectedLog"
    >
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
      <Column field="src_title" :header="$t('Title')"></Column>
      <Column field="copy_meta" :header="$t('Metadata')"></Column>
      <Column field="copy_layers" :header="$t('Layers')"></Column>
      <Column field="copy_styles" :header="$t('Styles')"></Column>
    </DataTable>
    <div v-if="selectedLog" class="m-5">
      <div class="flex flex-col gap-1">
        <div class="flex flex-row gap-5">
          <div>id:</div>
          <div>{{ selectedLog.id }}</div>
        </div>
        <div class="flex flex-row gap-5">
          <div>start_time:</div>
          <div>
            {{
              selectedLog.start_time.toLocaleString('fr-FR', {
                dateStyle: 'short',
                timeStyle: 'short',
              })
            }}
          </div>
        </div>
        <div class="flex flex-row gap-5">
          <div>end_time:</div>
          <div>
            {{
              selectedLog.end_time.toLocaleString('fr-FR', {
                dateStyle: 'short',
                timeStyle: 'short',
              })
            }}
          </div>
        </div>
        <div class="flex flex-row gap-5">
          <div>last_name:</div>
          <div>
            {{ selectedLog.last_name }}
          </div>
        </div>
        <div class="flex flex-row gap-5">
          <div>status_code:</div>
          <div>
            {{ selectedLog.status_code }}
          </div>
        </div>
        <div class="flex flex-row gap-5">
          <div>src_name:</div>
          <div>
            {{ selectedLog.src_name }}
          </div>
        </div>
        <div class="flex flex-row gap-5">
          <div>dataset_uuid:</div>
          <div>
            {{ selectedLog.dataset_uuid }}
          </div>
        </div>
        <div class="flex flex-row gap-5">
          <div>src_title:</div>
          <div>
            {{ selectedLog.src_title }}
          </div>
        </div>
        <div class="flex flex-row gap-5">
          <div>dst_title:</div>
          <div>
            {{ selectedLog.dst_title }}
          </div>
        </div>
        <div class="flex flex-row gap-5">
          <div>copy_meta:</div>
          <div>
            {{ selectedLog.copy_meta }}
          </div>
        </div>
        <div class="flex flex-row gap-5">
          <div>copy_layers:</div>
          <div>
            {{ selectedLog.copy_layers }}
          </div>
        </div>
        <div class="flex flex-row gap-5">
          <div>copy_styles:</div>
          <div>
            {{ selectedLog.copy_styles }}
          </div>
        </div>
      </div>
      <LogsReport :logs="selectedLog?.details" />
    </div>
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
