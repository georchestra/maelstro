<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { RouterView, useRouter } from 'vue-router'
import Menubar from 'primevue/menubar'
import { Select } from 'primevue'

const { t } = useI18n()
const router = useRouter()

const menuItems = [
  {
    label: t('Synchronize'),
    icon: 'pi pi-sync',
    url: router.resolve({ name: 'synchronize' }).href,
  },
  {
    label: t('Operations log'),
    icon: 'pi pi-list',
    url: router.resolve({ name: 'logs' }).href,
  },
  { label: t('User guide'), icon: 'pi pi-book', command: () => {} },
]
</script>

<template>
  <Menubar :model="menuItems">
    <template #end>
      <Select :options="$i18n.availableLocales" v-model="$i18n.locale"></Select>
    </template>
  </Menubar>
  <main>
    <RouterView />
  </main>
</template>
