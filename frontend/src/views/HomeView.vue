<template>
  <div class="home">
    <button @click="logMe()">logMe</button>
    <!-- <button @click="getMarketState()">Click to actualize</button> -->
    <MarketState :marketData="marketData" v-if="marketData.length != 0" @updateMarket="getMarketState()"/>
    <LineChart :dataLineChart="dataLineChart" v-if="dataLineChart.length != 0" />
    <StatsTable :tableData="dataStatsTable" v-if="dataStatsTable.length != 0"/>
  </div>
</template>

<script setup>
// TODO :
// - se débarasser des let
// - mettre l'autocomplete
import { reactive, ref, onMounted, createApp } from 'vue'
import axios from 'axios'

import LineChart from '../components/LineChart.vue'
import StatsTable from '../components/StatsTable.vue'
import MarketState from '../components/MarketState.vue'

import apiUrl from '../../config.js'


const dataStatsTable = reactive([])
const dataLineChart = reactive([])
const marketData = reactive([])
const selectedSymbols = reactive(['AAPL', 'MSFT', 'META'])

onMounted(() => {
  getMarketState()
  getAllTimeSeries()
})

function getMarketState() {
  axios
    .get(apiUrl + "check_market_state")
    .then((res) => {
      if (res.data.status == 'ok') {
        
        Object.assign(marketData, res.data.data) 
      }
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
 * @param {String} symbol The symbol of the stock information we want to get
 */
function getOneTimeSeries(symbol) {

  // First check if we have the data in the data base
  // - if data is in the database :
  //    - if data is fresh in database, get data from databse
  //    - if data is not fresh in database :
  //        - if exchange market is open, fetch Twelve Data API
  //        - if exchange market is close, get data from database
  // - if data is not in the database, fetch Twelve Data API
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

function processApiResult(res) {
  if (res.data.status == 'ok') {
    dataLineChart.push({ name: res.data.symbol, data: res.data.data })
    dataStatsTable.push(res.data.stats)
  }
}

function logMe() {
  console.log(marketData)

}
</script>




<style scoped>
.home {
    display: inline;
    justify-content: center;
    align-items: center;
    text-align: center;

}
</style>