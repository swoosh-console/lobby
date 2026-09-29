<script>
const buttons = [{
  text: 'Refresh',
  icon: 'fa-solid fa-arrows-rotate',
  action: 'refresh'
},{
  text: 'Update',
  icon: 'fa-solid fa-download',
  action: 'update'
},{
  text: 'Settings',
  icon: 'fa-solid fa-gears',
  action: 'settings'
}, {
  text: 'Shutdown',
  icon: 'fa-solid fa-power-off',
  action: 'shutdown'
}]

export default {
  props: ['updateAvailable'],
  emits: ['onAction'],
  data() {
    return {
      hover : Array.apply(null, {length: buttons.length}).map(() => false),
      currentIndex : -1,
      buttons : buttons,
      headerDisabled : true
    }
  },
  methods: {
    getAvailableButtons() {
      return buttons.filter(b => b.text != "Update" || this.updateAvailable);
    },
    navigateLeft() {
        this.currentIndex = Math.max(0, this.currentIndex - 1)
    },
    navigateRight() {
        this.currentIndex = Math.min(buttons.length - 1, this.currentIndex + 1)
    },
    navigateUp() {
      this.headerDisabled = false;
      this.currentIndex = this.getAvailableButtons().findIndex(b => b.action === "settings");
    },
    navigateDown() {
      this.headerDisabled = true;
      this.currentIndex = -1;
    },
    runAction(buttonIndex) {
      let action = this.getAvailableButtons()[buttonIndex].action;
      this.$emit('onAction', action);
    },
    onKeydown(event) {
      if (event.key == "ArrowUp") {
        this.navigateUp();
      }
      if (this.headerDisabled) {
        return;
      }
      if (event.key == "Enter") {
        this.runAction(this.currentIndex);
      } else if (event.key == "ArrowLeft") {
        this.navigateLeft();
      } else if (event.key == "ArrowRight") {
        this.navigateRight();
      } else if (event.key == "ArrowDown") {
        this.navigateDown();
      }
    },
    gamepadHandler(event) {
      let self = this;
      const gamepad = navigator.getGamepads()[event.gamepad.index];
      let gamepadState = {
        horizontalState: 0,
        verticalState: 0,
        buttonState: 1,
        exitCounter: 0
      };
      let poller = () => {
        if (gamepad.connected) {
          if (!document.hasFocus()) {
            setTimeout(poller, 1000);
            let buttonCount = gamepad.buttons.filter((b) => b.pressed).length;
            if (buttonCount >= 5) {
              gamepadState.exitCounter++;
              gamepadState.buttonState = 1;
            } else {
              gamepadState.exitCounter = 0;
            }
            if (gamepadState.exitCounter == 3) {
              this.$emit('onAction', 'exit');
            }
            return;
          }
          setTimeout(poller, 25);
          gamepad.axes.forEach((axis, index) => {
            if (index == 0 && !self.headerDisabled) {
              let newHorizontalState = axis > 0.5 ? 1 : (axis < -0.5 ? -1 : 0);
              if (newHorizontalState == 1 && gamepadState.horizontalState != 1) {
                self.navigateRight();
              } else if (newHorizontalState == -1 && gamepadState.horizontalState != -1) {
                self.navigateLeft();
              }
              gamepadState.horizontalState = newHorizontalState;
            } else if (index == 1) {
              let newVerticalState = axis > 0.5 ? 1 : (axis < -0.5 ? -1 : 0);
              if (newVerticalState == 1 && gamepadState.verticalState != 1) {
                self.navigateDown();
              } else if (newVerticalState == -1 && gamepadState.verticalState != -1) {
                self.navigateUp();
              }
              gamepadState.verticalState = newVerticalState;
            }
          });
          let newButtonState = 0;
          gamepad.buttons.forEach((button, index) => {
            newButtonState = button.pressed ? 1 : newButtonState;
          });
          if (newButtonState == 1 && gamepadState.buttonState == 0 && !self.headerDisabled) {
            self.runAction();
          }
          gamepadState.buttonState = newButtonState;
        }
      }
      poller();
    },
    isMouseEnabled() {
      return document.body.style.cursor!='none';
    }
  },
  computed: {
    availableButtons() {
      return this.getAvailableButtons()
    }
  },
  mounted() {
    document.addEventListener( "keydown", this.onKeydown );
    window.addEventListener("gamepadconnected", this.gamepadHandler);
  },
  unmounted() {
    document.removeEventListener( "keydown", this.onKeydown );
    window.removeEventListener("gamepadconnected", this.gamepadHandler);
  }
}
</script>

<template>
  <div class="header">
    <div class="logo"><img src="images/favicon.png" style="height: 3.5vh;">SWOOSH</div>
    <div v-for="(b, index) in availableButtons" class="button-parent">
      <div class="button active-button" 
        @mouseenter="hover[index]=isMouseEnabled()"
        @mouseleave="hover[index]=false"
        @click="runAction(index)">
        <i :class="{ [b.icon] : true, 'fa-bounce active-icon' : index == currentIndex || hover[index]}"></i>
      </div>
      <p v-if="index == currentIndex" class="button-info">{{ b.text }}</p>
    </div>
  </div>
</template>

<style scoped>
@font-face {
  font-family: 'retro';
  src: url('fonts/ARCADECLASSIC.TTF'); 
}

.header {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 8vh;
  background-color: rgb(80, 80, 80);
  display: flex;
  justify-content: center;
  z-index: 2;
}

.logo {
  display: flex;
  position: absolute;
  line-height: 4vh;
  padding: 2px;
  left: 0;
  top: 0;
  height: 4vh;
  z-index: 3;
  font-family: 'retro';
}

.button-parent {
  margin-left: 16px;
  margin-right: 16px;
  margin-top: 8px;
  height: 5.75vh;
  text-align: center;
}

.button {
  background-color: rgb(70, 68, 73);
  border-radius: 4px;
  padding: 0.75vh;
  width: 64px;
}

.button-info {
  margin-top: 0px;
  color: rgb(245, 245, 250);
  text-shadow: 3px 3px 6px black;
  font-weight: bold;
}

i {
  color: rgb(167, 167, 187);
  font-size: 4vh;
}

.active-button {
  background-color: rgb(106, 102, 110);
}

.active-icon {
  color: rgb(156, 148, 190);
}



</style>
