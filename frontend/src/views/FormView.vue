<script setup lang="ts">
import LogsReport from '@/components/LogsReport.vue'
import type { SearchResult } from '@/services/geonetworkSearch.service'
import {
  synchronizeService,
  type InvolvedResources,
  type Log,
  type SynchronizeParams,
} from '@/services/synchronize.service'
import { useConfigStore } from '@/stores/config.store'
import { useDatasetsStore } from '@/stores/datasets.store'
import { Form, FormField } from '@primevue/forms'
import {
  AutoComplete,
  Button,
  Message,
  Select,
  ToggleSwitch,
  type AutoCompleteCompleteEvent,
} from 'primevue'
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'

const confirmation = ref(false)

const configStore = useConfigStore()
const source = ref(configStore.sources[0])

const errors = ref<Record<string, string>>({})

const { t } = useI18n()

const datasetsStore = useDatasetsStore()
const optionLabel = (option: SearchResult) => option.resourceTitleObject.default
const onComplete = (event: AutoCompleteCompleteEvent) =>
  datasetsStore.search(source.value.name, event.query)
const selectedDataset = ref<SearchResult | null>(null)

const parameters = ref({
  src_name: source.value.name,
  dst_name: '',
  copy_meta: true,
  copy_layers: true,
  copy_styles: true,
  dry_run: false,
})

const involvedResources = ref<InvolvedResources>({
  metadata: [],
  data: [],
})

const logs = ref<Log[]>([])

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
    involvedResources.value = await synchronizeService.getInvolvedResources(synchronizeParams.value)
  } catch (error) {
    console.error(error)
  }

  confirmation.value = true
}

const confirm = async () => {
  const params = {
    ...parameters.value,
    metadataUuid: selectedDataset.value?.uuid,
  } as unknown as SynchronizeParams

  logs.value = await synchronizeService.synchronize(params)
}

const backToForm = () => {
  confirmation.value = false
  logs.value = []
}
</script>

<template>
  <div class="flex flex-col my-12 items-center">
    <div class="text-4xl mb-10">
      {{ $t('Synchronization of datasets between platforms') }}
    </div>

    <div v-if="!confirmation">
      <Form class="flex flex-col gap-5" @submit="onFormSubmit">
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
            />
            <Button icon="pi pi-delete-left" @click="selectedDataset = null" severity="secondary" />
            <Message v-if="errors.metadataUuid" class="min-w-[300px]" severity="error">{{
              errors.metadataUuid
            }}</Message>
            <p v-if="!errors.metadataUuid" class="min-w-[300px]">{{ selectedDataset?.uuid }}</p>
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
          <ToggleSwitch id="copy_meta" placeholder="" v-model="parameters.copy_meta" />
        </FormField>
        <FormField name="copy_layers" class="flex gap-5 items-center">
          <label for="copy_layers" class="w-36">{{ $t('Layers') }}</label>
          <ToggleSwitch id="copy_layers" placeholder="" v-model="parameters.copy_layers" />
        </FormField>
        <FormField name="copy_styles" class="flex gap-5 items-center">
          <label for="copy_styles" class="w-36">{{ $t('Styles') }}</label>
          <ToggleSwitch id="copy_styles" placeholder="" v-model="parameters.copy_styles" />
        </FormField>
        <Button type="submit" :label="$t('Synchronize')" class="mt-5" />
      </Form>
    </div>

    <div v-else>
      <div class="w-[600px] mx-auto">
        <div class="mt-4 font-semibold">Les données suivantes seront synchronisées :</div>

        <div
          class="mt-4 p-4 border rounded shadow"
          v-for="(geonetwork, index) in involvedResources.metadata"
          :key="index"
        >
          <div class="my-1">{{ $t('Source:') }} {{ geonetwork.src }}</div>
          <div class="my-1">{{ $t('Destination:') }} {{ geonetwork.dst }}</div>
          <div class="my-1">{{ $t('Metadata:') }}</div>
          <ul v-for="(metadata, index) in geonetwork.metadata" :key="index">
            <li class="list-disc ml-4">{{ metadata.title }}</li>
          </ul>
        </div>

        <div
          class="mt-4 p-4 border rounded shadow"
          v-for="(server, index) in involvedResources.data"
          :key="index"
        >
          <div class="my-1">{{ $t('Source:') }} {{ server.src }}</div>
          <div class="my-1">{{ $t('Destination:') }} {{ server.dst }}</div>
          <div class="my-1">{{ $t('Layers:') }}</div>
          <ul v-for="layer in server.layers" :key="layer">
            <li class="list-disc ml-4">{{ layer }}</li>
          </ul>
          <div class="my-1">{{ $t('Styles:') }}</div>
          <ul v-for="style in server.styles" :key="style">
            <li class="list-disc ml-4">{{ style }}</li>
          </ul>
        </div>

        <div class="mt-4 flex justify-between">
          <Button :label="$t('Go back to form')" severity="secondary" @click.stop="backToForm" />
          <Button :label="$t('Confirm')" @click.stop="confirm" />
        </div>
      </div>

      <div class="m-5">
        <LogsReport v-if="logs.length" :logs="logs"></LogsReport>
      </div>
    </div>
  </div>
</template>
