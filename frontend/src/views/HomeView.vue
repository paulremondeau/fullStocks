<template>
  <div class="home">
    <MarketState :marketData="marketData" :doUpdateMarket="doUpdateMarket" @updateMarket="updateMarketData" />
    <div class="symboldata">
      <div class="lineChart">
        <div class="buttons">
          <SelectSymbols :availableSymbols="availableSymbols" v-model:selectedSymbols="selectedSymbols"
            @updateSymbols="updateSymbols" />
          <button :class="[showPerformance ? 'active' : '']" @click="showPerformance = true">Performance</button>
          <button :class="[!showPerformance ? 'active' : '']" @click="showPerformance = false">Value</button>
        </div>
        <LineChart :dataLineChart="showPerformance ? dataLineChartPerformance : dataLineChartValue" />
        <!-- <LineChart :dataLineChart="dataLineChartValue" v-if="!showPerformance" /> -->
      </div>
    </div>
    <StatsTable :tableData="dataStatsTable" />
  </div>
  <button @click="logMe">Log Me Home</button>
</template>

<script setup>
function logMe() {
  console.log(dataStatsTable.value)
  console.log(availableSymbols.value)
}

import { reactive, ref, onMounted, watch } from 'vue'
import axios from 'axios'

import LineChart from '../components/LineChart.vue'
import StatsTable from '../components/StatsTable.vue'
import MarketState from '../components/MarketState.vue'
import SelectSymbols from '../components/SelectSymbols.vue'


import apiUrl from '../../config.js'

///// States /////
const dataStatsTable = ref([])
const dataLineChartPerformance = ref([])
const dataLineChartValue = ref([])
const marketData = reactive([])
const doUpdateMarket = reactive([false]) // A   petty trick to update in props...
const selectedSymbols = ref(['AAPL', 'MSFT', 'META'])
const availableSymbols = ref([])
const showPerformance = ref(true)
const timeDelta = ref("timeDelta")

onMounted(() => {
  createMarketState()
  initializeTimeSeries()
  initializeAvailableSymbols()
})


///// Functions /////

function initializeAvailableSymbols() {

  getAvailableSymbols().then((newData) => {

    availableSymbols.value = newData.map(x => x.symbolsList).flat()
  })

  // For now, all symbols at once
  // TODO : make lists per exchange market
  // availableSymbols.value = newData


}

function getAvailableSymbols() {
  return axios
    .get(apiUrl + "symbols/list")
    .then((res) => {

      // Data exists
      if (res.status == 200) {
        return res.data
      }

      // Data does not exist
      if (res.status == 204) {
        return createAvailableSymbols()
      }


    })
    .catch((error) => {
      console.log(error)
    })

}

function createAvailableSymbols() {
  return axios
    .post(apiUrl + "symbols/list")
    .then((res) => {


      // Data already exists
      if (res.status == 200) {
        return updateAvailableSymbols()
      }

      // Data was created
      if (res.status == 201) {
        return getAvailableSymbols()

      }

      if (fetchData) {

      }

    }).catch((error) => {
      console.log(error)
    })
}

function updateAvailableSymbols() {

  return axios
    .put(apiUrl + "symbols/list")
    .then((res) => {

      // Data successfully update
      if (res.status == 200) {
        return getAvailableSymbols()
      }

      // Data does not exist
      if (res.status == 204) {
        return createAvailableSymbols()
      }
    })


}

function updateSymbols(newSymbols) {



  // Two cases : one new symbol or one less symbol

  // One less symbol
  if (selectedSymbols.value.length > newSymbols.value.length) {
    // Get the different symbol
    console.log("one less")
    let removedSymbol = selectedSymbols.value.filter(x => !newSymbols.value.includes(x))[0]
    console.log(removedSymbol)
    selectedSymbols.value = selectedSymbols.value.filter(x => x != removedSymbol)

    dataLineChartValue.value = dataLineChartValue.value.filter(x => x.name != removedSymbol)
    dataLineChartPerformance.value = dataLineChartPerformance.value.filter(x => x.name != removedSymbol)
    dataStatsTable.value = dataStatsTable.value.filter(x => x.symbol != removedSymbol)


  }

  // One more symbol
  if (selectedSymbols.value.length < newSymbols.value.length) {
    console.log("one more")
    // Get the different symbol
    let addedSymbol = newSymbols.value.filter(x => !selectedSymbols.value.includes(x))[0]
    console.log(addedSymbol)
    updateTimeSeries(addedSymbol).then(symbolData => processApiResult(symbolData))

    selectedSymbols.value.push(addedSymbol)
  }


}

function createMarketState() {

  let fetchData = false
  let timeOffset = false

  axios
    .post(apiUrl + "market")
    .then(async (res) => {


      // The data was created on the server
      if (res.status == 201) {

        fetchData = true

      }

      // The data already exists on the server
      if (res.status == 200) {
        timeOffset = true
        fetchData = true

      }

      if (fetchData) {

        let data = await getMarketState()
        assignMarketData(data, timeOffset)

      }

    })
    .catch((error) => {
      console.log(error)
    }
    )

}

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


function assignMarketData(data, timeOffset = false) {

  doUpdateMarket[0] = true



  new Promise((resolve, reject) => {

    let workData = data
    if (timeOffset) {
      const timestamp = new Date().getTime();
      const offSet = timestamp - data[0].dateCheck * 1000
      workData = offSetMarketTime(data, offSet)
    }

    Object.assign(marketData, workData)
    resolve()
  }).then(doUpdateMarket[0] = false)
}

function updateMarketData() {

  axios
    .put(apiUrl + "market")
    .then(async (res) => {

      // Data does not exist on the server
      if (res.status == 204) {
        createMarketState()
      }

      // Data successfully updated
      if (res.status == 200) {

        let data = await getMarketState()
        assignMarketData(data)
      }
    })
    .catch((error) => {
      console.log(error)
    }
    )

}

/**
 * Fetch backend for market state information.
 * Disable the timer market then updates the marketData state object.
 * Then enable timer and reset it.
 */
function getMarketState() {

  return axios
    .get(apiUrl + "market")
    .then(res => res.data)
    .catch((error) => {
      console.error(error)
    })
}

function initializeTimeSeries() {

  for (let symbol of selectedSymbols.value) {
    console.log(symbol)
    updateTimeSeries(symbol).then(symbolData => processApiResult(symbolData))
  }

}

function updateTimeSeries(symbol) {

  return axios
    .put(apiUrl + "symbols/" + symbol)
    .then((res) => {



      // Data does not exist
      if (res.status == 204) {
        return createTimeSeries(symbol)
      }

      // Data successfully update
      if (res.status == 200) {
        return getTimeSeries(symbol)
      }



    })
    .catch((error) => {

      if (error.response.status == 304) {
        return getTimeSeries(symbol)
      } else {
        console.log(error)
      }

    })

}

function createTimeSeries(symbol) {

  return axios({
    method: 'post',
    url: apiUrl + 'symbols',
    data: {
      symbol: symbol
    }
  }).then((res) => {

    // Data already exists
    if (res.status == 200) {
      return getTimeSeries(symbol)
    }

    // Data created
    if (res.status == 201) {
      return getTimeSeries(symbol)
    }

  }).catch((error) => {
    console.log(error)
  })

}

function getTimeSeries(symbol) {

  return axios
    .get(apiUrl + "symbols/" + symbol)
    .then((res) => {

      // No data found
      if (res.status == 204) {
        console.log("No data for symbol " + symbol)
      }

      // Data found
      if (res.status == 200) {
        return res.data
      }

    }).catch((error) => {
      console.log(error)
    })

}


/**
 * Add API results to state.
 * @param {Object} res The results from the backend API.
 */
function processApiResult(symbolData) {

  let symbol = symbolData.stats.symbol


  updateDataList(dataLineChartPerformance.value, symbol, symbolData.timeseries.performance)
  updateDataList(dataLineChartValue.value, symbol, symbolData.timeseries.values)


  let indexData = dataStatsTable.value.findIndex((item) => item.symbol == symbol)
  console.log(indexData)
  if (indexData >= 0) {
    dataStatsTable.value[indexData] = symbolData.stats
  } else {
    dataStatsTable.value.push(symbolData.stats)
  }
}

function updateDataList(dataList, symbol, newValue) {

  let indexData = dataList.findIndex((item) => item.name == symbol)
  let newData = { name: symbol, data: newValue }
  if (indexData >= 0) {
    dataList[indexData] = newData
  } else {
    dataList.push(newData)
  }
}

// watch(selectedSymbols, () => {

//   dataLineChartPerformance.value = dataLineChartPerformance.value.filter((item) => selectedSymbols.value.includes(item.name))
//   dataLineChartValue.value = dataLineChartValue.value.filter((item) => selectedSymbols.value.includes(item.name))
//   dataStatsTable.value = dataStatsTable.value.filter((item) => selectedSymbols.value.includes(item.symbol))

//   initializeTimeSeries()

// }

// )

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
        align-items: center;

        .active {
          margin: 10px;
          background-color: lightblue;
        }

      }
    }
  }
}
</style>