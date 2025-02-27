import Aura from '@primevue/themes/aura'
import { createPinia } from 'pinia'
import PrimeVue, { type PrimeVueLocaleOptions } from 'primevue/config'
import { createApp } from 'vue'
import App from './App.vue'
import './assets/main.css'
import router from './router'
import primeEnMessages from 'primelocale/en.json'
import primeFrMessages from 'primelocale/fr.json'
import 'primeicons/primeicons.css'
import { ToastService } from 'primevue'
import i18n from '@/plugins/i18n'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(i18n)

const primeLocales = {
  en: primeEnMessages.en as unknown as PrimeVueLocaleOptions,
  fr: primeFrMessages.fr as unknown as PrimeVueLocaleOptions,
}

app.use(PrimeVue, {
  theme: {
    preset: Aura,
    options: {
      cssLayer: {
        name: 'primevue',
        order: 'tailwind-base, primevue, tailwind-utilities',
      },
    },
  },
  locale: primeLocales[i18n.global.locale.value],
})
app.use(ToastService)

app.mount('#app')
