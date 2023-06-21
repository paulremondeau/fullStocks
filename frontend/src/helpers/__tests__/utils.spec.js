import { describe, it, expect } from 'vitest'

import { offSetMarketTime, updateChartData } from '../utils'

describe('offSetMarketTime', () => {

    it('should work', () => {

        const offSet = 1
        const marketData = [
            {
                "isMarketOpen": true,
                "timeToClose": 100,
                "timeToOpen": 100
            },
            {
                "isMarketOpen": false,
                "timeToClose": 100,
                "timeToOpen": 100
            },
        ]

        offSetMarketTime(marketData, offSet)
        expect(marketData).toStrictEqual([
            {
                "isMarketOpen": true,
                "timeToClose": 99,
                "timeToOpen": 100
            },
            {
                "isMarketOpen": false,
                "timeToClose": 100,
                "timeToOpen": 99
            },
        ])

        offSetMarketTime(marketData, -2)
        expect(marketData).toStrictEqual([
            {
                "isMarketOpen": true,
                "timeToClose": 101,
                "timeToOpen": 100
            },
            {
                "isMarketOpen": false,
                "timeToClose": 100,
                "timeToOpen": 101
            },
        ])

    })


})

describe('updateChartData', () => {

    it('should work', () => {

        const symbol1 = "ABCD"
        const symbol2 = "EFGH"

        let dataList = [
            {
                "name": "ABCD",
                "data": 10
            },
            {
                "name": "IJKL",
                "data": 50
            }
        ]

        updateChartData(dataList, symbol1, 30)

        expect(dataList).toStrictEqual([
            {
                "name": "ABCD",
                "data": 30
            },
            {
                "name": "IJKL",
                "data": 50
            }
        ])

        updateChartData(dataList, symbol2, 22.15)
        expect(dataList).toStrictEqual([
            {
                "name": "ABCD",
                "data": 30
            },
            {
                "name": "IJKL",
                "data": 50
            },
            {
                "name": "EFGH",
                "data": 22.15
            }
        ])

    })

})
