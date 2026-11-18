import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import FormView from '../FormView.vue'
import { useConfigStore } from '@/stores/config.store'
import { ToggleSwitch } from 'primevue'
import { nextTick } from 'vue'

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

  it('requires and locks all synchronization options when Datafeeder is enabled', async () => {
    const wrapper = mount(FormView)
    const vm = wrapper.vm as unknown as {
      parameters: {
        copy_meta: boolean
        copy_layers: boolean
        copy_styles: boolean
        copy_data: boolean
      }
    }

    vm.parameters.copy_meta = false
    vm.parameters.copy_layers = false
    vm.parameters.copy_styles = false
    vm.parameters.copy_data = true
    await nextTick()

    expect(vm.parameters).toMatchObject({
      copy_meta: true,
      copy_layers: true,
      copy_styles: true,
      copy_data: true,
    })
    const synchronizationOptions = wrapper.findAllComponents(ToggleSwitch).slice(0, 3)
    expect(synchronizationOptions.every((option) => option.props('disabled'))).toBe(true)
  })
})
