import { defineStore } from 'pinia'
import {ref, watch} from 'vue'

export const useTimerMarketStore = defineStore('timermarket', () => {
    const timerValue = ref(1)
    const isEnabled = ref(true)
    
    function increment() {
      if (isEnabled.value) {
        setTimeout(() => {
           timerValue.value++
        }, 1000);
      }
    }
    function reset() {
      timerValue.value = 0
    }
    function disable() {
      isEnabled.value = false
    }
    function enable() {
      isEnabled.value = true
    }
    
    return { timerValue, isEnabled, increment, reset, disable, enable}
  })