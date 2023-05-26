<script setup>
import { reactive, computed} from 'vue'
import VueTableLite from 'vue3-table-lite'

const props = defineProps({
  tableData: Object
})


const table = reactive({
  columns: [
        {
          label: "Symbol",
          field: "symbol",
          width: "3%",
          sortable: true,
          isKey: true,
        },
        {
          label: "Cumulative return", 
          field: "cumulativeReturn",
          width: "5%",
          sortable: true,
        },
        {
          label: "Annualized comulative return",
          field: "annualizedCumulativeReturn",
          width: "5%",
          sortable: true,
        },
        {
          label: "Annualized volatility",
          field: "annualizedVolatility",
          width: "5%",
          sortable: true,
        },
      ],

  rows: props.tableData, 
  totalRecordCount: computed(() => {
        return table.rows.length;
      }),
  sortable: {
    order: "id",
    sort: "asc",
  },
})
</script>


<template>
  <VueTableLite
    :is-static-mode="true"
    :columns="table.columns"
    :rows="table.rows"
    :total="table.totalRecordCount"
    :sortable="table.sortable"
  ></VueTableLite>
</template>