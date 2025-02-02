import { config } from '@vue/test-utils'
import PrimeVue from 'primevue/config'
import { createTestingPinia } from '@pinia/testing'
import { vi } from 'vitest'

config.global.mocks = {
  $t: (key: string) => key,
}

config.global.plugins = [
  PrimeVue,
  createTestingPinia({
    createSpy: vi.fn, // spy with vitest
    stubActions: false,
  }),
]
