<script setup>
import { RouterLink, RouterView } from 'vue-router'
import {useTimerMarketStore} from '@/stores/timermarket'
const timerMarket = useTimerMarketStore() 
</script>

<template>
  <RouterView />
</template>

<style scoped>

</style>
