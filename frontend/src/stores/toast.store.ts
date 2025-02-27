import { defineStore } from 'pinia'
import type { ToastMessageOptions } from 'primevue'
import { ref } from 'vue'

export const useToastStore = defineStore('toast', () => {
  /*
  Store toast messages between beforeEnter and component setup.
  */
  const messages = ref<ToastMessageOptions[]>([])

  const addToast = (message: ToastMessageOptions) => {
    messages.value.push(message)
  }

  return { messages, addToast }
})
