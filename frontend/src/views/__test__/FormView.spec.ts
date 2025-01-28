import { describe, it, expect } from 'vitest'

import { mount } from '@vue/test-utils'
import FormView from '../FormView.vue'

describe('FormView', () => {
  it('renders properly', () => {
    const wrapper = mount(FormView)
    expect(wrapper.text()).toContain('Synchronization of datasets between platforms')
  })
})
