<template>
  <div>
    <div class="tab-switcher">
      <button
        v-for="(d, idx) in details"
        :key="idx"
        :class="['tab-btn', { active: idx === activeTab }]"
        @click="$emit('changeTab', idx)"
      >
        {{ d.name }}
      </button>
    </div>
    <div class="tab-content">
      <div v-if="details[activeTab]">
        <div class="detail-info-block">
          <div>
            <strong>{{ $t("evaluationName") }}:</strong>
            {{ details[activeTab].name }}
          </div>
          <div>
            <strong>{{ $t("targetModelName") }}:</strong>
            {{ details[activeTab].modelName }}
          </div>
          <div>
            <strong>{{ $t("judgeModelName") }}:</strong>
            {{ details[activeTab].judgeModelName }}
          </div>
          <div>
            <strong>{{ $t("definitionName") }}:</strong>
            {{ details[activeTab].definitionName }}
          </div>
          <div>
            <strong>{{ $t("evaluatedAt") }}:</strong>
            {{ details[activeTab].evaluatedAt }}
          </div>
        </div>
        <button
          class="regist-btn"
          style="margin-top: 1.5rem"
          @click="$emit('goDetail', details[activeTab].id)"
        >
          {{ $t("goToDetailScreen") }}
        </button>
      </div>
      <div v-else>
        <p>{{ $t("noDetailInfo") }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { EvaluationCriteriaConst } from "../constants/EvaluationCriteria";

const criteriaList = EvaluationCriteriaConst.LIST;

const props = defineProps<{
  details: Array<{
    id: number;
    name: string;
    modelName: string;
    judgeModelName: string;
    definitionName: string;
    evaluatedAt: string;
    // Added: Correct count, incorrect count, and accuracy for each perspective
    criteriaStats?: Array<{
      correct: number;
      incorrect: number;
      accuracy: number; // 0~1
    }>;
  }>;
  activeTab: number;
}>();
const emit = defineEmits(["changeTab", "goDetail"]);
</script>

<style scoped>
/* tab button */
.tab-switcher {
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
.tab-btn {
  padding: 8px 16px;
  border: none;
  background: var(--color-bg-secondary);
  cursor: pointer;
  border-radius: 4px 4px 0 0;
  font-weight: bold;
  color: var(--color-text-main);
  transition: background 0.2s, color 0.2s;
}
.tab-btn.active {
  background: var(--color-btn-main);
  color: var(--color-text-main);
}
/* tab content */
.tab-content {
  background: var(--color-bg-accent);
  border: 1px solid var(--color-border);
  border-radius: 4px 4px 0 0;
  padding: 8px;
  min-height: 80px;
  color: var(--color-text-main);
}
.tab-content table {
  max-width: 90%;
  min-width: 400px;
  margin: 2rem auto 0 auto;
  overflow: hidden;
  width: 100%;
}

.tab-content th,
.tab-content td {
  padding: 0.5rem 1rem;
  text-align: left;
}

.tab-content th {
  font-weight: bold;
}

.detail-info-block {
  background: var(--color-bg-card);
  border-radius: 1rem;
  padding: 1.5rem 2rem;
  color: var(--color-text-main);
  font-size: 1.1rem;
}
</style>
