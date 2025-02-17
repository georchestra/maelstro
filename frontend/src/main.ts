import Aura from '@primevue/themes/aura'
import { createPinia } from 'pinia'
import PrimeVue, { type PrimeVueLocaleOptions } from 'primevue/config'
import { createApp } from 'vue'
import App from './App.vue'
import './assets/main.css'
import router from './router'
import { createI18n } from 'vue-i18n'
import frMessages from './locales/fr.json'
import primeEnMessages from 'primelocale/en.json'
import primeFrMessages from 'primelocale/fr.json'
import 'primeicons/primeicons.css'

function detectBrowserLanguage() {
  const availableLocales = ['en', 'fr']
  const browserLocale = navigator.language
  const normalizedLocale = browserLocale.split('-')[0]
  return availableLocales.includes(normalizedLocale) ? normalizedLocale : 'en'
}

const i18n = createI18n({
  legacy: false,
  locale: detectBrowserLanguage(),
  fallbackLocale: 'en',
  messages: {
    en: {},
    fr: frMessages,
  },
})

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

app.mount('#app')
