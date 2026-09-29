<script>
export default {
  props: ['currentVersion'],
  data() {
    return {
      year: new Date().getFullYear()
    }
  }
}
</script>

<template>
  <div class="footer">Version: {{currentVersion}} &copy; 2025-{{ year }} Oscar Granfeldt</div>
</template>

<style>
.footer {
  position: absolute;
  bottom: 0px;
  left: 0;
  width: 100%;
  height: 16px;
  background-color: rgba(184, 171, 183, 0.5);
  border-top: 1px solid rgb(143, 110, 137);
  border-bottom: 1px solid rgb(52, 40, 50);
  color: rgb(189, 178, 178);
  font-size: small;
}

</style>
