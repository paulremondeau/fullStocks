<template>
    <div class="header">
        <h1 class="name">Full Stocks</h1>
        <div class="market">
            <MarketState :marketData="marketData" :doUpdateMarket="doUpdateMarket"
                @updateMarket="fetchBackend('market', 'put').then(newData => assignMarketData(newData))" />
        </div>
        <h1 class="search"></h1>
    </div>
</template>

<script setup>

import { reactive, onMounted } from 'vue';
import { fetchBackend } from '../helpers/fetchbackend'
import { offSetMarketTime } from '../helpers/utils'

import MarketState from "./MarketState.vue"

onMounted(() => {
    fetchBackend("market", "post")
        .then(newData => assignMarketData(newData))
        .catch((error) => {
            console.log(error)
        })
})

const marketData = reactive([])
const doUpdateMarket = reactive([false])

function assignMarketData(data) {

    doUpdateMarket[0] = true

    new Promise((resolve) => {


        const timestamp = new Date().getTime();
        const offSet = timestamp - data[0].dateCheck * 1000
        offSetMarketTime(data, offSet)
        Object.assign(marketData, data)
        resolve()
    }).then(doUpdateMarket[0] = false)
}


</script>

<style lang="scss" scoped>
.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    height: 100%;
    background: linear-gradient(0.25turn, rgb(241, 238, 238), rgb(209, 210, 226));

    .name {
        width: 8vw
    }

    .market {
        width: 88vw
    }

    .search {
        width: 2vw;
    }


}
</style>