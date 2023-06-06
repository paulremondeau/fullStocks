import { describe, it, expect, beforeEach} from 'vitest'

import { mount, } from '@vue/test-utils'
import MarketState from '../MarketState.vue'

import { setActivePinia, createPinia } from 'pinia'

describe('MarketState', () => {

    beforeEach(() => {
        // creates a fresh pinia and make it active so it's automatically picked
        // up by any useStore() call without having to pass it to it:
        // `useStore(pinia)`
        setActivePinia(createPinia())
    })
  
    it ('initial render is empty', () => {
        
        const wrapper = mount(MarketState, 
            { 
                props: 
                {
                    marketData: []
                }
            }
        )
        expect(wrapper.text()).toBe("")

    })

})
