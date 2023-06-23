<template>
  <div class="home">
    <div class="symboldata">
      <div class="lineChart">
        <div class="buttons">
          <div class="selectedSymbols">
            <SelectSymbols :availableSymbols="availableSymbols" v-model:selectedSymbols="selectedSymbols"
              @updateSymbols="updateSymbols" />
          </div>
          <ul class="timeDelta">
            <li v-for="timeDelta in timeDeltas">
              <button :class="[chosenTimeDelta == timeDelta ? 'active' : '']" @click="chosenTimeDelta = timeDelta">{{
                timeDelta }}</button>
            </li>
          </ul>
          <div class="performanceValue">
            <button :class="[showPerformance ? 'active' : '']" @click="showPerformance = true">Performance</button>
            <button :class="[!showPerformance ? 'active' : '']" @click="showPerformance = false">Value</button>
          </div>
        </div>
        <LineChart :dataLineChart="showPerformance
          ? dataLineChartPerformance[chosenTimeDelta]
          : dataLineChartValue[chosenTimeDelta]" />
      </div>
    </div>
    <StatsTable :tableData="dataStatsTable" />
    <button @click="logMe">Log Me home</button>
  </div>
</template>

<script setup>

// TODO : maybe change data to store only the shown graph, to reduce memory client side (thus call backend everytime performance/value change or timeDelta change)
import { reactive, ref, onMounted, watch } from 'vue'

import { fetchBackend } from '../helpers/fetchbackend'
import { updateChartData } from '../helpers/utils'

// Components
import LineChart from '../components/LineChart.vue'
import StatsTable from '../components/StatsTable.vue'
import SelectSymbols from '../components/SelectSymbols.vue'

const timeDeltas = ["1min", "5min", "15min", "30min", "45min", "1h", "2h", "4h", "1day", "1week", "1month"]

///// States /////
const dataStatsTable = ref([])
const dataLineChartPerformance = reactive(Object.fromEntries(timeDeltas.map(i => [i, []])))
const dataLineChartValue = reactive(Object.fromEntries(timeDeltas.map(i => [i, []])))
const marketData = reactive([])
// TODO : make it a ref and update it in props (computed return read-only, that's why...)
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

    fetchBackend("symbols/" + symbol, 'put', {}, { "timeDelta": chosenTimeDelta.value })
      .then((symbolData) => {

        processApiResult(symbolData, chosenTimeDelta.value)
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

    dataLineChartValue[timeDelta] = dataLineChartValue[timeDelta].filter(x => x.name != removedSymbol)
    dataLineChartPerformance[timeDelta] = dataLineChartPerformance[timeDelta].filter(x => x.name != removedSymbol)
    dataStatsTable.value = dataStatsTable.value.filter(x => x.symbol != removedSymbol)
  }

  // One more symbol
  if (selectedSymbols.value.length < newSymbols.value.length) {
    // Get the different symbol
    const addedSymbol = newSymbols.value.filter(x => !selectedSymbols.value.includes(x))[0]
    fetchBackend("symbols/" + addedSymbol, 'put', {}, { "timeDelta": timeDelta }).then(symbolData => processApiResult(symbolData, timeDelta))

    selectedSymbols.value.push(addedSymbol)
  }


}


/**
 * Add API results to state.
 * @param {Object} res The results from the backend API.
 */
function processApiResult(symbolData, timeDelta) {

  let symbol = symbolData.stats.symbol

  updateChartData(dataLineChartPerformance[timeDelta], symbol, symbolData.timeseries.performance)
  updateChartData(dataLineChartValue[timeDelta], symbol, symbolData.timeseries.values)


  let indexData = dataStatsTable.value.findIndex((item) => item.symbol == symbol)
  if (indexData >= 0) {
    dataStatsTable.value[indexData] = symbolData.stats
  } else {
    dataStatsTable.value.push(symbolData.stats)
  }
}

watch(chosenTimeDelta, initTimeSeries)

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

        ul.timeDelta {
          display: flex;
          list-style-type: none;
          justify-content: space-between;


        }

        .selectedSymbols {
          margin-left: 200px;
        }

        .performanceValue {
          display: flex;
          justify-content: center;
          align-items: center;
          padding: 10px;
          margin-left: 100px;

        }

        .active {
          background-color: lightblue;
        }

      }
    }
  }
}
</style>