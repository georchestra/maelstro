import { config } from '@vue/test-utils'
import PrimeVue from 'primevue/config'
import { createTestingPinia } from '@pinia/testing'
import { vi } from 'vitest'

vi.mock('vue-i18n', () => ({
  useI18n: vi.fn(() => ({
    t: vi.fn((tKey) => tKey),
  })),
}))

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
