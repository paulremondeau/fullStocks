<template>
  <div class="home">
    <MarketState :marketData="marketData" :doUpdateMarket="doUpdateMarket" @updateMarket="updateMarketData()" />
    <div class="symboldata">
      <div class="lineChart">
        <div class="buttons">
          <button :class="[showPerformance ? 'active' : '']" @click="showPerformance = true">Performance</button>
          <button :class="[!showPerformance ? 'active' : '']" @click="showPerformance = false">Value</button>
        </div>
        <LineChart :dataLineChart="showPerformance ? dataLineChartPerformance : dataLineChartValue" />
        <!-- <LineChart :dataLineChart="dataLineChartValue" v-if="!showPerformance" /> -->
      </div>
      <StatsTable :tableData="dataStatsTable" />
    </div>
  </div>
</template>

<script setup>

import { reactive, ref, onMounted, watch } from 'vue'
import axios from 'axios'

import LineChart from '../components/LineChart.vue'
import StatsTable from '../components/StatsTable.vue'
import MarketState from '../components/MarketState.vue'


import apiUrl from '../../config.js'

///// States /////
const dataStatsTable = reactive([])
const dataLineChartPerformance = reactive([])
const dataLineChartValue = reactive([])
const marketData = reactive([])
const doUpdateMarket = reactive([false]) // A   petty trick to update in props...
const selectedSymbols = reactive(['AAPL', 'MSFT', 'META'])
const showPerformance = ref(true)
const timeDelta = ref("timeDelta")

onMounted(() => {
  createMarketState()
  initializeTimeSeries()
})

///// Functions /////
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

      // Data sucessfuly updated
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

async function initializeTimeSeries() {

  for (let symbol of selectedSymbols) {
    let symbolData = await updateTimeSeries(symbol)
    processApiResult(symbolData)
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

  dataLineChartPerformance.push({ name: symbolData.stats.symbol, data: symbolData.timeseries.performance })
  dataLineChartValue.push({ name: symbolData.stats.symbol, data: symbolData.timeseries.values })
  dataStatsTable.push(symbolData.stats)
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

      display: inline;

      .buttons {
        display: flex;
        justify-content: center;
        align-items: center;

        .active {
          background-color: lightblue;
        }

      }
    }
  }
}
</style>