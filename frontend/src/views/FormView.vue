<script setup lang="ts">
import { Form, FormField } from '@primevue/forms'
import { Button, ToggleSwitch } from 'primevue'
import InputText from 'primevue/inputtext'
import { ref } from 'vue'

const parameters = ref({
  sourceDataset: null,
  targetPlatform: null,
  contentMetadata: true,
  contentLayers: true,
  contentStyles: true,
})
</script>

<template>
  <div class="flex flex-col my-12 items-center">
    <div class="text-4xl text-gray-800 mb-10">
      {{ $t('Synchronization of datasets between platforms') }}
    </div>
    <Form class="flex flex-col gap-5">
      <FormField name="sourceDataset" class="flex gap-5 items-center">
        <label for="sourceDataset" class="w-36">{{ $t('Source dataset') }}</label>
        <InputText id="sourceDataset" placeholder="" v-model="parameters.sourceDataset" />
      </FormField>
      <FormField name="targetPlatform" class="flex gap-5 items-center">
        <label for="targetPlatform" class="w-36">{{ $t('Target platform') }}</label>
        <InputText id="targetPlatform" placeholder="" v-model="parameters.targetPlatform" />
      </FormField>
      <FormField name="contentMetadata" class="flex gap-5 items-center">
        <label for="contentMetadata" class="w-36">{{ $t('Metadata') }}</label>
        <ToggleSwitch id="contentMetadata" placeholder="" v-model="parameters.contentMetadata" />
      </FormField>
      <FormField name="contentLayers" class="flex gap-5 items-center">
        <label for="contentLayers" class="w-36">{{ $t('Layers') }}</label>
        <ToggleSwitch id="contentLayers" placeholder="" v-model="parameters.contentLayers" />
      </FormField>
      <FormField name="contentStyles" class="flex gap-5 items-center">
        <label for="contentStyles" class="w-36">{{ $t('Styles') }}</label>
        <ToggleSwitch id="contentStyles" placeholder="" v-model="parameters.contentStyles" />
      </FormField>
      <Button :label="$t('Synchronize')" class="mt-5" />
    </Form>
  </div>
</template>
