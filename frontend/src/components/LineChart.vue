<script setup>
import { reactive, computed, watch } from 'vue'

///// Props /////
const props = defineProps({
  dataLineChart: Object
})

///// States /////
// Needed to make the chart reactive to option change
const minimum = computed(() => {
        return props.dataLineChart.length == 0 ? 0 : props.dataLineChart[Object.keys(props.dataLineChart)[0]].data[0][0]
})

const data = reactive({
  series: props.dataLineChart,
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
      min : minimum,
      tickAmount: 6
    }
  }
})

// Make the chart rerender when data minimum changes
watch(minimum, () => {
   data.chartOptions = {...data.chartOptions}
})

</script>

<template>
  <apexchart
    type="line"
    height="700"
    width="1200"
    :options="data.chartOptions"
    :series="data.series"
  ></apexchart>
</template>
