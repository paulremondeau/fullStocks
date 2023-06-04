<template>
    <div class="slider" >
        <div class="slide-track" v-for="index in 3" :key="index">
            <div class="slide" v-for="exchangeData in marketData">
                <h1> {{exchangeData.exchange}} </h1>
                <span :class="openOrClose(exchangeData)"> 
                    {{exchangeData.isMarketOpen ? "OPEN" : "CLOSE"}} 
                </span>
                <h2> 
                    {{exchangeData.isMarketOpen ? Duration.fromMillis(exchangeData.timeToClose).toFormat("hh:mm:ss")
                    : Duration.fromMillis(exchangeData.timeToOpen).toFormat("hh:mm:ss")}} 
                </h2>
            </div>
        </div>
    </div>
</template>

<script setup>
import {reactive, ref, watch, computed} from 'vue'
import {Duration} from "luxon";
import {storeToRefs} from 'pinia'

///// Stores /////
import {useTimerMarketStore} from '@/stores/timermarket'
const timerMarket = useTimerMarketStore() 
const {timerValue} = storeToRefs(timerMarket)

///// States /////
const emitUpdateMarket = ref(false)

// For the Caroussel
const nomberOfExhanges = computed(() => 
    props.marketData.length
)


///// Functions /////
/**
 * Switch class between open or close
 * @param {Object} exchangeData Exchange market data informations.
 */
function openOrClose (exchangeData) {
    return exchangeData.isMarketOpen ? 'open' : 'close'
}

/**
 * Update the time displayed under exchange markets information.
 * @return {Promise} A promise to make sure all data are updated and only one emit will trigger.
 */
function updateTimerMarket(){
    return new Promise((resolve, reject) => {
        if (!emitUpdateMarket.value) {
             for (const exchangeData of props.marketData){
            let indexData = props.marketData.indexOf(exchangeData)
            if (exchangeData.isMarketOpen) {     
                exchangeData.timeToClose -= 1000;
                if (exchangeData.timeToClose < 0){
                    timerMarket.disable()
                    emitUpdateMarket.value = true
                    
                } else {
                props.marketData[indexData] = exchangeData
                }
            } else {
                exchangeData.timeToOpen -= 1000;
                if (exchangeData.timeToOpen < 0){
                    timerMarket.disable()
                    emitUpdateMarket.value = true
                    
                } else {
                props.marketData[indexData] = exchangeData
                }
            }
        }
    } else {
        emitUpdateMarket.value = false
    }
    // It's to make sure we will only trigger one emit
    resolve()
    })
}


///// Props /////
const props = defineProps({
  /**
   * The markets data.
   */
  marketData: Object
})

///// Emits /////
const emit = defineEmits(["updateMarket"])

// Timer decreasing event
watch(timerValue, timerMarket.increment)
watch(timerValue, () => {
    updateTimerMarket()
        .then((res) => {
            if (emitUpdateMarket.value) {
                emit('updateMarket')
            }
        })
    }
)
</script>


<style scoped lang="scss">

@mixin white-gradient {
	background: linear-gradient(to right,  rgba(255,255,255,1) 0%,rgba(255,255,255,0) 100%);
}

// Scroll adapts to number of child component to make it look continuous
$nomberOfExhanges: v-bind('nomberOfExhanges');
$animationSpeed: 40s;
$sliderHeight: 80px;
$slideWidth: 100px;

// Animation
@keyframes scroll {
	0% { transform: translateX(0); }
	100% { transform: translateX(calc(-1 * $slideWidth * $nomberOfExhanges))}
}

// Styling
.slider {
    display: flex;
    overflow:hidden;
	background: white;
    margin-bottom: 10px;
	height: $sliderHeight;
	
	&::before,
	&::after {
		@include white-gradient;
		content: "";
		height: $sliderHeight;
		position: absolute;
		width: calc(2* $slideWidth);
		z-index: 2;
	}
	
	&::after {
		right: 0;
		top: 0;
		transform: rotateZ(180deg);
	}

	&::before {
		left: 0;
		top: 0;
	}
	
	.slide-track {
		animation: scroll $animationSpeed linear infinite;
		display: flex;
		width: calc($slideWidth  * $nomberOfExhanges);

        .slide {
		height: $sliderHeight;
		width: $slideWidth;
        line-height: 25px;
        text-align: center;

            h1 {
                    font-size: 25px;
                    margin: 0;
                    padding: 0;
            }

            h2 {
                font-size: 20px;
            }

            .open {
                background-color: #5df542;
                font-size: 20px;
            }

            .close {
                background-color: #ed2424;
                font-size: 20px;
            }
	    }
	}
}
</style>