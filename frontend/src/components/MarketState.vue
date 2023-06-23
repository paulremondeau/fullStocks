<template>
    <div class="slider">
        <div class="slide-track" v-for="index in 2" :key="index">
            <div class="slide" v-for="exchangeData in props.marketData">
                <h1> {{ exchangeData.exchange }} </h1>
                <span :class="openOrClose(exchangeData)">
                    {{ exchangeData.isMarketOpen ? "OPEN" : "CLOSE" }}
                </span>
                <h2>
                    {{ exchangeData.isMarketOpen ? Duration.fromMillis(exchangeData.timeToClose).toFormat("hh:mm:ss")
                        : Duration.fromMillis(exchangeData.timeToOpen).toFormat("hh:mm:ss") }}
                </h2>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { Duration } from "luxon";

///// Timer /////
const currentTime = ref(0);
const updateCurrentTime = () => {
    if (!props.doUpdateMarket[0]) {

        if (currentTime.value > 1000) { // To avoid big big value and slow down
            currentTime.value = 0

        } else {

            currentTime.value++;
        }
    }
};
const updateTimeInterval = setInterval(updateCurrentTime, 1000);

// For the Caroussel
const numberOfExhanges = computed(() =>
    props.marketData.length
)


///// Functions /////
/**
 * Switch class between open or close
 * @param {Object} exchangeData Exchange market data informations.
 */
function openOrClose(exchangeData) {
    return exchangeData.isMarketOpen ? 'open' : 'close'
}

/**
 * Update the time displayed under exchange markets information.
 * @return {Promise} A promise to make sure all data are updated and only one emit will trigger.
 */
function updateTimerMarket() {
    return new Promise((resolve, reject) => {
        // If updateMarket is false
        if (!props.doUpdateMarket[0]) {
            for (const exchangeData of props.marketData) {
                let indexData = props.marketData.indexOf(exchangeData)
                if (exchangeData.isMarketOpen) {
                    exchangeData.timeToClose -= 1000;
                    if (exchangeData.timeToClose <= 0.99) {

                        // This will trigger the emit and stop the updating
                        props.doUpdateMarket[0] = true

                    } else {
                        props.marketData[indexData] = exchangeData
                    }
                } else {
                    exchangeData.timeToOpen -= 1000;
                    if (exchangeData.timeToOpen <= 0.99) {

                        // This will trigger the emit and stop the updating
                        props.doUpdateMarket[0] = true

                    } else {
                        props.marketData[indexData] = exchangeData
                    }
                }
            }
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
    marketData: Object,
    doUpdateMarket: Object,

})

///// Emits /////
const emit = defineEmits(["updateMarket"])

// Timer decreasing event
watch(currentTime, () => {
    updateTimerMarket()
        .then((res) => {
            // If updateMarket is true
            if (props.doUpdateMarket[0]) {
                emit('updateMarket')
            }
        })
}
)

</script>


<style scoped lang="scss">
// @mixin white-gradient {
//     background: linear-gradient(to right, rgba(255, 255, 255, 1) 0%, rgba(255, 255, 255, 0) 100%);
// }
@mixin left-gradient {
    background: linear-gradient(to right, rgba(241, 238, 238, 1) 0%, rgba(241, 238, 238, 0) 100%);
}

@mixin right-gradient {
    background: linear-gradient(to right, rgba(209, 210, 226, 1) 0%, rgba(209, 210, 226, 0) 100%);
}

// Scroll adapts to number of child component to make it look continuous
$numberOfExhanges: v-bind('numberOfExhanges');
$animationSpeed: 40s;
$slideWidth: 100px;

// Animation
@keyframes scroll {
    0% {
        transform: translateX(0);
    }

    100% {
        transform: translateX(calc(-1 * $slideWidth * $numberOfExhanges))
    }
}

// Styling
.slider {
    display: flex;
    margin: 0;
    padding: 0;
    overflow: hidden;
    height: 100%;


    &::before,
    &::after {
        // @include white-gradient;
        // content: "";
        height: 100%;
        position: absolute;
        width: calc(2* $slideWidth);
        z-index: 2;
    }

    &::after {
        @include right-gradient;
        content: "";
        right: 0;
        top: 0;
        transform: rotateZ(180deg);
    }

    &::before {
        @include left-gradient;
        content: "";
        left: 0;
        top: 0;
    }

    .slide-track {
        animation: scroll $animationSpeed linear infinite;
        display: flex;
        width: calc($slideWidth * $numberOfExhanges);

        .slide {

            width: $slideWidth;
            line-height: 15px;
            text-align: center;

            h1 {
                font-size: 20px;

            }

            h2 {
                font-size: 15px;

            }

            .open {
                background-color: #7eff68fd;
                font-size: 15px;

            }

            .close {
                background-color: #ff6262;
                font-size: 15px;
            }
        }
    }
}
</style>