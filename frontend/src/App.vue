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

  .header {
    height: 7vh;
    background: linear-gradient(0.25turn, rgb(241, 238, 238), rgb(209, 210, 226));

  }

  .router {
    padding: 0 10px 0 10px;
  }


}
</style>
