import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import FormView from '../FormView.vue'
import { useConfigStore } from '@/stores/config.store'

describe('FormView', () => {
  beforeEach(() => {
    const configStore = useConfigStore()
    configStore.sources = [{ name: 'src', url: 'https://localhost/geonetwork/' }]
    configStore.destinations = [
      {
        name: 'dest',
        gs_url: 'https://localhost/geoserver/',
        gn_url: 'https://localhost/geonetwork/',
      },
    ]
  })

  it('renders properly', () => {
    const wrapper = mount(FormView)
    expect(wrapper.text()).toContain('Synchronization of datasets between platforms')
  })
})
