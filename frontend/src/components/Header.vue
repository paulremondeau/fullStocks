<template>
    <div class="header">
        <h1 class="name">Full Stocks</h1>
        <div class="market">
            <MarketState :marketData="marketData" :doUpdateMarket="doUpdateMarket"
                @updateMarket="fetchBackend('market', 'put').then(newData => assignMarketData(newData))" />
        </div>
        <!-- <div class="logo"></div> -->
        <a href="https://paulremondeau.github.io">
            <img src="../assets/github.svg" class="logo" target="_blank" rel="noopener noreferrer" />
        </a>
    </div>
</template>

<script setup>

import { reactive, onMounted } from 'vue';
import { fetchBackend } from '../helpers/fetchbackend'
import { offSetMarketTime } from '../helpers/utils'

import MarketState from "./MarketState.vue"

onMounted(() => {
    fetchBackend("market", "post")
        .then((newData) => {
            if (newData.status == "ok") {
                assignMarketData(newData.data)
            }
        })
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

    .name {
        width: 8vw;
        line-height: 30px;
        margin-left: 10px;
    }

    .market {
        width: 87vw
    }

    a {
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 10px;

        transition-property: none;
        pointer-events: stroke;

        &:hover {
            background-color: transparent;

        }


    }

}
</style>