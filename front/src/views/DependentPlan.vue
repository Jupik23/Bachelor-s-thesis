<template>
    <div>
        <h1>Plan for Dependent (ID: {{ dependentId }})</h1>
        <p>This is a read-only view of your dependent's plan. They can update status from their own account.</p>

        <div class="date-navigation">
            <button class="btn-nav" @click="changeDate(-1)">← Prev</button>
            <div class="current-date">
                <h2>{{ formattedDisplayDate }}</h2>
                <span v-if="isToday" class="today-badge">Today</span>
            </div>
            <button class="btn-nav" @click="changeDate(1)">Next →</button>
        </div>

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
import { onMounted, ref, computed } from 'vue';
import { useRoute } from 'vue-router'; 
import PlanDisplay from '@/components/PlanDisplay/Plan.vue';
import api, {getDependentPlanByDate, getRecipeDetails} from '@/lib/api';


const route = useRoute();
const dependentId = ref(route.params.id); 

const currentDate = ref(new Date());  
const isLoading = ref(false);
const error = ref(null);
const planData = ref(null);

const apiDateFormat = computed(() => {
  return currentDate.value.toISOString().split('T')[0];
});

const formattedDisplayDate = computed(() => {
    return currentDate.value.toDateString();
});

const changeDate = (days) => {
  const newDate = new Date(currentDate.value);
  newDate.setDate(newDate.getDate() + days);
  currentDate.value = newDate;
  loadPlanData(); 
};

const loadInitialData = async () => {
    isLoading.value = true;
    error.value = null;
    planData.value = null; 
    try {
        const planResponse = await getDependentPlanByDate(dependentId.value, apiDateFormat.value);
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
.date-navigation {
    display: flex;
    align-items: center;
    justify-content: center; 
    gap: 2rem; 
    margin-bottom: 2rem;
    padding: 1rem;
    background-color: var(--white-color);
    border-radius: var(--border-radius-md);
    box-shadow: var(--shadow-sm);
    border: 1px solid var(--border-color); 
}

.current-date {
    display: flex;
    flex-direction: column;
    align-items: center;
    min-width: 200px; 
}

.current-date h2 {
    margin: 0;
    font-size: 1.4rem;
    color: var(--text-color-dark);
    font-weight: 700;
    letter-spacing: -0.5px;
}

.today-badge {
    margin-top: 0.3rem;
    background-color: #e8f5e9; 
    color: var(--primary-color);
    font-size: 0.75rem;
    font-weight: 700;
    padding: 2px 10px;
    border-radius: 12px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.btn-nav {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background-color: transparent;
    border: 1px solid var(--border-color); 
    color: var(--text-color-light);
    padding: 0.6rem 1.2rem;
    border-radius: var(--border-radius-md);
    cursor: pointer;
    font-weight: 600;
    font-size: 0.95rem;
    transition: all 0.2s ease-in-out;
    user-select: none; 
}

.btn-nav:hover {
    border-color: var(--primary-color);
    color: var(--primary-color);
    background-color: rgba(39, 174, 96, 0.05); 
    transform: translateY(-1px);
}

.btn-nav:active {
    transform: translateY(1px);
    background-color: rgba(39, 174, 96, 0.1);
}

@media (max-width: 480px) {
    .date-navigation {
        gap: 0.5rem;
        padding: 0.75rem;
    }
    
    .current-date {
        min-width: auto; 
    }
    
    .current-date h2 {
        font-size: 1.1rem;
    }
    
    .btn-nav {
        padding: 0.5rem 0.8rem;
        font-size: 0.85rem;
    }
}
</style>