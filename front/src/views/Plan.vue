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
                    <div class="meal-actions">
                            <input 
                                type="text" 
                                class="meal-comment"
                                v-model="meal.comment"
                                placeholder="Add comment..."
                                @blur="updateMealStatus(meal)" 
                            />
                            <div class="checkbox-wrapper">
                                <input 
                                    type="checkbox" 
                                    :id="'meal-' + meal.id"
                                    v-model="meal.eaten"
                                    @change="updateMealStatus(meal)"
                                />
                                <label :for="'meal-' + meal.id">
                                    {{ meal.eaten ? 'Eaten' : 'Mark as eaten' }}
                                </label>
                            </div>
                        </div>
                    </li>
                </ul>
                <p v-if="!planData.meals.length" class="no-data">No meals found for today.</p>
            </Card>
            <Card title="Medications">
                <ul v-if="planData.medications && planData.medications.length" class="item-list simple-list">
                    <li v-for="med in planData.medications" :key="med.id" class="list-item simple-item med-item" :class="{ 'is-taken': med.taken }">
                        <div class="med-details">
                                <strong>{{ med.name }}</strong> ({{ formatTime(med.time) }})
                                <p>{{ med.description }}</p>
                            </div>
                            <input 
                                type="checkbox" 
                                :id="'med-' + med.id"
                                v-model="med.taken"
                                @change="updateMedicationStatus(med)"
                            />
                            <label :for="'med-' + med.id">{{ med.taken ? 'Taken' : 'Mark as taken' }}</label>
                        </li>
                </ul>
                <p v-else class="no-data">No medications listed in your Health Form.</p>
                <RouterLink to="/health-form" class="btn-secondary">Edit Medications in Health Form</RouterLink>
            </Card>

            <Card title="Interaction Alerts">
                <ul v-if="interactionAlerts.length" class="item-list alert-list">
                     <li v-for="(alert, index) in interactionAlerts" :key="index" :class="['list-item alert-item', alert.severity.toLowerCase()]">
                        <div class="item-details">
                            <strong class="item-type alert-severity">{{ alert.severity }}</strong>
                             <p class="item-desc">
                                 <strong>{{ alert.medication_1 }} & {{ alert.medication_2 }}:</strong>
                                 {{ alert.description }}
                             </p>
                        </div>
                     </li>
                 </ul>
                <p v-else class="no-data alert-success">No significant drug interactions detected based on your Health Form.</p>
            </Card>
        </div>
    </div>
</template> 

<script setup>
import { onMounted, ref, computed, renderSlot } from 'vue';
import Card from '@/components/Card.vue';
import api from '@/lib/api';

const today = new Date().toDateString();
const isLoading = ref(false)
const error = ref(false)
const planData =  ref(null)
const medicationNamesFromHealthForm = ref([]);

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
    return [...planData.value.meals].sort((a, b) => a.time.localeCompare(b.time));
});

const interactionAlerts = computed(() => {
    return planData.value?.interactions || []; 
})

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

const loadInitialData = async () => {
    isLoading.value = true;
    error.value = null;
    planData.value = null; 
    medicationNamesFromHealthForm.value = [];
    try {
        const planResponse = await api.get("api/v1/meals/today");
        console.log(test)
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
        meal.comment = response.data.comment;
        meal.eaten = response.data.eaten;
    } catch (e) {
        console.error("Failed to update meal status:", e);
        error.value = "Failed to update meal. Please try again.";
        meal.eaten = !meal.eaten;
    }
}
async function updateMedicationStatus(medication) {
    error.value = null;
    const payload = {
        taken: medication.taken
    };
    try {
        await api.patch(`/api/v1/plans/${medication.id}/medication`, payload);
    } catch (e) {
        console.error("Failed to update medication status:", e);
        error.value = "Failed to update medication. Please try again.";
        medication.taken = !medication.taken;
    }
}

onMounted(() => {
    //generatePlan()
    loadInitialData();
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