<template>
  <header class="header">
    <div class="header-content">
      <div class="breadcrumbs">
        <span v-for="(crumb, idx) in breadcrumbs" :key="idx">
          <template v-if="idx !== 0"> &gt; </template>
          <router-link v-if="crumb.link" :to="crumb.link">{{
            $t(crumb.label)
          }}</router-link>
          <span v-else>{{ $t(crumb.label) }}</span>
        </span>
      </div>
      <div class="lang-switch">
        <button
          @click="switchLanguage('ja')"
          :class="{ active: currentLang === 'ja' }"
        >
          {{ $t("japanese") }}
        </button>
        <button
          @click="switchLanguage('en')"
          :class="{ active: currentLang === 'en' }"
        >
          {{ $t("english") }}
        </button>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useI18n } from "vue-i18n";
// import { useRoute } from 'vue-router';

defineProps<{ breadcrumbs: Array<{ label: string; link?: string }> }>();

const { locale } = useI18n();
// const route = useRoute();
const currentLang = computed(() => locale.value);

function switchLanguage(lang: string) {
  locale.value = lang;
}
</script>

<style scoped>
.header {
  width: 100%;
  min-width: 100%;
  background-color: var(--color-header-bg);
  color: var(--color-text-main);
  padding-top: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--color-border);
  box-sizing: border-box;
  margin-bottom: 20px;
}
.header-content {
  max-width: 100vw;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 2rem;
  box-sizing: border-box;
}
.breadcrumbs {
  font-size: 1rem;
  color: var(--color-text-main);
}
.breadcrumbs a {
  color: var(--color-text-accent);
  text-decoration: none;
}
.breadcrumbs a:hover {
  text-decoration: underline;
}
.lang-switch button {
  margin-left: 8px;
  padding: 4px 12px;
  border: none;
  background: var(--color-header-btn-bg);
  color: var(--color-header-btn-text);
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
}
.lang-switch button.active {
  background: var(--color-pushed-btn-bg);
  color: var(--color-pushed-btn-text);
}
@media (max-width: 600px) {
  .header-content {
    flex-direction: column;
    align-items: flex-start;
    padding: 0 1rem;
  }
  .lang-switch {
    margin-top: 10px;
  }
}
</style>
