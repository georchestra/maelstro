import { config } from '@vue/test-utils'
import PrimeVue from 'primevue/config'
import { createTestingPinia } from '@pinia/testing'
import { vi } from 'vitest'

Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation((query) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
})

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
