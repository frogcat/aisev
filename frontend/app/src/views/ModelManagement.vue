<template>
  <div class="container-bg">
    <!-- Header -->
    <Header :breadcrumbs="breadcrumbs" />
    <main class="container">
      <section class="card">
        <h2>{{ $t("aiInformationManagement") }}</h2>
        <div class="table-header">
          <button
            class="delete-btn"
            @click="deleteSelectedModel"
            :disabled="selectedModelId === null"
          >
            {{ $t("deleteBtn") }}
          </button>
        </div>
        <div>
          <table>
            <thead>
              <tr>
                <th></th>
                <th>{{ $t("id") }}</th>
                <th>{{ $t("aiInformationLabel") }}</th>
                <th>{{ $t("aiInformationName") }}</th>
                <th>{{ $t("url") }}</th>
                <th>{{ $t("apiKey") }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="model in pagedModels" :key="model.id">
                <td>
                  <input
                    type="radio"
                    name="selectedModel"
                    :value="model.id"
                    v-model="selectedModelId"
                  />
                </td>
                <td>{{ model.id }}</td>
                <td>{{ model.name }}</td>
                <td>{{ model.model_name }}</td>
                <td>{{ model.url }}</td>
                <td>{{ maskApiKey(model.apiKey) }}</td>
              </tr>
            </tbody>
          </table>
          <div class="pagination">
            <button @click="prevPage" :disabled="currentPage === 1">
              {{ $t("previousPage") }}
            </button>
            <span> {{ currentPage }} / {{ totalPages }} </span>
            <button @click="nextPage" :disabled="currentPage === totalPages">
              {{ $t("nextPage") }}
            </button>
          </div>
        </div>
      </section>

      <div class="tab-switcher">
        <button
          :class="{ active: activeTab === 'register' }"
          @click="activeTab = 'register'"
        >
          {{ $t("aiInformationRegistration") }}
        </button>
        <button
          :class="{ active: activeTab === 'update' }"
          @click="activeTab = 'update'"
        >
          {{ $t("aiInformationUpdate") }}
        </button>
      </div>

      <div v-if="activeTab === 'register'" class="card" style="margin-top: 0">
        <h3>{{ $t("aiInformationRegistrationTitle") }}</h3>
        <div class="form-group">
          <label>{{ $t("aiInformationLabel") }}</label>
          <input v-model="registerForm.name" type="text" required />
        </div>
        <div class="form-group">
          <label>{{ $t("aiInformationName") }}</label>
          <input v-model="registerForm.model_name" type="text" required />
        </div>
        <div class="form-group">
          <label>{{ $t("url") }}</label>
          <input v-model="registerForm.url" type="text" required />
        </div>
        <div class="form-group">
          <label>{{ $t("apiKey") }}</label>
          <input v-model="registerForm.apiKey" type="text" />
        </div>
        <div class="form-group">
          <!-- Removed prompt format -->
        </div>
        <button class="regist-btn" @click="registerModel">
          {{ $t("register") }}
        </button>
      </div>

      <div v-if="activeTab === 'update'" class="card" style="margin-top: 0">
        <h3>{{ $t("aiInformationUpdated") }}</h3>
        <div class="form-group">
          <label>{{ $t("updateTargetAiInformationLabel") }}</label>
          <select v-model="updateForm.id">
            <option v-for="model in models" :key="model.id" :value="model.id">
              {{ model.id }}: {{ model.name }}
            </option>
          </select>
        </div>
        <div class="form-group">
          <label>{{ $t("aiInformationLabel") }}</label>
          <input v-model="updateForm.name" type="text" required />
        </div>
        <div class="form-group">
          <label>{{ $t("aiInformationName") }}</label>
          <input v-model="updateForm.model_name" type="text" required />
        </div>
        <div class="form-group">
          <label>{{ $t("url") }}</label>
          <input v-model="updateForm.url" type="text" required />
        </div>
        <div class="form-group">
          <label>{{ $t("apiKey") }}</label>
          <input v-model="updateForm.apiKey" type="text" />
        </div>
        <div class="form-group">
          <!-- Removed prompt format -->
        </div>
        <button class="regist-btn" @click="updateModel">
          {{ $t("update") }}
        </button>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute } from "vue-router";
import Header from "../components/Header.vue";

const { t } = useI18n();
const route = useRoute();

const breadcrumbs = computed(() => {
  const from = route.query.from;
  if (from === "definer-home") {
    return [
      { label: "home", link: "/" },
      { label: "evaluationDefinerHomeTitle", link: "/definer-home" },
      { label: "modelManagementScreen" },
    ];
  } else {
    // Default is evaluator-home
    return [
      { label: "home", link: "/" },
      { label: "evaluatorHomeTitle", link: "/evaluator-home" },
      { label: "modelManagementScreen" },
    ];
  }
});

// Retrieve model list from API
const models = ref([]);

async function fetchModels() {
  try {
    const res = await fetch("http://localhost:8000/ai_models", {
      method: "GET",
      headers: { "Content-Type": "application/json" },
    });
    const data = await res.json();
    models.value = Array.isArray(data.ai_models)
      ? data.ai_models
      : Array.isArray(data)
      ? data
      : [];
  } catch (e) {
    console.error(t("modelListRetrievalFailed"), e);
    models.value = [];
  }
}

onMounted(fetchModels);

const itemsPerPage = 5;
const currentPage = ref(1);
const totalPages = computed(() =>
  Math.ceil(models.value.length / itemsPerPage)
);

const pagedModels = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage;
  return models.value.slice(start, start + itemsPerPage);
});

// modelsが更新されたときにcurrentPageを最終ページに自動で移動
watch(
  () => models.value.length,
  (newLen: number, oldLen: number) => {
    if (newLen !== oldLen && newLen > 0) {
      currentPage.value = totalPages.value;
    } else if (newLen === 0) {
      currentPage.value = 1;
    }
  }
);

function prevPage() {
  if (currentPage.value > 1) currentPage.value--;
}
function nextPage() {
  if (currentPage.value < totalPages.value) currentPage.value++;
}

const activeTab = ref("register");

// registerForm
const registerForm = ref({
  name: "",
  model_name: "",
  url: "",
  apiKey: "",
  promptFormat: "",
  basicAuth: false,
});

// watch for changes in registerForm and update the model
function registerModel() {
  if (!registerForm.value.name) return alert(t("aiModelNameRequired"));
  // Check for duplicates
  const isDuplicate = models.value.some(
    (m: any) => m.name === registerForm.value.name
  );
  if (isDuplicate) {
    alert(t("nameAlreadyUsed"));
    return;
  }
  const newId = models.value.length
    ? Math.max(...models.value.map((m: any) => m.id)) + 1
    : 1;
  const payload = { id: newId, ...registerForm.value };
  console.log("登録データ:", JSON.stringify(payload, null, 2));
  fetch("http://localhost:8000/ai_models", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  })
    .then((res) => res.json())
    .then((data) => {
      console.log("APIレスポンス:", data);
      fetchModels(); // Reacquired after registration
      Object.assign(registerForm.value, {
        name: "",
        model_name: "",
        url: "",
        apiKey: "",
        promptFormat: "",
        basicAuth: false,
      });
      currentPage.value = totalPages.value;
      alert(t("registered"));
    })
    .catch((err) => console.error(t("apiError"), err));
}

const updateForm = ref({
  id: null as number | null,
  name: "",
  model_name: "",
  url: "",
  apiKey: "",
  promptFormat: "",
  basicAuth: false,
});
watch(
  () => updateForm.value.id,
  (id: number | null) => {
    const m = models.value.find((m: any) => m.id === id);
    if (m) Object.assign(updateForm.value, m);
  }
);

// updateForm
function updateModel() {
  if (updateForm.value.id === null) {
    alert(t("selectUpdateTargetId"));
    return;
  }
  // Check for duplicates (excluding self)
  const isDuplicate = models.value.some(
    (m: any) => m.id !== updateForm.value.id && m.name === updateForm.value.name
  );
  if (isDuplicate) {
    alert(t("nameAlreadyUsed"));
    return;
  }
  const payload = { ...updateForm.value };
  console.log("更新データ:", JSON.stringify(payload, null, 2));
  fetch(`http://localhost:8000/ai_models/${updateForm.value.id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  })
    .then((res) => res.json())
    .then((data) => {
      console.log("APIレスポンス:", data);
      fetchModels(); // Reacquired after update
      alert(t("updated"));
    })
    .catch((err) => console.error(t("apiError"), err));
}

const selectedModelId = ref<number | null>(null);

async function deleteSelectedModel() {
  if (selectedModelId.value === null) {
    alert(t("selectModelToDelete"));
    return;
  }
  if (!confirm(t("confirmDelete"))) return;
  try {
    const res = await fetch(
      `http://localhost:8000/ai_models/${selectedModelId.value}`,
      {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
      }
    );
    if (!res.ok) throw new Error(t("deleteApiError"));
    await fetchModels();
    selectedModelId.value = null;
    alert(t("deleted"));
  } catch (e) {
    console.error(t("deletionFailed"), e);
    alert(t("deleteFailed"));
  }
}

function maskApiKey(apiKey: string): string {
  if (!apiKey) return "";
  return apiKey.length <= 5 ? apiKey : apiKey.slice(0, 5) + "*******";
}
</script>

<style scoped>
.tab-switcher {
  margin-top: 5rem;
  display: flex;
}
.tab-switcher button {
  padding: 0.5rem 1.5rem;
  border: none;
  background: var(--color-btn-secondary);
  color: var(--color-btn-text);
  border-radius: 6px 6px 0 0;
  cursor: pointer;
  font-weight: bold;
  transition: background 0.2s, color 0.2s;
}
.tab-switcher button.active {
  background: var(--color-btn-main);
  color: var(--color-btn-text);
}

.form-group {
  margin-bottom: 1rem;
}
.form-group label {
  display: block;
  margin-bottom: 0.5rem;
}
input[type="text"],
select,
textarea {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  font-size: 1rem;
}
</style>
