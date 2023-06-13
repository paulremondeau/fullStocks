import { describe, it, expect } from 'vitest'

import { reactive } from 'vue'
import { mount } from '@vue/test-utils'
import StatsTable from '../StatsTable.vue'

describe('StatsTable', () => {

    it('initial render is empty', () => {

        const wrapper = mount(StatsTable,
            {
                props:
                {
                    tableData: []
                }
            }
        )
        expect(wrapper.text()).toBe("SymbolCumulative returnAnnualized cumulative returnAnnualized volatilityNo data")

    })

    it('it renders data properly', () => {

        const wrapper = mount(StatsTable,
            {
                props: {

                    tableData: [{
                        "symbol": "TEST",
                        "cumulativeReturn": 10,
                        "annualizedCumulativeReturn": 15,
                        "annualizedVolatility": 20,
                    },
                    {
                        "symbol": "ABCD",
                        "cumulativeReturn": 90,
                        "annualizedCumulativeReturn": 55,
                        "annualizedVolatility": 23,
                    }]
                }
            }
        )

        expect(wrapper.text()).toBe("SymbolCumulative returnAnnualized cumulative returnAnnualized volatilityTEST101520ABCD905523Showing 1-2 of 2Row count:102550Go to page:1«First<Prev1>Next»Last")
    })

    it('it updates data properly', async () => {
        // No data at first
        const tableData = reactive([])

        const wrapper = mount(StatsTable,
            {
                props:
                {
                    tableData: tableData
                }
            }
        )

        expect(wrapper.text()).toBe("SymbolCumulative returnAnnualized cumulative returnAnnualized volatilityNo data")

        // Add some data
        await tableData.push(...[
            {
                "symbol": "TEST",
                "cumulativeReturn": 10,
                "annualizedCumulativeReturn": 15,
                "annualizedVolatility": 20,
            },
            {
                "symbol": "ABCD",
                "cumulativeReturn": 90,
                "annualizedCumulativeReturn": 55,
                "annualizedVolatility": 23,
            }
        ])


        expect(wrapper.text()).toBe("SymbolCumulative returnAnnualized cumulative returnAnnualized volatilityTEST101520ABCD905523Showing 1-2 of 2Row count:102550Go to page:1«First<Prev1>Next»Last")

        // Remove data
        await tableData.pop()
        expect(wrapper.text()).toBe("SymbolCumulative returnAnnualized cumulative returnAnnualized volatilityTEST101520Showing 1-1 of 1Row count:102550Go to page:1«First<Prev1>Next»Last")

    })
})
