<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { RouterView, useRouter } from 'vue-router'
import Menubar from 'primevue/menubar'
import { Select, Toast, useToast } from 'primevue'
import { useToastStore } from '@/stores/toast.store'
import { computed, onMounted, watch } from 'vue'

const { t } = useI18n()
const router = useRouter()

const menuItems = computed(() => [
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
  // { label: t('User guide'), icon: 'pi pi-book' },
])

const toastStore = useToastStore()
const toast = useToast()

const loadToastMessages = () => {
  if (toastStore.messages.length > 0) {
    toastStore.messages.forEach((msg) => toast.add(msg))
    toastStore.messages = []
  }
}
onMounted(loadToastMessages)

watch(
  () => toastStore.messages,
  () => loadToastMessages,
)
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
  <Toast />
</template>
