<template>
  <div class="container-bg">
    <Header :breadcrumbs="breadcrumbs" />
    <div class="container">
      <h2 class="page-title">{{ $t("evaluationDefinerHomeTitle") }}</h2>
      <nav class="nav-links">
        <ul>
          <li>
            <router-link to="/dataset-register" class="nav-link">{{
              $t("datasetRegisterScreen")
            }}</router-link>
          </li>
          <li>
            <router-link to="/qualitative-definition" class="nav-link">{{
              $t("qualitativeDefinitionScreen")
            }}</router-link>
          </li>
          <li>
            <router-link
              :to="{
                path: '/model-management',
                query: { from: 'definer-home' },
              }"
              class="nav-link"
            >
              {{ $t("modelManagementScreen") }}
            </router-link>
          </li>
          <li>
            <router-link to="/eval-design" class="nav-link">{{
              $t("evalDesignScreen")
            }}</router-link>
          </li>
        </ul>
      </nav>
    </div>
  </div>
</template>

<script setup lang="ts">
import Header from "../components/Header.vue";
const breadcrumbs = [
  { label: "home", link: "/" },
  { label: "evaluationDefinerHomeTitle" },
];
</script>

<style scoped>
ul {
  list-style: none;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 2rem;
  width: 100%;
  max-width: 400px;
  align-items: center;
}
li {
  margin: 0;
  width: 100%;
  display: flex;
  justify-content: center;
}
@media (max-width: 700px) {
  .container {
    max-width: 98vw;
    padding: 0.5rem;
  }
  ul {
    max-width: 98vw;
  }
  .nav-link {
    font-size: 1rem;
    padding: 1rem 0.5rem;
  }
}
</style>
