<script setup lang="ts">
// App.vue
</script>

<template>
  <div class="app">
    <router-view></router-view>
  </div>
</template>

<style>
.app {
  font-family: var(--font-family, Arial, sans-serif);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: var(--color-text-main);
  margin: 0;
  padding: 0;
  background: var(--color-bg-main);
}

/* Animation */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
