import type { Config } from 'tailwindcss'
import tailwindcssPrimeUI from 'tailwindcss-primeui'

export default {
  content: ['./src/**/*.vue'],
  theme: {
    extend: {},
  },
  plugins: [tailwindcssPrimeUI],
} satisfies Config
