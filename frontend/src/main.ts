import Aura from '@primevue/themes/aura'
import { createPinia } from 'pinia'
import PrimeVue from 'primevue/config'
import { createApp } from 'vue'
import App from './App.vue'
import './assets/main.css'
import router from './router'
import { createI18n } from 'vue-i18n'
import frMessages from './locales/fr.json'

function detectBrowserLanguage() {
  const availableLocales = ['en', 'fr']
  const browserLocale = navigator.language
  const normalizedLocale = browserLocale.split('-')[0]
  return availableLocales.includes(normalizedLocale) ? normalizedLocale : 'en'
}

const i18n = createI18n({
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
})

app.mount('#app')
