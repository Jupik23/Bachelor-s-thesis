<template>
    <div>
        <h1>Today's plan: {{ today }}</h1>
        <div v-if="isLoading" class="loading-state">
            <p>Generating your plan! Pelase wait!</p>
            <div class="spinner"></div>
        </div>
        <div v-else-if="error" class="error-state">
            <p>Error generating plan: {{ error }}</p>
            <p>Please ensure your Health Metrics are up-to-date.</p>
            <RouterLink to="/health_form" class="btn-primary">Update Health Metrics</RouterLink>
        </div>

        <div v-else-if="planData" class="meals-schedule">
            <Card title="Meals Scheadule">
                <ul class="meal-list">
                    <li v-for="meal in sortedMeals"
                    :key="meal.id"
                    class="meal-item">
                    <span class="meal-time">{{ formatTime(meal.time) }}</span>
                    <div class="meal-details">
                        <strong :class="['meal-type', meal.meal_type]">{{ meal.meal_type.toUpperCase() }}</strong>
                        <p class="meal-desc">{{ meal.description.split('.')[0] }}</p>
                    </div>
                    </li>
                </ul>
                <p v-if="!planData.meals.length" class="no-data">No meals found for today.</p>
            </Card>
        </div>
    </div>
</template> 

<script setup>
import { onMounted, ref, computed } from 'vue';
import Card from '@/components/Card.vue';
import api from '@/lib/api';

const today = new Date().toDateString();
const isLoading = ref(false)
const error = ref(false)
const planData =  ref(null)

const formatTime = (inputTime) => {
    if (!inputTime) return ''
    try{
        const parts = inputTime.split(":");
        return `${parts[0]}:${parts[1]}`;
    }catch (e) {
        return timeString.substring(0, 5);
    }
};

const sortedMeals = computed(() => {
    if (!planData.value || !planData.value.meals) return []
    return [...planData.value.meals].sort((a,b)=> {
        return a.time.localeCompare(b.time)
    });
});

const generatePlan = async() => {
    isLoading.value = true
    try{
        const respose = await api.post("api/v1/meals/generate")
        planData.value = respose.data;
    }catch (e){
        console.log("Error: ", e)
        error.value = e.response?.data?.detail || "Could not generate meal plan"
    }finally{
        isLoading.value = false;
    }
}

const getPlan = async() => {
        isLoading.value = true
    try{
        const respose = await api.get("api/v1/meals/today")
        planData.value = respose.data;
    }catch (e){
        console.log("Error: ", e)
        error.value = e.response?.data?.detail || "Could not load meal plan"
    }finally{
        isLoading.value = false;
    }
}

onMounted(() => {
    getPlan()
})
</script>

<style scoped>
.plan-container {
    padding: 2rem;
}
.cards-layout {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
    margin-top: 2rem;
}
.meal-list {
    list-style: none;
    padding: 0;
    margin: 0;
}
.meal-item {
    display: flex;
    align-items: flex-start; 
    gap: 1rem;
    padding: 0.75rem 0;
    border-bottom: 1px solid var(--border-color);
}
.meal-item:last-child {
    border-bottom: none;
}
.meal-time {
    font-weight: 700;
    color: var(--primary-color);
    flex-shrink: 0; 
}
.meal-details {
    display: flex;
    flex-direction: column;
    text-align: left;
}
.meal-type {
    font-size: 0.85rem;
    font-weight: 600;
    padding: 2px 6px;
    border-radius: var(--border-radius-sm);
    color: var(--white-color);
    display: inline-block;
    margin-bottom: 0.25rem;
}
.meal-desc {
    margin: 0;
    font-size: 0.95rem;
    color: var(--text-color-dark);
}
.no-data, .error-state p {
    color: var(--text-color-subtle);
    font-style: italic;
    margin-top: 0.5rem;
}

.meal-type.breakfast, .meal-type.second_breakfast { background-color: #4CAF50; } 
.meal-type.lunch { background-color: #2196F3; } 
.meal-type.snack { background-color: #FF9800; } 
.meal-type.dinner, .meal-type.supper { background-color: #F44336; } 
</style>