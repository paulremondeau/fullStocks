<script setup>
import { reactive } from 'vue'
import VueApexCharts from 'vue3-apexcharts'

const props = defineProps({
  dataLineChart: Object
})

const data = reactive({
  series: props.dataLineChart,
  chartOptions: {
    chart: {
      height: 350,
      type: 'line',
      zoom: {
        type: 'x',
        enabled: true,
        autoScaleYaxis: true
      }
    },
    dataLabels: {
      enabled: false
    },
    stroke: {
      curve: 'straight'
    },
    title: {
      text: 'Stocks performances',
      align: 'center'
    },
    grid: {
      row: {
        colors: ['#f3f3f3', 'transparent'], // takes an array which will be repeated on columns
        opacity: 0.5
      }
    },
    xaxis: {
      type: 'datetime',
      min: props.dataLineChart[Object.keys(props.dataLineChart)[0]].data[0][0],
      tickAmount: 6
    }
  }
})

function logMe() {
  console.log(props.dataLineChart)
  console.log(props.dataLineChart[Object.keys(props.dataLineChart)[0]].data[0][0])
}
</script>

<template>
  <!-- <button @click="logMe()">logMe</button> -->
  <VueApexCharts
    type="line"
    height="500"
    width="1000"
    :options="data.chartOptions"
    :series="data.series"
  ></VueApexCharts>
</template>