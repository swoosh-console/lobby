<script>
export default {
  props: ['info']
}
</script>

<template>
  <div class="loader"><i class="loader-icon fa-solid fa-cog fa-spin-snap"></i><br><p class="loader-text">{{ info }}</p></div>
</template>

<style>
.loader {
  position: absolute;
  background-color: rgba(0,0,0,0.75);
  top: 0px;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 4;
  text-align: center;
  color: rgb(70, 68, 73);
}

.loader-icon {
    font-size: 50vh;
    margin-top: 20vh;
}

.loader-text {
    background-color: black;
    margin-top: 5vh;
    font-size: 5vh;
    color: white;
    text-shadow: 1px 1px black;
    white-space: pre-wrap;
}
</style>
