import { describe, it, expect, beforeEach, vi } from 'vitest'

import { mount, } from '@vue/test-utils'
import MarketState from '../MarketState.vue'

import { reactive } from 'vue'

function delay(milliseconds) {
    return new Promise(resolve => {
        setTimeout(resolve, milliseconds);
    });
}


describe('MarketState', () => {

    it('initial render is empty', () => {

        const wrapper = mount(MarketState,
            {
                props:
                {
                    marketData: [],
                    doUpdateMarket: [false]
                }
            }
        )
        expect(wrapper.text()).toBe("")
    })

    it('it renders data properly', () => {
        const wrapper = mount(MarketState,
            {
                props:
                {
                    marketData: [{ "exchange": "NASDAQ", "isMarketOpen": true, "timeToClose": 224000 }],
                    doUpdateMarket: [false]
                }
            }
        )
        expect(wrapper.text()).toBe("NASDAQOPEN00:03:44NASDAQOPEN00:03:44")
    })


    it('the timer is correctly decreasing', async () => {

        const wrapper = mount(MarketState,
            {
                props:
                {
                    marketData: [
                        { "exchange": "NASDAQ", "isMarketOpen": true, "timeToClose": 224000, "timeToOpen": 1651651065 },
                        { "exchange": "Munich", "isMarketOpen": false, "timeToClose": 11606523065, "timeToOpen": 1450000 }
                    ],
                    doUpdateMarket: [false]
                }
            }
        )

        expect(wrapper.text()).toBe("NASDAQOPEN00:03:44MunichCLOSE00:24:10NASDAQOPEN00:03:44MunichCLOSE00:24:10")

        await (delay(1000))

        expect(wrapper.text()).toBe("NASDAQOPEN00:03:43MunichCLOSE00:24:09NASDAQOPEN00:03:43MunichCLOSE00:24:09")

    })

    it('the timer does not go below 0', async () => {

        const wrapper = mount(MarketState,
            {
                props:
                {
                    marketData: [
                        { "exchange": "NASDAQ", "isMarketOpen": true, "timeToClose": 1000, "timeToOpen": 1000 },
                        { "exchange": "Munich", "isMarketOpen": false, "timeToClose": 1000, "timeToOpen": 1000 }
                    ],
                    doUpdateMarket: [false]
                }
            }
        )

        expect(wrapper.text()).toBe("NASDAQOPEN00:00:01MunichCLOSE00:00:01NASDAQOPEN00:00:01MunichCLOSE00:00:01")

        await (delay(1000))

        expect(wrapper.text()).toBe("NASDAQOPEN00:00:00MunichCLOSE00:00:00NASDAQOPEN00:00:00MunichCLOSE00:00:00")

        await (delay(1000))

        expect(wrapper.text()).toBe("NASDAQOPEN00:00:00MunichCLOSE00:00:00NASDAQOPEN00:00:00MunichCLOSE00:00:00")

    })

})
