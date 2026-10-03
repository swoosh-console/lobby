<script setup>
import { ref, defineEmits, onMounted, onUnmounted } from 'vue';
import { Carousel, Slide, Navigation } from 'vue3-carousel';

const emit = defineEmits(['onRunDefault', 'onSelect', 'onEnable', 'onDisable']);

const appInfo = ref({plain: null, content: ''});

const currentSlide = ref(0);

const appSlides = ref([]);

const carouselDisabled = ref(false);

const appPressed = ref(-1);

const carouselConfig = {
  itemsToShow: 3,
  wrapAround: true,
  enabled: true,
  mouseDrag: false,
  mouseWheel: false,
};

const appCarousel = ref();

const handleInit = () => {
};

const handleSlideStart = (data) => {
  let newIndex = data.slidingToIndex;
  if (newIndex < 0) {
    newIndex += appSlides.value.length;
  } else if (newIndex >= appSlides.value.length) {
    newIndex -= appSlides.value.length;
  }
  let app = appSlides.value.find(app => app.index == newIndex);
  loadApp(app);
};

const loadApp = (app) => {
  emit('onSelect', app);
  axios.get('/info/' + app.id).then((response) => {
    appInfo.value = {
      plain : response.headers['content-type'].includes('text/plain'),
      content : response.data
    };
  }).catch((error) => {
    appInfo.value = {plain: null, content: ''};
  });
}

const getCurrentApp = () => {
  return appSlides.value.find(app => app.index == appCarousel.value.currentSlide);
};

const runDefault = () => {
  if (appPressed.value == -1) {
    setTimeout(() => {
      appPressed.value = -1;
    }, 3000);
    appPressed.value = appCarousel.value.currentSlide;
    emit('onRunDefault' /*, app */);
  }
};

const navigateLeft = () => {
  appCarousel.value.prev();
};

const navigateRight = () => {
  appCarousel.value.next();
};

const navigateUp = () => {
  carouselDisabled.value = true;
  emit('onDisable');
};

const navigateDown = () => {
  carouselDisabled.value = false;
  emit('onEnable');
};

const onKeydown = (event) => {
  if (event.key == "ArrowDown") {
    navigateDown();
  }
  if (carouselDisabled.value) {
    return;
  }
  if (event.key == "Enter") {
    runDefault();
  } else if (event.key == "ArrowLeft") {
    navigateLeft();
  } else if (event.key == "ArrowRight") {
    navigateRight();
  } else if (event.key == "ArrowUp") {
    navigateUp();
  }
};

const gamepadHandler = (event) => {
  const gamepad = navigator.getGamepads()[event.gamepad.index];
  let gamepadState = {
    horizontalState: 0,
    verticalState: 0,
    buttonState: 1,
  };
  let poller = () => {
    if (gamepad.connected) {
      if (!document.hasFocus()) {
        setTimeout(poller, 1000);
        gamepadState.buttonState = 1;
        return;
      }
      setTimeout(poller, 25);
      gamepad.axes.forEach((axis, index) => {
        if (index == 0 && !carouselDisabled.value) {
          let newHorizontalState = axis > 0.5 ? 1 : (axis < -0.5 ? -1 : 0);
          if (newHorizontalState == 1 && gamepadState.horizontalState != 1) {
            navigateRight();
          } else if (newHorizontalState == -1 && gamepadState.horizontalState != -1) {
            navigateLeft();
          }
          gamepadState.horizontalState = newHorizontalState;
        } else if (index == 1) {
          let newVerticalState = axis > 0.5 ? 1 : (axis < -0.5 ? -1 : 0);
          if (newVerticalState == 1 && gamepadState.verticalState != 1) {
            navigateDown();
          } else if (newVerticalState == -1 && gamepadState.verticalState != -1) {
            navigateUp();
          }
          gamepadState.verticalState = newVerticalState;
        }
      });
      let newButtonState = 0;
      gamepad.buttons.forEach((button, index) => {
        newButtonState = button.pressed ? 1 : newButtonState;
      });
      if (newButtonState == 1 && gamepadState.buttonState == 0 && !carouselDisabled.value) {
        runDefault();
      }
      gamepadState.buttonState = newButtonState;
    }
  }
  poller();
}

onMounted(() => {
  axios.get('/apps').then((response) => {
    let apps = response.data;
    apps.forEach((app, i) => {
      appSlides.value.push({
        index : i,
        id : app.id,
        title : app.title,
        subtitle : app.subtitle,
        platform : app.platform,
        category : app.category,
        cover: '/covers/' + app.id,
        soundtrack : '/soundtracks/' + app.id,
        run_sound : '/run_sounds/' + app.id,
        info: '/info/' + app.id,
      })
    });
    axios.get('/state').then((response) => {
      let state = response.data;
      let last_app = state['last_app'];
      let appSlide = appSlides.value.filter(as => as.id == last_app);
      if (appSlide.length > 0) {
        appCarousel.value.slideTo(appSlide[0].index, true);
        loadApp(appSlides.value[appSlide[0].index]);
      } else {
        loadApp(appSlides.value[0]);
      }
    }).catch((error) => {
      loadApp(appSlides.value[0]);
    });
  }).catch((error) => {

  });
  document.addEventListener( "keydown", onKeydown );
  window.addEventListener("gamepadconnected", gamepadHandler);
});

onUnmounted(() => {
  document.removeEventListener( "keydown", onKeydown );
  window.removeEventListener("gamepadconnected", gamepadHandler);
});

const getPlatformIcon = (platform) => {
  switch (new String(platform).toLowerCase()) {
    case "gc":
      return "images/gc.png"
    case "gba":
      return "images/gba.png"
    case "n64":
      return "images/n64.png";
    case "nes":
      return "images/nes.png"
    case "ps2":
      return "images/ps2.png"
    case "snes":
      return "images/snes.png"
    case "wii":
      return "images/wii.webp"
    case "wiiu":
      return "images/wiiu.png"
    default:
      return "images/unknown.png"
  }
}

const getPlatformName = (platform) => {
  switch (new String(platform).toLowerCase()) {
    case "gc":
      return "GameCube"
    case "gba":
      return "Game Boy Advance"
    case "n64":
      return "Nintendo 64";
    case "nes":
      return "Nintendo Entertainment System"
    case "ps1":
      return "Playstation";
    case "ps2":
      return "Playstation 2";
    case "ps3":
      return "Playstation 3";
    case "snes":
      return "Super Nintendo"
    case "wii":
      return "Wii"
    case "wiiu":
      return "Wii U"
    default:
      return "unknown platform"
  }
}

const getAppSummary = (app) => {
  if (app.platform) {
    if (app.category) {
      return app.category + " game for " + getPlatformName(app.platform);
    } else {
      return "Game for " + getPlatformName(app.platform);
    }
  }
  if (app.category) {
    return app.category + " game";
  } else {
    return "Game";
  }
}

</script>


<template>
  <Carousel ref="appCarousel" v-bind="carouselConfig" @init="handleInit" @slide-start="handleSlideStart" v-model="currentSlide">
    <Slide v-for="app in appSlides" :key="app.id">
      <p style="text-align: center; position: absolute; top: 20px;">
        <h1>{{ app.title }}</h1>
        <h2>{{ app.subtitle }}</h2>
        <img @dblclick="runDefault" class="cover" :class="{cover_start_animation:appPressed==app.index}" :src="app.cover" alt="image" :style="[app.index == appPressed || (carouselDisabled && app.index == currentSlide) ? {opacity: 0.5} : {}]" /><br>
        <div class="reflection-perspective" v-if="app.index == currentSlide">
          <img class="reflection" :src="app.cover" alt="image" />
        </div>
        <div class="info-header" v-if="app.index == currentSlide">
            <img class="info-header-icon" :src="getPlatformIcon(app.platform)">
            <span class="info-header-summary">{{getAppSummary(app)}}</span>
        </div>
        <div class="info" v-if="app.index == currentSlide && appInfo.content &&  appInfo.plain">{{appInfo.content}}</div>
        <div class="info" v-if="app.index == currentSlide && appInfo.content && !appInfo.plain" v-html="appInfo.content"></div>
      </p>
    </Slide>

    <template #addons>
      <Navigation />
    </template>
  </Carousel>
</template>


<style>
:root {
  --carousel-transition: 300ms;
  --carousel-opacity-inactive: 0.7;
  --carousel-opacity-active: 1;
  --carousel-opacity-near: 0.20;

}

.carousel {
  --vc-nav-background: rgba(255, 255, 255, 0.7);
  --vc-nav-border-radius: 100%;
  height: 100vh;
}

h1 {
  color: rgb(167, 167, 187);
}

h2 {
  color: rgb(156, 148, 190);
}

.cover {
  width: auto;
  height: 250px;
  margin-top: 8px;
}

.reflection-perspective {
  perspective: 180px;
  margin-top: 15%;
}


.reflection {
  width: auto;
  height: 250px;
  transform: scaleY(-1) rotateX(-45deg);
  opacity: 0.3;
  filter: blur(2px);
  mask-image: linear-gradient(transparent, black);
}

.info-header {
  text-align: left;
  position: relative;
  left: -25%;
  top: -200px;
  height: 50px;
  width: 150%;
  margin-top: -15%;
  background: rgba(92, 92, 92, 0.2);
  border-top-left-radius: 8px;
  border-top-right-radius: 8px;
  color: rgb(200, 199, 204);
}

.info-header-icon {
  margin-left: 10px; 
  margin-top: 1px;
  width: 48px; 
  height: 48px;
}

.info-header-summary {
  position: absolute;
  top: 17px;
  margin-left: 12px;
}

.info {
  text-align: left;
  position: relative;
  left: -25%;
  top: -200px;
  min-height: 50px;
  width: 150%;
  background: rgba(0,0,0,0.2);
  border-bottom-left-radius: 8px;
  border-bottom-right-radius: 8px;
  color: rgb(200, 199, 204);
  line-height: 150%;
  font-size: larger;
  overflow: scroll;
}

.carousel__viewport {
  perspective: 2000px;
  position: absolute;
  top: 10vh;
  height: 90vh;
}

.carousel__track {
  transform-style: preserve-3d;
}

.carousel__slide--sliding {
  transition:
    opacity var(--carousel-transition),
    transform var(--carousel-transition);
}

.carousel.is-dragging .carousel__slide {
  transition:
    opacity var(--carousel-transition),
    transform var(--carousel-transition);
}

.carousel__slide {
  opacity: var(--carousel-opacity-inactive);
  transform: translateX(10px) rotateY(-12deg) scale(0.9);
  /*align-items: unset;*/
}

.carousel__slide--prev {
  opacity: var(--carousel-opacity-near);
  transform: rotateY(0deg) scale(0.75);
}

.carousel__slide--active {
  opacity: var(--carousel-opacity-active);
  transform: rotateY(0) scale(1);
}

.carousel__slide--next {
  opacity: var(--carousel-opacity-near);
  transform: rotateY(-0deg) scale(0.75);
}

.carousel__slide--next ~ .carousel__slide {
  opacity: var(--carousel-opacity-inactive);
  transform: translateX(-10px) rotateY(12deg) scale(0.9);
}

.cover_start_animation {
  animation: start 0.2s linear;
}

@keyframes start {

    0%{
        transform: rotateY(0) scale(1);
    }

    50%{
        transform: rotateY(0) scale(0.95);
    }

    100%{
        transform: rotateY(0) scale(1);
    }

}
</style>
