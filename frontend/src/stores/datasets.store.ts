import { defineStore } from 'pinia'
import { geonetworkSearchService, type SearchResult } from '@/services/geonetworkSearch.service'
import { ref } from 'vue'

export const useDatasetsStore = defineStore('datasets', () => {
  // State
  const results = ref<SearchResult[]>([])
  const loading = ref(false)

  // Actions
  const search = async (sourceName: string, query: string): Promise<void> => {
    loading.value = true
    results.value = (await geonetworkSearchService.search(sourceName, query)) || []
    loading.value = false
  }

  return {
    // State
    results,
    loading,

    // Actions
    search,
  }
})
