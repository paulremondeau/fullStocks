<script setup>
// TODO :
// - se débarasser des let
// - mettre l'autocomplete
// - déployer
import { reactive, ref, onMounted, createApp } from 'vue'
import axios from 'axios'

import LineChart from './components/LineChart.vue'
import StatsTable from './components/StatsTable.vue'

import apiUrl from '../config.js'
console.log(apiUrl)
let availableSymbols = reactive([])
const dataStatsTable = reactive([])
const dataLineChart = reactive([])

const selectedSymbols = reactive(['AAPL', 'MSFT', 'META'])

onMounted(() => {
  // fetchAvailableSymbols() // will be used when the accordion to select the symbol will be working
  getAllTimeSeries()
})

function logMe() {
  console.log(dataLineChart)
  console.log(availableSymbols)
  console.log(dataStatsTable)
}

/**
 * Fetch the available symbols on the Twele Data API.
 * Call the backend python on the route /fetch_symbol .
 */
function fetchAvailableSymbols() {
  axios
    .get(apiUrl + 'fetch_symbol')
    .then((res) => {
      availableSymbols = res.data.symbolsList
    })
    .catch((error) => {
      console.error(error)
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
  axios
    .get(apiUrl + 'symbol/' + symbol)

    .then((res) => {
      dataLineChart.push({ name: symbol, data: res.data.timeSeries })
      dataStatsTable.push(res.data.stats)
    })
    .catch((error) => {
      console.error(error)
    })
}
</script>

<template>
  <div>
    <!-- <button @click="logMe()">logMe</button> -->
    <!-- <button @click="getAllTimeSeries()">Click to actualize</button> -->
    <LineChart :dataLineChart="dataLineChart" v-if="dataLineChart.length != 0" />
    <StatsTable :tableData="dataStatsTable" v-if="dataStatsTable.length != 0"/>
  </div>
</template>
