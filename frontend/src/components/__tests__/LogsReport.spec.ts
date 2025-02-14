import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import LogsReport from '../LogsReport.vue'

describe('LogsReport', () => {
  it('renders properly', () => {
    const wrapper = mount(LogsReport, {
      props: {
        logs: [
          {
            method: 'PUT',
            status_code: 200,
            url: 'http://proxy:8080/geoserver/rest/styles/point.sld',
          },
        ],
      },
    })
    expect(wrapper.text()).toContain('http://proxy:8080/geoserver/rest/styles/point.sld')
  })
})
