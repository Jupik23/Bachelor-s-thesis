<template>
    <div>
        <h1>Plan for Dependent (ID: {{ dependentId }})</h1>
        <p>This is a read-only view of your dependent's plan. They can update status from their own account.</p>

        <PlanDisplay
            :planData="planData"
            :isLoading="isLoading"
            :error="error"
            :is-read-only="true" 
            @generate-plan="generatePlanForDependent"
            @update-meal="handleUpdateMeal"
            @update-medication="handleUpdateMedication"
        />
    </div>
</template>

<script setup>
import { onMounted, ref } from 'vue';
import { useRoute } from 'vue-router'; 
import PlanDisplay from '@/components/PlanDisplay/Plan.vue';
import api from '@/lib/api';


const route = useRoute();
const dependentId = ref(route.params.id); 

const isLoading = ref(false);
const error = ref(null);
const planData = ref(null);

const loadInitialData = async () => {
    isLoading.value = true;
    error.value = null;
    planData.value = null; 
    try {
        const url = `/api/v1/dependents/${dependentId.value}/plan/today`;
        const planResponse = await api.get(url);
        planData.value = planResponse.data;
    } catch (e) {
        console.error("Error loading dependent plan: ", e);
        error.value = e.response?.data?.detail || "Could not load dependent's plan.";
    } finally {
        isLoading.value = false;
    }
};
const generatePlanForDependent = async () => {
    isLoading.value = true;
    try {
        const url = `/api/v1/dependents/${dependentId.value}/plan/generate`;
        const response = await api.post(url);
        planData.value = response.data;
    } catch (e) {
        console.log("Error: ", e);
        error.value = e.response?.data?.detail || "Could not generate dependent's plan.";
    } finally {
        isLoading.value = false;
    }
}

async function handleUpdateMeal(meal) {
    console.log("Read-only view. Status update not allowed here.", meal);
}

async function handleUpdateMedication(medication) {
    console.log("Read-only view. Status update not allowed here.", medication);
}


onMounted(() => {
    loadInitialData();
});
</script>

<style scoped>
h1 {
    margin-bottom: 5px;
}
p {
    font-style: italic;
    color: #555;
    margin-bottom: 20px;
}
</style>