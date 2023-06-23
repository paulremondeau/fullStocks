<script setup>
import { RouterView } from 'vue-router'
import Header from './components/Header.vue'
</script>

<template>
  <div class="app">
    <div class="header">
      <Header />
    </div>
    <div class="router">
      <RouterView />
    </div>

  </div>
</template>

<style scoped lang="scss">
.app {
  display: inline;
  width: 100vw;


  .header {
    height: 5vh;
  }

  .router {
    height: 95vh;
    padding: 0 10px 0 10px;
  }


}
</style>
