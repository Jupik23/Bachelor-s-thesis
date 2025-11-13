<template>
    <div>
        <h1>Today's plan: {{ today }}</h1>
        <div class="page-actions">
            <RouterLink to="/shopping-list" class="btn btn-secondary">
                🛒 Get Shopping List
            </RouterLink>
        </div>
        <PlanDisplay
            :planData="planData"
            :isLoading="isLoading"
            :error="error"
            :is-read-only="false" 
            @generate-plan="generatePlan"
            @update-meal="updateMealStatus"
            @update-medication="updateMedicationStatus"
        />
    </div>
</template> 

<script setup>
import { onMounted, ref } from 'vue';
import PlanDisplay from '@/components/PlanDisplay/Plan.vue'; 
import api from '@/lib/api';

const today = new Date().toDateString();
const isLoading = ref(false);
const error = ref(null);
const planData = ref(null);

const generatePlan = async () => {
    isLoading.value = true;
    try {
        const response = await api.post("api/v1/meals/generate"); 
        planData.value = response.data;
    } catch (e) {
        console.log("Error: ", e);
        error.value = e.response?.data?.detail || "Could not generate meal plan";
    } finally {
        isLoading.value = false;
    }
}

const loadInitialData = async () => {
    isLoading.value = true;
    error.value = null;
    planData.value = null;
    try {
        const planResponse = await api.get("api/v1/meals/today");
        planData.value = planResponse.data;
    } catch (e) {
        console.error("Error loading initial data: ", e);
        error.value = e.response?.data?.detail || "Could not load initial data.";
    } finally {
        isLoading.value = false;
    }
};

async function updateMealStatus(meal) {
    error.value = null;
    const payload = {
        eaten: meal.eaten,
        comment: meal.comment || null
    };

    try {
        const response = await api.patch(`/api/v1/meals/${meal.id}`, payload);
        const mealIndex = planData.value.meals.findIndex(m => m.id === meal.id);
        if (mealIndex !== -1) {
            planData.value.meals[mealIndex] = response.data;
        }
    } catch (e) {
        console.error("Failed to update meal status:", e);
        error.value = "Failed to update meal. Please try again.";
    }
}

async function updateMedicationStatus(medication) {
    error.value = null;
    const payload = {
        taken: medication.taken
    };
    try {
        await api.patch(`/api/v1/medications/${medication.id}/medication`, payload);
    } catch (e) {
        console.error("Failed to update medication status:", e);
        error.value = "Failed to update medication. Please try again.";
    }
}

onMounted(() => {
    loadInitialData();
});
</script>

<style scoped>
.page-actions {
    margin-bottom: 2rem;
    display: flex;
    justify-content: flex-start;
}

.page-actions .btn {
    width: auto; 
    padding: 10px 20px;
    font-size: 0.95rem;
}
</style>