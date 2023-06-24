<template>
  <div class="home">
    <div class="lineChart">
      <div class="chartOptions">
        <div class="selectedSymbols">
          <h2>Select symbols</h2>
          <SelectSymbols :availableSymbols="availableSymbols" v-model:selectedSymbols="selectedSymbols"
            @updateSymbols="updateSymbols" />
        </div>
        <div class="buttons">
          <h2>Select time interval</h2>
          <ul>
            <li v-for="timeDelta in timeDeltas">
              <button :class="[chosenTimeDelta == timeDelta ? 'active' : '']" @click="chosenTimeDelta = timeDelta">{{
                timeDelta }}</button>
            </li>
          </ul>
        </div>
        <div></div>
        <div class="buttons">
          <h2>Select data kind</h2>
          <ul>
            <li>
              <button :class="[showPerformance ? 'active' : '']" @click="showPerformance = true">Performance</button>
            </li>
            <li>
              <button :class="[!showPerformance ? 'active' : '']" @click="showPerformance = false">Value</button>
            </li>
          </ul>
        </div>
      </div>
      <LineChart :dataLineChart="dataLineChart" />
    </div>
    <div class="statsTable">
      <h1>Statistical informations</h1>
      <StatsTable :tableData="dataStatsTable" />
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'

import { fetchBackend } from '../helpers/fetchbackend'
import { updateChartData } from '../helpers/utils'

// Components
import LineChart from '../components/LineChart.vue'
import StatsTable from '../components/StatsTable.vue'
import SelectSymbols from '../components/SelectSymbols.vue'

const timeDeltas = ["1min", "5min", "15min", "30min", "45min", "1h", "2h", "4h", "1day", "1week", "1month"]

///// States /////
const dataStatsTable = ref([])
const dataLineChart = ref([])
const selectedSymbols = ref(['AAPL', 'MSFT', 'META'])
const availableSymbols = ref([])
const showPerformance = ref(true)


const chosenTimeDelta = ref("4h")

onMounted(() => {

  // Initialize symbols timeseries
  initTimeSeries()

  // Initialize available symbols
  // For now, all symbols at once
  // TODO : make lists per exchange market
  // availableSymbols.value = newData
  fetchBackend("symbols-list", 'get')
    .then((newData) => {
      availableSymbols.value = newData.map(x => x.symbolsList).flat()
    }).catch((error) => {
      console.log(error)
    })
})

function initTimeSeries() {
  for (let symbol of selectedSymbols.value) {

    fetchBackend("symbols/" + symbol, 'put', {}, { "timeDelta": chosenTimeDelta.value, performance: showPerformance.value })
      .then((symbolData) => {

        processApiResult(symbolData)
      }).catch((error) => {
        console.log(error)
      })
  }
}


///// Functions /////
function updateSymbols(newSymbols) {
  // Two cases : one new symbol or one less symbol

  const timeDelta = chosenTimeDelta.value // To fix this value through the function execution

  // One less symbol
  if (selectedSymbols.value.length > newSymbols.value.length) {
    // Get the different symbol
    const removedSymbol = selectedSymbols.value.filter(x => !newSymbols.value.includes(x))[0]
    selectedSymbols.value = selectedSymbols.value.filter(x => x != removedSymbol)

    dataLineChart.value = dataLineChart.value.filter(x => x.name != removedSymbol)
    dataStatsTable.value = dataStatsTable.value.filter(x => x.symbol != removedSymbol)
  }

  // One more symbol
  if (selectedSymbols.value.length < newSymbols.value.length) {
    // Get the different symbol
    const addedSymbol = newSymbols.value.filter(x => !selectedSymbols.value.includes(x))[0]
    fetchBackend("symbols/" + addedSymbol, 'put', {}, { "timeDelta": timeDelta, performance: showPerformance.value }).then(symbolData => processApiResult(symbolData, timeDelta))

    selectedSymbols.value.push(addedSymbol)
  }


}


/**
 * Add API results to state.
 * @param {Object} res The results from the backend API.
 */
function processApiResult(symbolData) {

  let symbol = symbolData.stats.symbol

  updateChartData(dataLineChart.value, symbol, symbolData.timeseries)


  let indexData = dataStatsTable.value.findIndex((item) => item.symbol == symbol)
  if (indexData >= 0) {
    dataStatsTable.value[indexData] = symbolData.stats
  } else {
    dataStatsTable.value.push(symbolData.stats)
  }
}

watch(chosenTimeDelta, initTimeSeries)
watch(showPerformance, initTimeSeries)

</script>

<style scoped lang="scss">
.home {
  display: inline;

  .lineChart {
    display: inline;
    text-align: center;


    .chartOptions {
      display: flex;
      justify-content: space-between;
      align-items: center;
      // background-color: blue;
      padding: 5px;

      .selectedSymbols {
        display: inline;
      }

      .buttons {
        display: inline;

        ul {
          display: flex;
          list-style-type: none;
          justify-content: space-between;

          li {
            text-align: justify;

            button {
              margin: 0 5px 0 0;
              height: 100%;
              font-size: 15px;
              width: 100px;
            }

            button.active {
              background-color: lightblue;
            }

          }
        }
      }
    }

  }

  .statsTable {
    text-align: center;
    display: inline;
  }
}
</style>