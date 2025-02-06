<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { RouterView } from 'vue-router'
import Menubar from 'primevue/menubar'
import { Select } from 'primevue'

const { t } = useI18n()

const menuItems = [
  { label: t('Synchronize'), icon: 'pi pi-sync', command: () => {} },
  { label: t('Operations log'), icon: 'pi pi-list', command: () => {} },
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
