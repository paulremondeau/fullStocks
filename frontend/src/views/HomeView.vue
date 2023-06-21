<template>
  <div class="home">
    <MarketState :marketData="marketData" :doUpdateMarket="doUpdateMarket"
      @updateMarket="fetchBackend('market', 'put').then(newData => assignMarketData(newData))" />
    <div class="symboldata">
      <div class="lineChart">
        <div class="buttons">
          <div class="selectedSymbols">
            <SelectSymbols :availableSymbols="availableSymbols" v-model:selectedSymbols="selectedSymbols"
              @updateSymbols="updateSymbols" />
          </div>
          <div class="performanceValue">
            <button :class="[showPerformance ? 'active' : '']" @click="showPerformance = true">Performance</button>
            <button :class="[!showPerformance ? 'active' : '']" @click="showPerformance = false">Value</button>
          </div>
        </div>
        <LineChart :dataLineChart="showPerformance ? dataLineChartPerformance : dataLineChartValue" />
      </div>
    </div>
    <StatsTable :tableData="dataStatsTable" />
  </div>
</template>

<script setup>


import { reactive, ref, onMounted, watch } from 'vue'

import { fetchBackend } from '../helpers/fetchbackend'
import { offSetMarketTime, updateChartData } from '../helpers/utils'

// Components
import LineChart from '../components/LineChart.vue'
import StatsTable from '../components/StatsTable.vue'
import MarketState from '../components/MarketState.vue'
import SelectSymbols from '../components/SelectSymbols.vue'

///// States /////
const dataStatsTable = ref([])
const dataLineChartPerformance = ref([])
const dataLineChartValue = ref([])
const marketData = reactive([])
// TODO : make it a ref and update it in props (computed return read-only, that's why...)
const doUpdateMarket = reactive([false]) // A   petty trick to update in props...
const selectedSymbols = ref(['AAPL', 'MSFT', 'META'])
const availableSymbols = ref([])
const showPerformance = ref(true)

onMounted(() => {

  // Initialize Market
  fetchBackend("market", "post").then(newData => assignMarketData(newData))

  // Initialize symbols timeseries
  for (let symbol of selectedSymbols.value) {

    fetchBackend("symbols/" + symbol, 'put').then((symbolData) => {
      processApiResult(symbolData)
    })
  }

  // Initialize available symbols
  // For now, all symbols at once
  // TODO : make lists per exchange market
  // availableSymbols.value = newData
  fetchBackend("symbols-list", 'get').then((newData) => {

    availableSymbols.value = newData.map(x => x.symbolsList).flat()
  })
})


///// Functions /////
function updateSymbols(newSymbols) {
  // Two cases : one new symbol or one less symbol

  // One less symbol
  if (selectedSymbols.value.length > newSymbols.value.length) {
    // Get the different symbol
    const removedSymbol = selectedSymbols.value.filter(x => !newSymbols.value.includes(x))[0]
    selectedSymbols.value = selectedSymbols.value.filter(x => x != removedSymbol)

    dataLineChartValue.value = dataLineChartValue.value.filter(x => x.name != removedSymbol)
    dataLineChartPerformance.value = dataLineChartPerformance.value.filter(x => x.name != removedSymbol)
    dataStatsTable.value = dataStatsTable.value.filter(x => x.symbol != removedSymbol)
  }

  // One more symbol
  if (selectedSymbols.value.length < newSymbols.value.length) {
    // Get the different symbol
    const addedSymbol = newSymbols.value.filter(x => !selectedSymbols.value.includes(x))[0]
    fetchBackend("symbols/" + addedSymbol, 'put').then(symbolData => processApiResult(symbolData))

    selectedSymbols.value.push(addedSymbol)
  }


}


function assignMarketData(data) {

  doUpdateMarket[0] = true

  new Promise((resolve) => {

    let workData = data

    const timestamp = new Date().getTime();
    const offSet = timestamp - data[0].dateCheck * 1000
    offSetMarketTime(data, offSet)
    Object.assign(marketData, data)
    resolve()
  }).then(doUpdateMarket[0] = false)
}

/**
 * Add API results to state.
 * @param {Object} res The results from the backend API.
 */
function processApiResult(symbolData) {

  let symbol = symbolData.stats.symbol


  updateChartData(dataLineChartPerformance.value, symbol, symbolData.timeseries.performance)
  updateChartData(dataLineChartValue.value, symbol, symbolData.timeseries.values)


  let indexData = dataStatsTable.value.findIndex((item) => item.symbol == symbol)
  if (indexData >= 0) {
    dataStatsTable.value[indexData] = symbolData.stats
  } else {
    dataStatsTable.value.push(symbolData.stats)
  }
}

</script>

<style scoped lang="scss">
.home {
  display: inline;

  .symboldata {
    display: flex;
    margin-top: 20px;
    justify-content: space-between;
    align-items: center;
    text-align: center;



    .lineChart {
      flex: 6;
      display: inline;

      .buttons {
        display: flex;
        justify-content: center;
        align-items: end;

        .selectedSymbols {
          margin-left: 200px;
        }

        .performanceValue {
          display: flex;
          justify-content: center;
          align-items: center;
          padding: 10px;
          margin-left: 100px;

          .active {
            background-color: lightblue;
          }

        }



      }
    }
  }
}
</style>