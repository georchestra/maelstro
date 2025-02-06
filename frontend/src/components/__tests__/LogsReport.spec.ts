import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import LogsReport from '../LogsReport.vue'

describe('LogsReport', () => {
  it('renders properly', () => {
    const wrapper = mount(LogsReport, {
      props: {
        logs: [
          {
            operation: 'Test operation',
            url: 'https://demo.georchestra.org/geonetwork/srv/api',
            context: 'source',
            service_type: 'geonetwork',
          },
        ],
      },
    })
    expect(wrapper.text()).toContain('Test operation')
  })
})
