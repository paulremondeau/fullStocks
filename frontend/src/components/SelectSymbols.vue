<template>
    >
    <VueMultiselect v-model="selectedSymbols" :options="options" :multiple="true" placeHolder="Select symbols">
    </VueMultiselect>
</template>

<script setup>

import { computed, ref, watch } from 'vue'
import VueMultiselect from 'vue-multiselect'


const props = defineProps({
    availableSymbols: Array,
    selectedSymbols: Array
})

const selectedSymbols = ref([])
selectedSymbols.value.push(...props.selectedSymbols)
const options = computed(() => props.availableSymbols)


function updateSelectedSymbols(selectedSymbols) {
    emit('input', selectedSymbols.value)
}

function logMe() {
    console.log(select)
}

///// Emits /////
const emit = defineEmits(["updateSymbols"])

watch(selectedSymbols, () => {
    console.log(selectedSymbols)
    emit("updateSymbols", selectedSymbols)
})

</script>

<style src="vue-multiselect/dist/vue-multiselect.css">
.placeHolder {

    width: 200px;
}
</style>

