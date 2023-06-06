import { describe, it, expect } from 'vitest'

import { mount } from '@vue/test-utils'
import LineChart from '../LineChart.vue'

describe('LineChart', () => {
  
    it ('initial render is empty', () => {
        
        const wrapper = mount(LineChart, 
            {
                props: 
                {
                    dataLineChart: []
                }
        })
        expect(wrapper.text()).toBe("")

    })

    it ('it renders data properly', () => {
        
        const wrapper = mount(LineChart, 
            {
                props: 
                {
                    dataLineChart: { name: "foo", data: [[10,1], [121,10], [150,5]] }
                }
        })

        expect(wrapper.text()).toBe("")

    })

})
