<script setup lang="ts">
import { Form, FormField } from '@primevue/forms'
import { Button } from 'primevue'
import InputText from 'primevue/inputtext'
</script>

<template>
  <div class="flex flex-col my-12 items-center">
    <div class="text-4xl text-gray-800 mb-10">
      {{ $t('Synchronization of datasets between platforms') }}
    </div>
    <Form class="flex flex-col gap-5">
      <FormField name="sourceDataset" class="flex gap-5 items-center">
        <label for="sourceDataset" class="w-36">{{ $t('Source dataset') }}</label>
        <InputText id="sourceDataset" placeholder="" />
      </FormField>
      <FormField name="sourceLayer" class="flex gap-5 items-center">
        <label for="sourceLayer" class="w-36">{{ $t('Source layer') }}</label>
        <InputText id="sourceLayer" placeholder="" />
      </FormField>
      <FormField name="targetPlatform" class="flex gap-5 items-center">
        <label for="targetPlatform" class="w-36">{{ $t('Target platform') }}</label>
        <InputText id="targetPlatform" placeholder="" />
      </FormField>
      <Button :label="$t('Synchronize')" class="mt-5" />
    </Form>
  </div>
</template>
