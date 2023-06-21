<template>
    >
    <VueMultiselect v-model="selectedSymbols" :options="options" :multiple="true" :close-on-select="false"
        placeHolder="Select symbols">
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


///// Emits /////
const emit = defineEmits(["updateSymbols"])

watch(selectedSymbols, () => {
    emit("updateSymbols", selectedSymbols)
})

</script>

<style src="vue-multiselect/dist/vue-multiselect.css">
.placeHolder {

    width: 200px;
}
</style>

