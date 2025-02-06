import { config } from '@vue/test-utils'
import PrimeVue from 'primevue/config'

config.global.mocks = {
  $t: (key: string) => key,
}

config.global.plugins = [PrimeVue]
