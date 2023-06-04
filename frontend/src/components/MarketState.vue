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

// TODO : régler le prolbème du timer -> utilisation de pinia ?
// Voir comment régler le problème du enable
// Voir si il faudrait passer par le parent

import {reactive, ref, watch, computed} from 'vue'
import { Duration } from "luxon";

const props = defineProps({
  marketData: Object
})

// Emit event : if one timer comes to 0 -> trigger the API call
const emit = defineEmits(["updateMarket"])

// For the Caroussel
const nomberOfExhanges = computed(() => 
    props.marketData.length
)

// Timer for the countdown before open/close
const timerEnabled = ref(true)
const timerCount = ref(0)
function increaseTimer() {
    if (timerEnabled.value) {
    setTimeout(() => {
        timerCount.value += 1;
    }, 1000);
    }
}
increaseTimer()


// async function updateTimers() {
//     for (const exchangeData of props.marketData){
//         updateTimer(exchangeData)
//     }
// }

// function updateTimer(exchangeData) {
//     let indexData = props.marketData.indexOf(exchangeData)
//     if (exchangeData.isMarketOpen) {     
//         exchangeData.timeToClose -= 1000;
//         if (exchangeData.timeToClose < 0){
//             emit('updateMarket')
//             return
//         } else {    
//         props.marketData[indexData] = exchangeData
//         }
//     } else {
//         exchangeData.timeToOpen -= 1000;
//         if (exchangeData.timeToOpen < 0){
//             emit('updateMarket')
//             return
//         } else {
//         props.marketData[indexData] = exchangeData
//         }
//     }
// }


// Timer decreasing event
watch(timerCount, increaseTimer)
watch(timerCount, () => {
    for (const exchangeData of props.marketData){
        let indexData = props.marketData.indexOf(exchangeData)
        if (exchangeData.isMarketOpen) {     
            exchangeData.timeToClose -= 1000;
            if (exchangeData.timeToClose < 0){
                timerEnabled.value = false
                emit('updateMarket')
                return
            } else {
            props.marketData[indexData] = exchangeData
            }
        } else {
            exchangeData.timeToOpen -= 1000;
            if (exchangeData.timeToOpen < 0){
                timerEnabled.value = false
                emit('updateMarket')
                return
            } else {
            props.marketData[indexData] = exchangeData
            }
        }
    }
})

// Open or Close style
function openOrClose (exchangeData) {
    return exchangeData.isMarketOpen ? 'open' : 'close'
}

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