<script setup lang="ts">
import type { SearchResult } from '@/services/geonetworkSearch.service'
import { useConfigStore } from '@/stores/config.store'
import { useDatasetsStore } from '@/stores/datasets.store'
import { Form, FormField } from '@primevue/forms'
import {
  AutoComplete,
  Button,
  Select,
  ToggleSwitch,
  type AutoCompleteCompleteEvent,
} from 'primevue'
import { ref } from 'vue'

const configStore = useConfigStore()
const source = ref(configStore.sources[0])

const datasetsStore = useDatasetsStore()
const optionLabel = (option: SearchResult) => option.resourceTitleObject.default
const onComplete = (event: AutoCompleteCompleteEvent) =>
  datasetsStore.search(source.value.name, event.query)
const selectedDataset = ref<SearchResult | null>(null)

const parameters = ref({
  src_name: configStore.sources[0].name,
  dst_name: null,
  metadataUuid: null,
  copy_meta: true,
  copy_layers: true,
  copy_styles: true,
  dry_run: false,
})
</script>

<template>
  <div class="flex flex-col my-12 items-center">
    <div class="text-4xl text-gray-800 mb-10">
      {{ $t('Synchronization of datasets between platforms') }}
    </div>
    <Form class="flex flex-col gap-5">
      <FormField name="metadataUuid" class="flex gap-5 items-center">
        <label for="metadataUuid" class="w-36">{{ $t('Source dataset') }}</label>
        <AutoComplete
          id="metadataUuid"
          v-model="selectedDataset"
          :suggestions="datasetsStore.results"
          :optionLabel="optionLabel"
          @complete="onComplete"
        />
        <Button icon="pi pi-times" @click="selectedDataset = null" v-if="selectedDataset" />
        <p>{{ selectedDataset?.uuid }}</p>
      </FormField>
      <FormField name="dst_name" class="flex gap-5 items-center">
        <label for="dst_name" class="w-36">{{ $t('Target platform') }}</label>
        <Select
          id="dst_name"
          v-model="parameters.dst_name"
          :options="configStore.destinations.map((d) => d.name)"
          placeholder=""
        />
      </FormField>
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
      <Button :label="$t('Synchronize')" class="mt-5" />
    </Form>
  </div>
</template>
