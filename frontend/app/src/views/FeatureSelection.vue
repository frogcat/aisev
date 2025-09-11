<template>
  <div class="container-bg">
    <!-- Header -->
    <Header :breadcrumbs="breadcrumbs" />
    <div class="container">
      <h2 class="page-title">
        {{ $t("appTitle1") }}<br />{{ $t("appTitle2") }}
      </h2>
      <nav class="nav-links">
        <ul>
          <li>
            <router-link to="/definer-home" class="nav-link">{{
              $t("definerHome")
            }}</router-link>
          </li>
          <li>
            <router-link to="/evaluator-home" class="nav-link">{{
              $t("evaluatorHome")
            }}</router-link>
          </li>
          <li>
            <button @click="launchLLMEval" class="nav-link">
              {{ $t("autoRtToolHome") }}
            </button>
          </li>
        </ul>
      </nav>
      <div v-if="dbMessage" class="result-message db-message">
        {{ dbMessage }}
      </div>
    </div>
    <button class="db-init-btn" @click="showConfirmDialog">{{ $t("initializeDb") }}</button>

    <!-- Confirmation Modal -->
    <div v-if="showDialog" class="modal-overlay">
      <div class="modal-content">
        <h3>{{ $t("confirmDbInit") }}</h3>
        <div class="modal-buttons">
          <button class="confirm-btn" @click="confirmInitialization">
            {{ $t("yes") }}
          </button>
          <button class="cancel-btn" @click="cancelInitialization">
            {{ $t("no") }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useI18n } from "vue-i18n";
import Header from "../components/Header.vue";import { rtURL, initURL } from "../main.ts";

const { t } = useI18n();

// Breadcrumbs
const breadcrumbs = [{ label: "home" }];

async function launchLLMEval() {
  try {
    // Manager-backend API endpoint
    const res = await fetch(
    rtURL, 
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    });
    if (!res.ok) {
      throw new Error(`API呼び出し失敗 status: ${res.status}`);
    }
    const data = await res.json();
    if (!data.url) {
      throw new Error("API応答にURLが含まれていません");
    }
    // Navigate to the service URL
    window.location.href = data.url;
  } catch (e) {
    alert("起動に失敗しました: " + e);
  }
}

// DB initialization feature
const dbMessage = ref("");
const showDialog = ref(false);

function showConfirmDialog() {
  showDialog.value = true;
}

function cancelInitialization() {
  showDialog.value = false;
}

function confirmInitialization() {
  showDialog.value = false;
  callMigrateApi();
}

async function callMigrateApi() {
  try {
    const response = await fetch(
      initURL,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      }
    );
    if (!response.ok) throw new Error("API取得に失敗しました");
    const data = await response.json();
    // Use internationalized success message
    dbMessage.value = t("dbInitSuccess");
  } catch (err) {
    console.error(err);
    window.alert(t("dbInitFailed"));
    dbMessage.value = t("dbInitApiError");
  }
}
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
.db-init-btn {
  position: fixed;
  right: 2rem;
  bottom: 2rem;
  padding: 0.7rem 1.5rem;
  background: #2196f3;
  color: #fff;
  border: none;
  border-radius: 0.5rem;
  font-size: 1.1rem;
  cursor: pointer;
  z-index: 100;
}
.db-message {
  margin-top: 2rem;
  color: #1976d2;
  font-size: 1.1rem;
}

/* Modal styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
  max-width: 400px;
  width: 90%;
  text-align: center;
}

.modal-content h3 {
  margin: 0 0 1.5rem 0;
  color: #333;
  font-size: 1.2rem;
}

.modal-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.confirm-btn, .cancel-btn {
  padding: 0.75rem 2rem;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  transition: background 0.2s;
}

.confirm-btn {
  background: #2196f3;
  color: white;
}

.confirm-btn:hover {
  background: #1976d2;
}

.cancel-btn {
  background: #f5f5f5;
  color: #333;
  border: 1px solid #ddd;
}

.cancel-btn:hover {
  background: #e0e0e0;
}
</style>
