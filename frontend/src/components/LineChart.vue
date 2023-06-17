
<template>
  <apexchart type="line" height="700" width="1200" :options="data.chartOptions" :series="data.series">
  </apexchart>
</template>



<script setup>
import { reactive, computed, watch } from 'vue'


///// Props /////
const props = defineProps({
  dataLineChart: Object,
})


// Needed to make the chart reactive to option change
const minimum = computed(() => {
  return data.series.length == 0 ? 0 : data.series[Object.keys(data.series)[0]].data[0][0]
})

const title = computed(() => props.title)

const data = reactive({
  series: computed(() => props.dataLineChart),
  chartOptions: {
    chart: {
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
    grid: {
      row: {
        colors: ['#f3f3f3', 'transparent'], // takes an array which will be repeated on columns
        opacity: 0.5
      }
    },
    xaxis: {
      type: 'datetime',
      min: minimum,
      tickAmount: 6
    }
  }
})

// Make the chart rerender when data minimum changes
watch(minimum, () => {
  data.chartOptions = { ...data.chartOptions }
})


</script>
