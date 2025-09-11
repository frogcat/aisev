<template>
  <div class="evaluation-result-list">
    <h4>{{ $t("evaluationResultList") }}</h4>
    <table>
      <thead>
        <tr>
          <th>{{ $t("select") }}</th>
          <th>{{ $t("evaluatedAt") }}</th>
          <th>{{ $t("evaluationName") }}</th>
          <th>{{ $t("targetAIModel") }}</th>
          <th>{{ $t("definitionName") }}</th>
          <th>{{ $t("evaluationStatus") }}</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="result in sortedResults" :key="result.id">
          <td>
            <input
              type="checkbox"
              :checked="selectedIds.includes(result.id)"
              :disabled="
                !selectedIds.includes(result.id) &&
                selectedIds.length >= (props.maxSelectable ?? 2)
              "
              @change="toggleSelect(result.id)"
            />
          </td>
          <td>{{ result.evaluatedAt }}</td>
          <td>{{ result.name }}</td>
          <td>{{ result.modelName }}</td>
          <td>{{ result.definitionName }}</td>
          <td>{{ result.status }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from "vue";

const props = defineProps<{
  results: Array<{
    id: number;
    name: string;
    modelName: string;
    judgeModelName: string;
    definitionName: string;
    evaluatedAt: string;
    status: string;
    radarData: number[];
  }>;
  selectedIds: number[];
  maxSelectable?: number; // ADD: Maximum number of selections
}>();
const emit = defineEmits(["selectResult"]);

console.log("EvaluationResultList props:", props.results);

// Sorted array (descending order by evaluation date)
const sortedResults = computed(() =>
  [...props.results].sort(
    (a, b) =>
      new Date(b.evaluatedAt).getTime() - new Date(a.evaluatedAt).getTime()
  )
);

// ID of the latest result
const latestId = computed(() => {
  if (!props.results.length) return null;
  return sortedResults.value[0].id;
});

// Set to select only the latest result on initial display
onMounted(() => {
  if (
    props.results.length > 0 &&
    latestId.value !== null &&
    (props.selectedIds.length === 0 ||
      !props.selectedIds.includes(latestId.value))
  ) {
    emit("selectResult", [latestId.value]);
  }
});

function toggleSelect(id: number) {
  let newIds = [...props.selectedIds];
  const max = props.maxSelectable ?? 2;
  if (newIds.includes(id)) {
    newIds = newIds.filter((i) => i !== id);
  } else if (newIds.length < max) {
    newIds.push(id);
  }
  emit("selectResult", newIds);
}
</script>

<style scoped>
th,
td {
  padding: 8px 12px;
  text-align: left;
  color: var(--color-text-main);
}
th {
  background: var(--color-tbl-header);
}
input[type="checkbox"] {
  width: 18px;
  height: 18px;
}
</style>
