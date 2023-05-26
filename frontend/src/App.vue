<script setup>
// TODO :
// - se débarasser des let
// - faire les box de stats
// - mettre l'autocomplete
// - mettre sur git
// - déployer
import { reactive, ref, onMounted, createApp } from 'vue'
import axios from 'axios'

import LineChart from './components/LineChart.vue'
import StatsTable from './components/StatsTable.vue'

const apiUrl = 'http://localhost:5000/'
let availableSymbols = reactive([])
const dataStatsTable = reactive([])
const dataLineChart = reactive([])

const selectedSymbols = reactive(['AAPL', 'MSFT', 'META'])

onMounted(() => {
  // fetchAvailableSymbols()
  getAllTimeSeries()
  console.log(availableSymbols)
})

function logMe() {
  console.log(dataLineChart)
  console.log(availableSymbols)
  console.log(dataStatsTable)
}

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

function getAllTimeSeries() {
  for (const symbol of selectedSymbols) {
    getOneTimeSeries(symbol)
  }
}

function getOneTimeSeries(symbol) {
  axios
    .get(apiUrl + 'symbol/' + symbol)

    .then((res) => {
      dataLineChart.push({ name: symbol, data: res.data.timeSeries })
      console.log(res.data.stats)
      dataStatsTable.push(res.data.stats)
      console.log(dataLineChart)
    })
    .catch((error) => {
      console.error(error)
    })
}
</script>

<template>
  <div>
    <button @click="logMe()">logMe</button>
    <!-- <button @click="getAllTimeSeries()">Click to actualize</button> -->
    <LineChart :dataLineChart="dataLineChart" v-if="dataLineChart.length != 0" />
    <StatsTable :tableData="dataStatsTable" v-if="dataStatsTable.length != 0"/>
  </div>
</template>
