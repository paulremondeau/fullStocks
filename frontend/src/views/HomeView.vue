<template>
  <div class="home">
    <MarketState :marketData="marketData" :updateMarket="updateMarket" @updateMarket="getMarketState()"/>
    <div class="symboldata">
      <LineChart :dataLineChart="dataLineChart" />
      <StatsTable :tableData="dataStatsTable"/>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted, createApp } from 'vue'
import axios from 'axios'

import LineChart from '../components/LineChart.vue'
import StatsTable from '../components/StatsTable.vue'
import MarketState from '../components/MarketState.vue'


import apiUrl from '../../config.js'

///// States /////
const dataStatsTable = reactive([])
const dataLineChart = reactive([])
const marketData = reactive([])
const updateMarket = reactive([false]) // A petty trick to update in props...
const selectedSymbols = reactive(['AAPL', 'MSFT', 'META'])

onMounted(() => {
  getMarketState()
  getAllTimeSeries()
})

///// Functions /////

/**
 * Fetch backend for market state information.
 * Disable the timer market then updates the marketData state object.
 * Then enable timer and reset it.
 */
function getMarketState() {
  axios
    .get(apiUrl + "check_market_state")
    .then((res) => {
      // This prevents unnecessary updating
      updateMarket[0] = true
      if (res.data.status == 'ok') {
        Object.assign(marketData, res.data.data)  
      }
    }).catch((error) => {
      console.error(error)
    }).finally(() => {
      // Data can update again
      updateMarket[0] = false
    })
}

/**
 * Fetch the time series and stats tables of all the symbols in selectedSymbols.
 * Add all the results in dataLineChart and dataStatsTable.
 */
function getAllTimeSeries() {
  for (const symbol of selectedSymbols) {
    getOneTimeSeries(symbol)
  }
} 

/**
 * Fetch the time series and stats table of the symbol we want.
 * Add the results to dataLineChart and dataStatsTable.
 * 
 * First check if we have the data in the data base :
 *  - if data is in the database :
 *   - if data is fresh in database, get data from databse
 *   - if data is not fresh in database :
 *    - if exchange market is open, fetch Twelve Data API
 *    - if exchange market is close, get data from database
 *  - if data is not in the database, fetch Twelve Data API
 * @param {String} symbol The symbol of the stock information we want to get
 */
function getOneTimeSeries(symbol) {
  axios
    .get(apiUrl + 'check_symbol_data/' + symbol)
    .then((res) => {
      if (res.data.dataExists) { 
        if (res.data.dataIsFresh){
          axios.get(apiUrl + 'get_symbol_data/' + symbol)
          .then((res) => {
            processApiResult(res)
          })
        } else {
          if (res.data.isMarketOpen) {
            axios.put(apiUrl + 'get_symbol_data/' + symbol)
          .then((res) => {
            processApiResult(res)
          })
          } else {
            axios.get(apiUrl + 'get_symbol_data/' + symbol)
          .then((res) => {
            processApiResult(res)
          })
          }
  
        }
      }
      else {
        axios.post(apiUrl + 'get_symbol_data/' + symbol)
          .then((res) => {
            processApiResult(res)
          })
      }
    }).catch((error) => {
      console.error(error)
    })
}

/**
 * Add API results to state.
 * @param {Object} res The results from the backend API.
 */
function processApiResult(res) {
  if (res.data.status == 'ok') {
    dataLineChart.push({ name: res.data.symbol, data: res.data.data })
    dataStatsTable.push(res.data.stats)
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
    }
}

</style>