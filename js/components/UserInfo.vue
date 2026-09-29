<script>
export default {
  props: ['info']
}
</script>

<template>
  <div v-if="info" class="user-info">{{info}}</div>
</template>

<style>
.user-info {
  position: absolute;
  top: 8vh;
  left: 0;
  width: 100%;
  height: 20px;
  background-color: rgba(184, 171, 183, 0.5);
  border-top: 1px solid rgb(143, 110, 137);
  border-bottom: 1px solid rgb(52, 40, 50);
  color: rgb(189, 178, 178);
  text-align: center;
  font-weight: bold;
  letter-spacing: 0px;
  animation: blinker 2s linear infinite, stretcher 1s linear infinite;
  z-index: 3;
}

@keyframes blinker {
  50% {
    color: rgba(255, 152, 152, 0.5);
    letter-spacing: 0.5px;
  }
}

@keyframes stretcher {
  0% {
    letter-spacing: 0px;
  }
  50% {
    letter-spacing: 0.1px;
  }
  100% {
    letter-spacing: 0px;
  }
}
</style>
