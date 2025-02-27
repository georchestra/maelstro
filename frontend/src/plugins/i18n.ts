import { createI18n } from 'vue-i18n'
import frMessages from '@/locales/fr.json'

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
    en: Object.fromEntries(Object.keys(frMessages).map((key) => [key, key])),
    fr: frMessages,
  },
})

export default i18n
