function offSetMarketTime(data, offSet) {

    let result = []


    for (let market of data) {

        if (market.isMarketOpen) {
            market.timeToClose -= offSet
        } else {
            market.timeToOpen -= offSet
        }

        result.push(market)
    }

    return result
}

function updateChartData(dataList, symbol, newValue) {

    let indexData = dataList.findIndex((item) => item.name == symbol)
    let newData = { name: symbol, data: newValue }
    if (indexData >= 0) {
        dataList[indexData] = newData
    } else {
        dataList.push(newData)
    }
}

export { offSetMarketTime, updateChartData }