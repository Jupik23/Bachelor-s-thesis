<template>
    <div>
        <div v-if="isLoading" class="loading-state">
            <p>Loading plan! Please wait!</p> <div class="spinner"></div>
        </div>

        <div v-else-if="error" class="error-state">
            <p>Error loading plan: {{ error }}</p>
            <p v>Please ensure Health Metrics are up-to-date (if this is your plan).</p>
        </div>

        <div v-else-if="planData" class="meals-schedule"
        :class="{ 'has-interactions': interactionAlerts.length > 0 }"
        >
            <Card title="Meals Schedule">
                <ul class="meal-list">
                    <li v-for="meal in sortedMeals" :key="meal.id" class="meal-item">
                        <span class="meal-time">{{ formatTime(meal.time) }}</span>
                        <div class="meal-details">
                            <strong :class="['meal-type', meal.meal_type]">{{ meal.meal_type.toUpperCase() }}</strong>
                            <p class="meal-desc recipe-link" @click="$emit('show-recipe', meal)">
                                {{ meal.description.split('.')[0] }}
                                <span class="recipe-prompt">(Click for recipe)</span>
                            </p>
                            <p v-if="meal.comment" class="meal-comment-display">
                                <strong>Comment:</strong> {{ meal.comment }}
                            </p>
                        </div>
                        <div class="meal-actions">
                            <input 
                                type="text" 
                                class="meal-comment"
                                :value="meal.comment"
                                placeholder="Add comment..."
                                @blur="$emit('update-meal', { ...meal, comment: $event.target.value })"
                                :disabled="isReadOnly"
                            />
                            <div class="checkbox-wrapper">
                                <input 
                                    type="checkbox" 
                                    :id="'meal-' + meal.id"
                                    :checked="meal.eaten"
                                    @change="$emit('update-meal', { ...meal, eaten: $event.target.checked })"
                                    :disabled="isReadOnly"
                                />
                                <label :for="'meal-' + meal.id">
                                    {{ meal.eaten ? 'Eaten' : 'Mark as eaten' }}
                                </label>
                            </div>
                            <div v-if="!isReadOnly" class="edit-action-wrapper">
                                <button 
                                    class="btn-edit" 
                                    @click="$emit('edit-meal', meal)"
                                >
                                    Edit Meal
                                </button>
                            </div>
                        </div>
                    </li>
                </ul>

                <div v-if="!planData.meals || !planData.meals.length" class="no-data-container">
                    <p class="no-data">No meals found for today.</p>
                    <button @click="$emit('generate-plan')" :disabled="isLoading" class="btn btn-primary">
                        Generate Today's Plan
                    </button>
                </div>
            </Card>

            <Card title="Medications">
                 <ul v-if="planData.medications && planData.medications.length" class="item-list simple-list">
                    <li v-for="med in planData.medications" :key="med.id" class="list-item simple-item med-item" :class="{ 'is-taken': med.taken }">
                        <div class="med-details">
                                <strong>{{ med.name }}</strong> ({{ formatTime(med.time) }})
                                <p>{{ med.description }}</p>
                        </div>
                        <div class="med-actions-group">
                            <div class="checkbox-wrapper">
                                <input 
                                    type="checkbox" 
                                    :id="'med-' + med.id"
                                    :checked="med.taken"
                                    @change="$emit('update-medication', { ...med, taken: $event.target.checked })"
                                    :disabled="isReadOnly"
                                />
                                <label :for="'med-' + med.id">{{ med.taken ? 'Taken' : 'Mark as taken' }}</label>
                            </div>
                            <div class="med-actions" v-if="!isReadOnly">
                                <button 
                                    class="btn-edit" 
                                    @click="$emit('edit-medication', med)"
                                >
                                    Edit Med
                                </button>
                            </div>
                        </div>
                    </li>
                </ul>
                <p v-else class="no-data">No medications listed in this plan.</p>
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
                <p v-else class="no-data alert-success">No significant drug interactions detected.</p>
            </Card>
        </div>
        
        </div>
</template> 

<script setup>
import { computed } from 'vue';
import Card from '@/components/Card.vue';

const props = defineProps({
    planData: {
        type: Object,
        default: null
    },
    isLoading: {
        type: Boolean,
        default: false
    },
    error: {
        type: [String, Boolean, Object],
        default: false
    },
    isReadOnly: {
        type: Boolean,
        default: false 
    }
});

const emit = defineEmits([
    'update-meal', 
    'update-medication', 
    'generate-plan', 
    'edit-medication', 
    'show-recipe',     
    'edit-meal'        
]);

const formatTime = (inputTime) => {
    if (!inputTime) return ''
    try{
        const parts = inputTime.split(":");
        return `${parts[0]}:${parts[1]}`;
    } catch (e) {
        return inputTime.substring(0, 5); 
    }
};

const sortedMeals = computed(() => {
    if (!props.planData || !props.planData.meals) return []
    return [...props.planData.meals].sort((a, b) => a.time.localeCompare(b.time));
});

const interactionAlerts = computed(() => {
    return props.planData?.interactions || []; 
});
</script>

<style scoped>
.med-actions-group {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.edit-action-wrapper {
    margin-top: 0.5rem; 
}

.btn-edit {
  padding: 0.3rem 0.75rem;
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--primary-color);
  background-color: var(--secondary-color);
  border: 1px solid var(--secondary-color);
  border-radius: var(--border-radius-md);
  cursor: pointer;
  transition: all 0.2s ease;
}
.btn-edit:hover {
  background-color: var(--secondary-color-hover);
  color: var(--primary-color-hover);
}
.loading-state,
.error-state {
  padding: 3rem 1.5rem;
  text-align: center;
  background-color: var(--background-color-light);
  border-radius: var(--border-radius-md);
  margin-top: 2rem;
}
.loading-state p {
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--text-color-light);
}
.error-state p {
  color: var(--danger-color);
  font-weight: 600;
  margin-bottom: 1.5rem;
  font-size: 1.1rem;
}
.error-state .btn-primary {
  width: auto;
}
.spinner {
  border: 4px solid var(--secondary-color);
  border-top: 4px solid var(--primary-color);
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 1.5rem auto 0;
}
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
.meals-schedule {
  display: grid;
  grid-template-columns: 1fr; 
  gap: 2rem;
  margin-top: 2rem;
}
@media (min-width: 992px) {
    .meals-schedule {
        grid-template-columns: 2fr 2fr 1fr;
        align-items: flex-start; 
    }
    .meals-schedule.has-interactions {
    grid-template-columns: 1fr 1fr 2fr;
  }
}

.meal-list,
.item-list {
  list-style-type: none;
  padding: 0;
  margin: 0;
}
.meal-list > li + li,
.item-list > li + li {
  margin-top: 1.25rem;
  border-top: 1px solid var(--secondary-color);
  padding-top: 1.25rem;
}
.list-item,
.meal-item {
  display: flex;
  margin: auto;
  align-items: flex-start;
  gap: 1rem;
}
.meal-time {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--primary-color);
  justify-content: center;
  background-color: var(--secondary-color);
  padding: 0.5rem 0.75rem;
  border-radius: var(--border-radius-md);
  min-width: 65px;
  text-align: center;
  flex-shrink: 0;
}
.meal-details {
  flex-grow: 0;
  flex-basis: 300px;
}
.meal-details p {
  margin: 0.25rem 0 0;
  color: var(--text-color-light);
  font-size: 0.95rem;
  line-height: 1.5;
}
.meal-type {
  font-size: 0.8rem;
  font-weight: 700;
  padding: 0.25rem 0.6rem;
  border-radius: 4px;
  color: var(--white-color);
  background-color: var(--text-color-subtle);
  display: inline-block;
  text-transform: uppercase;
  margin-bottom: 0.25rem;
}
.meal-type.breakfast { background-color: #f39c12; }
.meal-type.lunch { background-color: #3498db; }
.meal-type.dinner { background-color: #8e44ad; }
.meal-type.snack, .meal-type.second_breakfast, .meal-type.supper { background-color: #7f8c8d; }
.meal-actions {
  flex-shrink: 0;
  flex-basis: 220px;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
.meal-comment {
  font-size: 0.9rem;
  padding: 8px 10px;
}

.med-item {
  display: flex;
  justify-content: center; 
  align-items: center;
  gap: 1rem;
}
.med-details {
  flex-grow: 0;
  flex-basis: 300px;
}
.med-details strong {
  font-size: 1.1rem;
  color: var(--text-color-dark);
}
.med-details p {
  margin: 0.25rem 0 0;
  font-size: 0.9rem;
  color: var(--text-color-subtle);
}
.med-item.is-taken .med-details strong {
  text-decoration: line-through;
  color: var(--text-color-subtle);
}
.med-item.is-taken .med-details p {
  text-decoration: line-through;
}
.alert-item {
  border-left-width: 5px;
  border-left-style: solid;
  padding: 1rem 1.25rem;
  border-radius: var(--border-radius-md);
  background-color: var(--background-color-light);
}
.alert-severity {
  font-weight: 700;
  text-transform: uppercase;
  display: block;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
}
.item-desc {
  margin: 0;
  font-size: 0.95rem;
  line-height: 1.5;
}
.alert-item.high {
  border-color: var(--danger-color);
  background-color: #fdeeee;
}
.alert-item.high .alert-severity {
  color: var(--danger-color);
}
.alert-item.moderate {
  --warning-color: #f39c12; 
  border-color: var(--warning-color);
  background-color: #fef9e7; 
}
.alert-item.moderate .alert-severity {
  color: var(--warning-color);
}
.alert-item.low {
  --low-color: #3498db;
  border-color: var(--low-color);
  background-color: #ebf5fb; 
}
.alert-item.low .alert-severity {
  color: var(--low-color);
}
.no-data-container {
  text-align: center;
  padding: 2rem 1rem;
  background-color: var(--background-color-light);
  border-radius: var(--border-radius-md);
}

.no-data,
.alert-success {
  font-size: 1rem;
  color: var(--text-color-light);
  margin-top: 0;
  margin-bottom: 1.5rem;
}

.alert-success {
  color: var(--primary-color);
  font-weight: 600;
}
.no-data-container .btn-primary {
  width: auto; 
}
.checkbox-wrapper {
  display: flex;
  align-items: center;
  position: relative;
  cursor: pointer;
  user-select: none;
}
.checkbox-wrapper input[type="checkbox"] {
  opacity: 0;
  width: 0;
  height: 0;
  position: absolute;
}
.checkbox-wrapper label {
  position: relative;
  padding-left: 30px;
  cursor: pointer;
  font-size: 0.95rem;
  color: var(--text-color-light);
  font-weight: 500;
}
.checkbox-wrapper label::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 18px;
  height: 18px;
  border: 2px solid var(--border-color);
  border-radius: 4px;
  background: var(--white-color);
  transition: all 0.2s ease;
}
.checkbox-wrapper label::after {
  content: '✔';
  position: absolute;
  left: 4px;
  top: 50%;
  transform: translateY(-50%) scale(0);
  font-size: 14px;
  font-weight: 700;
  color: var(--white-color);
  transition: transform 0.2s ease;
}
.checkbox-wrapper input[type="checkbox"]:checked + label::before {
  background-color: var(--primary-color);
  border-color: var(--primary-color);
}
.checkbox-wrapper input[type="checkbox"]:checked + label::after {
  transform: translateY(-50%) scale(1);
}
.checkbox-wrapper input[type="checkbox"]:checked + label {
  color: var(--text-color-dark);
  font-weight: 600;
}
.checkbox-wrapper input[type="checkbox"]:disabled + label {
  cursor: not-allowed;
  color: var(--text-color-subtle);
}
.checkbox-wrapper input[type="checkbox"]:disabled + label::before {
  background-color: var(--secondary-color);
  border-color: var(--border-color);
}

.recipe-link {
  cursor: pointer;
  color: var(--primary-color) !important;
  text-decoration: none;
  font-weight: 500;
}
.recipe-link:hover {
  text-decoration: underline;
}
.recipe-prompt {
  font-size: 0.8rem;
  font-style: italic;
  margin-left: 5px;
  color: var(--text-color-subtle);
  font-weight: 400;
}
</style>