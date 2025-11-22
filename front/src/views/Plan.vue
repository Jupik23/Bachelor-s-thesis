<template>
    <div>
      <div v-if="isDependentView">
             <h1>Plan for Dependent (ID: {{ dependentId }})</h1>
             <p style="color: #666; font-style: italic; margin-bottom: 1rem;">
                You are managing this plan as a carer.
             </p>
        </div>
        <div class="date-navigation">
            <button class="btn-nav" @click="changeDate(-1)">← Prev</button>
            <div class="current-date">
                <h2>{{ formattedDisplayDate }}</h2>
                <span v-if="isToday" class="today-badge">Today</span>
            </div>
            <button class="btn-nav" @click="changeDate(1)">Next →</button>
        </div>
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
            @edit-medication="openEditModal"
            @show-recipe="showRecipeDetails"
            @edit-meal="openEditMealModal"
            @change-meal="openChangeMealModal"
        />
        <div v-if="isRecipeModalVisible" class="recipe-modal-overlay" @click.self="closeRecipeModal">
            <div class="recipe-modal-content">
                <button class="close-button" @click="closeRecipeModal">&times;</button>
                <div v-if="isRecipeLoading" class="modal-loading">
                    <div class="spinner"></div> <p>Loading recipe...</p>
                </div>
                <div v-else-if="recipeError" class="modal-error">
                    <h3>Error</h3> <p>{{ recipeError }}</p>
                </div>
                <div v-else-if="selectedRecipeDetails" class="recipe-details">
                    <h2>{{ selectedRecipeDetails.title }}</h2>
                    <h3>Summary</h3>
                    <div class="recipe-summary" v-html="selectedRecipeDetails.summary"></div>
                    <h3 v-if="selectedRecipeDetails.instructions">Instructions</h3>
                    <div class="recipe-instructions" v-html="selectedRecipeDetails.instructions"></div>
                </div>
            </div>
        </div>

        <EditMedModal
            v-if="isEditModalVisible"
            :medication="medicationToEdit"
            @close="closeEditModal"
            @save="handleSaveMedication"
        />
        <EditMealModal
            v-if="isEditMealModalVisible"
            :meal="itemToEdit"
            @close="closeEditMealModal"
            @save="handleSaveMeal"
        />
        <ChangeMealModal
          v-if="isChangeMealModalVisible"
          :meal="mealToChange"
          @close="closeChangeMealModal"
          @replace="handleReplaceMeal"
        />
    </div>
</template> 

<script setup>
import { onMounted, ref, computed, watch } from 'vue';
import PlanDisplay from '@/components/PlanDisplay/Plan.vue'
import { useRoute } from 'vue-router';
import EditMedModal from '@/components/EditMedModal.vue';
import EditMealModal from '@/components/EditMealModal.vue';
import ChangeMealModal from '@/components/ChangeMealModal.vue';
import api, { updateMedStatus, updateMedDetails, updateMealDetails, updateMealsStatus, getRecipeDetails,
  getDependentPlanByDate, replaceMeal, getPlanByDate } from '@/lib/api';

const currentDate = ref(new Date());
const isLoading = ref(false);
const error = ref(null);
const planData = ref(null)
const itemToEdit = ref(null)

const route = useRoute();
const dependentId = computed(() => route.params.id);
const isDependentView = computed(() => !!dependentId.value);

const apiDateFormat = computed(() => {
  return currentDate.value.toISOString().split('T')[0];
})

const formattedDisplayDate = computed(() => {
    return currentDate.value.toDateString();
});

const isToday = computed(() =>{
  const now = new Date();
  return currentDate.value.toDateString() === now.toDateString();
})

const changeDate = (days) => {
  const newDate = new Date(currentDate.value);
  newDate.setDate(newDate.getDate() + days);
  currentDate.value = newDate;
  loadInitialData()
}

const generatePlan = async () => {
    isLoading.value = true;
    try {
      let response;
      if (isDependentView){
        response = await api.post(`api/v1/dependents/${dependentId.value}/plan/generate`)
      }else{
        response = await api.post(`api/v1/meals/generate`)
      }
      if (isToday.value) {
             planData.value = response.data;
      } else {
            currentDate.value = new Date();
            planData.value = response.data;
      }
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
      let response; 
        if (isDependentView.value){
          response = await getDependentPlanByDate(dependentId.value, apiDateFormat.value)
        }else{
          response = await getPlanByDate(apiDateFormat.value)
        }
        planData.value = response.data;
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
        const response = await updateMealsStatus(meal.id, payload);
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
        await  updateMedStatus(medication.id, payload);
    } catch (e) {
        console.error("Failed to update medication status:", e);
        error.value = "Failed to update medication. Please try again.";
    }
}

const isRecipeModalVisible = ref(false);
const isRecipeLoading = ref(false);
const selectedRecipeDetails = ref(null);
const recipeError = ref(null);

const showRecipeDetails = async (meal) => {
  if (!meal.spoonacular_recipe_id) {
    recipeError.value = "No recipe ID available for this meal.";
    selectedRecipeDetails.value = { title: meal.description, instructions: "Details not available." };
    isRecipeModalVisible.value = true;
    return;
  }
  isRecipeModalVisible.value = true;
  isRecipeLoading.value = true;
  recipeError.value = null;
  selectedRecipeDetails.value = null;
  try {
    const response = await getRecipeDetails(meal.spoonacular_recipe_id);
    selectedRecipeDetails.value = response.data;
  } catch (e) {
    console.error("Failed to fetch recipe details:", e);
    recipeError.value = e.response?.data?.detail || "Could not load recipe details.";
  } finally {
    isRecipeLoading.value = false;
  }
};
const closeRecipeModal = () => {
  isRecipeModalVisible.value = false;
};

const isEditModalVisible = ref(false);
const medicationToEdit = ref(null);

function openEditModal(medication) {
  medicationToEdit.value = medication;
  isEditModalVisible.value = true;
}

function closeEditModal() {
  isEditModalVisible.value = false;
  medicationToEdit.value = null;
}

async function handleSaveMedication(payload) {
  const { id, data } = payload;
  try {
    const response = await updateMedDetails(id, data);  
    const medIndex = planData.value.medications.findIndex(m => m.id === id);
    if (medIndex !== -1) {
      planData.value.medications[medIndex] = response.data;
    }
    closeEditModal();
  } catch (e) {
    console.error("Failed to update medication details:", e);
    error.value = "Failed to update medication details.";
  }
}

const isEditMealModalVisible = ref(false);

function openEditMealModal(meal) {
  itemToEdit.value = meal;
  isEditMealModalVisible.value = true;
}
function closeEditMealModal() {
  isEditMealModalVisible.value = false;
  itemToEdit.value = null;
}
async function handleSaveMeal(payload) {
  const { id, data } = payload;
  try {
    const response = await updateMealDetails(id, data); 
    const mealIndex = planData.value.meals.findIndex(m => m.id === id);
    if (mealIndex !== -1) {
      planData.value.meals[mealIndex] = response.data;
    }
    closeEditMealModal();
  } catch (e) {
    console.error("Failed to update meal details:", e);
    error.value = "Failed to update meal details.";
  }
}
const isChangeMealModalVisible = ref(false);
const mealToChange = ref(null);

function openChangeMealModal(meal) {
  mealToChange.value = meal;
  isChangeMealModalVisible.value = true;
}

function closeChangeMealModal(){
  mealToChange.value = null;
  isChangeMealModalVisible.value = false;
}

async function handleReplaceMeal({mealId, newRecipeId}){
  try {
    const response = await replaceMeal(mealId, newRecipeId);
    const index = planData.value.meals.findIndex(m => m.id == mealId);
    if (index !== -1){
      planData.value.meals[index] = response.data;
    }
    isChangeMealModalVisible.value = false;
  } catch (e){
    console.error(e);
    alert("Failed to replace meal");
  }
}
watch(() => route.params.id, () => {
    loadPlanData();
});

onMounted(() => {
    loadInitialData();
});
</script>

<style scoped>
h1 {
    margin-bottom: 0.5rem;
    color: var(--text-color-dark);
}
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
.recipe-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}
.recipe-modal-content {
  background-color: var(--white-color);
  padding: 2rem;
  border-radius: var(--border-radius-md);
  box-shadow: var(--shadow-md);
  width: 90%;
  max-width: 700px;
  max-height: 85vh;
  overflow-y: auto;
  position: relative;
}
.close-button {
  position: absolute;
  top: 1rem;
  right: 1rem;
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-color-subtle);
  background: none;
  border: none;
  cursor: pointer;
  line-height: 1;
  padding: 0;
}
.date-navigation {
    display: flex;
    align-items: center;
    justify-content: center; 
    gap: 1.5rem;
    margin-bottom: 1.5rem;
    background-color: var(--background-color-light); 
    padding: 1rem;
    border-radius: 8px;
}

.current-date {
    text-align: center;
}

.current-date h2 {
    margin: 0;
    font-size: 1.5rem;
    color: var(--primary-color);
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
.modal-loading, .modal-error { text-align: center; padding: 3rem 1rem; }
.modal-error h3 { color: var(--danger-color); }
.recipe-details h2 { margin-top: 0; color: var(--primary-color); }
.recipe-details h3 { border-bottom: 2px solid var(--secondary-color); padding-bottom: 0.5rem; margin-top: 1.5rem; }
.recipe-summary, .recipe-instructions { font-size: 0.95rem; line-height: 1.6; color: var(--text-color-light); }
.recipe-instructions :deep(ol), .recipe-instructions :deep(ul) { padding-left: 20px; }
.recipe-instructions :deep(li) { margin-bottom: 0.75rem; }
.recipe-summary :deep(a) { color: var(--primary-color); font-weight: 600; }
</style>