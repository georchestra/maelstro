<script setup lang="ts">
import LogsReport from '@/components/LogsReport.vue'
import {
  datafeederService,
  type DatafeederInstance,
  type DatafeederIntegrityLink,
} from '@/services/datafeeder.service'
import type { SearchResult } from '@/services/geonetworkSearch.service'
import {
  synchronizeService,
  type CopyPreview,
  type CopyResponse,
  type SynchronizeParams,
} from '@/services/synchronize.service'
import { useConfigStore } from '@/stores/config.store'
import { useDatasetsStore } from '@/stores/datasets.store'
import { Form, FormField } from '@primevue/forms'
import {
  AutoComplete,
  Button,
  Checkbox,
  Message,
  Panel,
  ProgressSpinner,
  Select,
  ToggleSwitch,
  type AutoCompleteCompleteEvent,
} from 'primevue'
import { computed, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'

const includeHarvested = ref(false)
const confirmation = ref(false)

const configStore = useConfigStore()
const source = ref(configStore.sources.length ? configStore.sources[0] : undefined)

const errors = ref<Record<string, string>>({})

const { t } = useI18n()

const datasetsStore = useDatasetsStore()
const optionLabel = (option: SearchResult) => option.resourceTitleObject.default
const onComplete = (event: AutoCompleteCompleteEvent) => {
  if (source.value) {
    datasetsStore.search(source.value.name, event.query, includeHarvested.value)
  }
}
const selectedDataset = ref<SearchResult | null>(null)
const datafeederInstances = ref<DatafeederInstance[]>([])
const datafeederIntegrityLink = ref<DatafeederIntegrityLink | null>(null)
const checkingDatafeeder = ref(false)

onMounted(async () => {
  datafeederInstances.value = await datafeederService.getInstances()
})

const parameters = ref({
  src_name: source.value ? source.value.name : '',
  dst_name: configStore.destinations.length == 1 ? configStore.destinations[0].name : '',
  copy_meta: true,
  copy_layers: true,
  copy_styles: true,
  copy_data: false,
  dry_run: false,
})

watch(selectedDataset, async (dataset) => {
  parameters.value.copy_data = false
  datafeederIntegrityLink.value = null

  if (!dataset?.uuid || datafeederInstances.value.length === 0) {
    return
  }

  checkingDatafeeder.value = true
  try {
    datafeederIntegrityLink.value = await datafeederService.findByMetadataUuid(dataset.uuid)
  } finally {
    checkingDatafeeder.value = false
  }
})

watch(
  () => parameters.value.copy_data,
  (enabled) => {
    if (enabled) {
      parameters.value.copy_meta = true
      parameters.value.copy_layers = false
      parameters.value.copy_styles = false
    }
  },
)

const copyPreview = ref<CopyPreview>({
  geonetwork_resources: [],
  geoserver_resources: [],
})

const copyResponse = ref<CopyResponse | null>(null)

const synchronizeParams = computed(
  () =>
    ({
      ...parameters.value,
      metadataUuid: selectedDataset.value?.uuid,
    }) as unknown as SynchronizeParams,
)

const onFormSubmit = async () => {
  errors.value = {}
  if (!selectedDataset.value?.uuid) {
    errors.value.metadataUuid = t('Dataset is mandatory')
  }
  if (!parameters.value.dst_name) {
    errors.value.dst_name = t('Destination is mandatory')
  }
  if (Object.keys(errors.value).length) {
    return
  }

  try {
    copyPreview.value = await synchronizeService.getCopyPreview(synchronizeParams.value)
  } catch (error) {
    console.error(error)
  }

  confirmation.value = true
}

const isRunning = ref(false)

const confirm = async () => {
  isRunning.value = true
  const params = {
    ...parameters.value,
    metadataUuid: selectedDataset.value?.uuid,
  } as unknown as SynchronizeParams

  try {
    copyResponse.value = await synchronizeService.synchronize(params)
  } catch (error) {
    console.error(error)
  } finally {
    isRunning.value = false
  }
}

const logs = computed(() => copyPreview.value.operations || copyResponse.value?.operations || [])

const backToForm = () => {
  confirmation.value = false
  copyResponse.value = null
}

const metaLogs = computed(() => logs.value.filter((l) => l.data_type == 'Meta'))

const layerLogs = computed(() => logs.value.filter((l) => l.data_type == 'Layer'))

const styleLogs = computed(() => logs.value.filter((l) => l.data_type == 'Style'))
const datafeederLogs = computed(() => logs.value.filter((l) => l.data_type == 'Datafeeder'))

const metaSuccessful = computed(() => metaLogs.value.some((l) => l.status == 'OK'))
const layerSuccessful = computed(() => layerLogs.value.some((l) => l.status == 'OK'))
const styleSuccessful = computed(() => styleLogs.value.some((l) => l.status == 'OK'))
const datafeederSuccessful = computed(() => datafeederLogs.value.some((l) => l.status == 'OK'))
const metaFailed = computed(() => metaLogs.value.some((l) => l.status != 'OK'))
const layerFailed = computed(() => layerLogs.value.some((l) => l.status != 'OK'))
const styleFailed = computed(() => styleLogs.value.some((l) => l.status != 'OK'))

const hasMeta = computed(() =>
  copyPreview.value.geonetwork_resources?.some((gn) => gn.metadata.length > 0),
)
const hasLayers = computed(() =>
  copyPreview.value.geoserver_resources?.some((gs) => gs.layers.length > 0),
)
const hasStyles = computed(() =>
  copyPreview.value.geoserver_resources?.some((gs) => gs.styles.length > 0),
)

const success = computed(
  () =>
    (metaSuccessful.value ||
      layerSuccessful.value ||
      styleSuccessful.value ||
      datafeederSuccessful.value) &&
    (!hasMeta.value || metaSuccessful.value) &&
    (!hasLayers.value || layerSuccessful.value) &&
    (!hasStyles.value || styleSuccessful.value),
)
</script>

<template>
  <div class="my-12 w-4xl max-w-4xl mx-auto">
    <div class="text-4xl mb-10">
      {{ $t('Synchronization of datasets between platforms') }}
    </div>

    <div v-if="!confirmation">
      <Form class="flex flex-col gap-5" @submit="onFormSubmit">
        <div name="src_name" class="flex gap-5 items-center">
          <label for="src_name" class="w-36">{{ $t('Source platform') }}</label>
          <Select
            id="src_name"
            name="src_name"
            v-model="parameters.src_name"
            :options="configStore.sources.map((d) => d.name)"
            placeholder=""
            disabled
          />
          <Message v-if="errors.src_name" severity="error">{{ errors.src_name }}</Message>
        </div>

        <div class="flex gap-5 items-center">
          <label class="w-36 inline-block">&nbsp;</label>
          <label for="includeHarvested">{{ $t('Include harvested datasets') }}</label>
          <Checkbox inputId="includeHarvested" v-model="includeHarvested" binary />
        </div>

        <div class="flex flex-col gap-1">
          <div class="flex gap-5 items-center">
            <label for="metadataUuid" class="w-36">{{ $t('Source dataset') }}</label>
            <AutoComplete
              id="metadataUuid"
              v-model="selectedDataset"
              :suggestions="datasetsStore.results"
              :optionLabel="optionLabel"
              @complete="onComplete"
              size="large"
              scrollHeight="30rem"
              fluid
              class="grow"
              @update:model-value="delete errors.metadataUuid"
            />
            <Button icon="pi pi-delete-left" @click="selectedDataset = null" severity="secondary" />
            <Message v-if="errors.metadataUuid" class="min-w-[300px]" severity="error">{{
              errors.metadataUuid
            }}</Message>
          </div>
          <div class="ml-[164px]">
            <a
              v-if="selectedDataset?.uuid"
              :href="configStore.getMetadataUrl(source!, selectedDataset?.uuid)"
              target="_blank"
              class="text-blue-600 dark:text-blue-500 hover:underline"
              >{{ configStore.getMetadataUrl(source!, selectedDataset?.uuid) }}</a
            >
          </div>
          <div class="ml-[164px]">
            {{ selectedDataset?.resourceAbstractObject?.default }}
          </div>
        </div>
        <div name="dst_name" class="flex gap-5 items-center">
          <label for="dst_name" class="w-36">{{ $t('Target platform') }}</label>
          <Select
            id="dst_name"
            name="dst_name"
            v-model="parameters.dst_name"
            :options="configStore.destinations.map((d) => d.name)"
            placeholder=""
          />
          <Message v-if="errors.dst_name" severity="error">{{ errors.dst_name }}</Message>
        </div>
        <FormField name="copy_meta" class="flex gap-5 items-center">
          <label for="copy_meta" class="w-36">{{ $t('Metadata') }}</label>
          <ToggleSwitch
            id="copy_meta"
            placeholder=""
            v-model="parameters.copy_meta"
            :disabled="parameters.copy_data"
          />
        </FormField>
        <FormField name="copy_layers" class="flex gap-5 items-center">
          <label for="copy_layers" class="w-36">{{ $t('Layers') }}</label>
          <ToggleSwitch id="copy_layers" placeholder="" v-model="parameters.copy_layers" />
        </FormField>
        <FormField name="copy_styles" class="flex gap-5 items-center">
          <label for="copy_styles" class="w-36">{{ $t('Styles') }}</label>
          <ToggleSwitch id="copy_styles" placeholder="" v-model="parameters.copy_styles" />
        </FormField>
        <FormField
          v-if="datafeederInstances.length > 0"
          name="copy_data"
          class="flex gap-5 items-center"
        >
          <label for="copy_data" class="w-36">{{ $t('Import with Datafeeder') }}</label>
          <ToggleSwitch
            id="copy_data"
            placeholder=""
            v-model="parameters.copy_data"
            :disabled="checkingDatafeeder || !datafeederIntegrityLink"
          />
          <Message v-if="checkingDatafeeder" severity="secondary">
            {{ $t('Checking Datafeeder availability') }}
          </Message>
          <Message v-else-if="datafeederIntegrityLink" severity="success">
            {{ $t('Dataset found in Datafeeder') }}
          </Message>
          <Message v-else-if="selectedDataset" severity="warn">
            {{ $t('Dataset not found in Datafeeder') }}
          </Message>
        </FormField>
        <Button type="submit" :label="$t('Synchronize')" class="mt-5" />
      </Form>
    </div>

    <div v-else>
      <div>
        <div class="mt-4 font-semibold">
          {{ $t('Following data and metadata will be copied:') }}
        </div>

        <div
          v-if="parameters.copy_data && copyPreview.datafeeder"
          class="mt-4 p-4 border rounded shadow"
        >
          <div class="font-semibold">{{ $t('Datafeeder preview') }}</div>
          <div class="my-1">
            {{ $t('Integrity link:') }} {{ copyPreview.datafeeder.integrity_link_id }}
          </div>
          <div class="my-1">{{ $t('Import type:') }} {{ copyPreview.datafeeder.import_type }}</div>
          <div class="my-1">{{ $t('Table:') }} {{ copyPreview.datafeeder.table_name || '-' }}</div>
          <div class="my-1">{{ $t('Planned action:') }} {{ copyPreview.datafeeder.action }}</div>
          <LogsReport v-if="datafeederLogs.length" :logs="datafeederLogs"></LogsReport>
        </div>

        <div v-for="(geonetwork, index) in copyPreview.geonetwork_resources || []" :key="index">
          <div v-if="geonetwork.metadata.length > 0" class="mt-4 p-4 border rounded shadow">
            <div class="my-1">{{ $t('Source:') }} {{ geonetwork.src }}</div>
            <div class="my-1">{{ $t('Destination:') }} {{ geonetwork.dst }}</div>
            <Panel toggleable :collapsed="true">
              <template #header>
                <div>
                  <div class="my-1">
                    {{ $t('Metadata:') }}{{ metaSuccessful ? ' ✅' : metaFailed ? ' ❌' : '' }}
                  </div>
                  <ul v-for="(metadata, index) in geonetwork.metadata" :key="index">
                    <li class="list-disc ml-4">{{ metadata.title }}</li>
                  </ul>
                </div>
              </template>
              <LogsReport v-if="logs.length" :logs="metaLogs"></LogsReport>
            </Panel>
          </div>
        </div>

        <div v-for="(server, index) in copyPreview.geoserver_resources || []" :key="index">
          <div
            v-if="server.layers.length > 0 || server.styles.length > 0"
            class="mt-4 p-4 border rounded shadow"
          >
            <div class="my-1">{{ $t('Source:') }} {{ server.src }}</div>
            <div class="my-1">{{ $t('Destination:') }} {{ server.dst }}</div>
            <Panel v-if="server.layers.length > 0" toggleable :collapsed="true">
              <template #header>
                <div>
                  <div class="my-1">
                    {{ $t('Layers:') }}{{ layerSuccessful ? ' ✅' : layerFailed ? ' ❌' : '' }}
                  </div>
                  <ul v-for="layer in server.layers" :key="layer">
                    <li class="list-disc ml-4">{{ layer }}</li>
                  </ul>
                </div>
              </template>
              <LogsReport v-if="logs.length" :logs="layerLogs"></LogsReport>
            </Panel>
            <Panel v-if="server.styles.length > 0" toggleable :collapsed="true">
              <template #header>
                <div>
                  <div class="my-1">
                    {{ $t('Styles:') }}{{ styleSuccessful ? ' ✅' : styleFailed ? ' ❌' : '' }}
                  </div>
                  <ul v-for="style in server.styles" :key="style">
                    <li class="list-disc ml-4">{{ style }}</li>
                  </ul>
                </div>
              </template>
              <LogsReport v-if="logs.length" :logs="styleLogs"></LogsReport>
            </Panel>
          </div>
        </div>

        <div class="mt-4 flex justify-between items-center">
          <Button :label="$t('Go back to form')" severity="secondary" @click.stop="backToForm" />
          <ProgressSpinner v-if="isRunning" class="w-8 h-8" strokeWidth="8" fill="transparent" />
          <Button :label="$t('Confirm')" @click.stop="confirm" :disabled="isRunning" />
        </div>
      </div>

      <div class="mt-5" v-if="logs.length">
        <Panel toggleable :collapsed="true">
          <template #header>
            <div class="my-1">{{ success ? $t('Success') + ' ✅' : $t('Failure') + ' ❌' }}</div>
          </template>
          <div v-if="!success">
            <div v-if="copyPreview.info?.err">
              {{ copyPreview.info?.err }} [{{ copyPreview.info?.status_code }}]<br />
              {{ copyPreview.info?.server }}
            </div>
            <div v-else>
              {{ copyResponse?.info.err }} [{{ copyResponse?.info.status_code }}]<br />
              {{ copyResponse?.info.server }}
            </div>
          </div>
          <LogsReport :logs="logs"></LogsReport>
        </Panel>
      </div>
    </div>
  </div>
</template>
