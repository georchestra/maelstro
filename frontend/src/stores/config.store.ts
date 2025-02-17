import { configService, type Destination, type Source } from '@/services/config.service'
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useConfigStore = defineStore('config', () => {
  // State
  const sources = ref<Source[]>([])
  const destinations = ref<Destination[]>([])

  // Actions
  const fetchConfig = async (): Promise<void> => {
    const sourcesPromise = configService.getSources()
    const destinationsPromise = configService.getDestinations()

    sources.value = await sourcesPromise
    destinations.value = await destinationsPromise
  }

  // Getters
  const getSourceByName = (name: string): Source | undefined => {
    return sources.value.find((source) => source.name === name)
  }

  return {
    // State
    sources,
    destinations,

    // Actions
    fetchConfig,
    getSourceByName,
  }
})
