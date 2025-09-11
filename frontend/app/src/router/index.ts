import { createRouter, createWebHistory } from "vue-router";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "home",
      component: () => import("../views/FeatureSelection.vue"),
    },
    {
      path: "/definer-home",
      name: "definer-home",
      component: () => import("../views/EvaluationDefinerHome.vue"),
    },
    {
      path: "/evaluator-home",
      name: "evaluator-home",
      component: () => import("../views/EvaluatorHome.vue"),
    },
    {
      path: "/dataset-creation-assistance",
      name: "dataset-creation-assistance",
      component: () => import("../views/DatasetCreationAssistance.vue"),
    },
    {
      path: "/eval-design",
      name: "eval-design",
      component: () => import("../views/EvaluationDefinition.vue"),
    },
    {
      path: "/qualitative-definition",
      name: "qualitative-definition",
      component: () => import("../views/QualitativeDefinition.vue"),
    },
    {
      path: "/model-management",
      name: "model-management",
      component: () => import("../views/ModelManagement.vue"),
    },
    {
      path: "/eval-execution",
      name: "eval-execution",
      component: () => import("../views/EvaluationExecution.vue"),
    },
    {
      path: "/eval-result-summary",
      name: "eval-result-summary",
      component: () => import("../views/EvaluationResultsSummary.vue"),
    },
    {
      path: "/eval-result-detail",
      name: "eval-result-detail",
      component: () => import("../views/EvaluationResultDetail.vue"),
    },
    {
      path: "/dataset-register",
      name: "dataset-register",
      component: () => import("../views/DatasetRegister.vue"),
    },
    {
      path: "/report",
      name: "report",
      component: () => import("../views/Report.vue"),
    },
  ],
});

export default router;
