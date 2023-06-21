/**
 * Offset market timers inplace.
 * @param {Object} data The market data.
 * @param {Integer} offSet The offset to add.
 */
function offSetMarketTime(data, offSet) {

    for (let market of data) {

        if (market.isMarketOpen) {
            market.timeToClose -= offSet
        } else {
            market.timeToOpen -= offSet
        }
    }

}/**
 * Update inplace data for line charts.
 * Add or update symbol data.
 * @param {Object} dataList The data charts.
 * @param {String} symbol The symbol on which add or update data.
 * @param {Integer} newValue The data to add or update
 */
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