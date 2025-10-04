<template>
  <form class="form" @submit.prevent="handleSubmit">
    <input v-model="weight" placeholder="weight" type="number" min="1" step="0.1" />
    <input v-model="height" placeholder="height"  type="number" min="1" step="0.1"/>
    <input v-model="numberOfMeals" placeholder="number of meals" type="number" min="1"  max="6"/>
    
    <multiselect
      v-model="selectedPreferences"
      :options="preferences"
      :multiple="true"
      label="preference"
      track-by="preference"
      placeholder="Select preferences"
    />
    
    <multiselect
      v-model="selectedIntolerances"
      :options="intolerances"
      :multiple="true"
      label="intolerance"
      track-by="intolerance"
      placeholder="Select intolerances"
    />

    <input v-model="medicaments" placeholder="Medicaments taken" />
    <div class="button">
      <button class="btn-primary" type="submit" :disabled="isLoading">
      {{ isLoading ? 'Submitting...' : 'Submit' }}
    </button>
    </div>
    <div v-if="successMessage" class="success-message">{{ successMessage }}</div>
    <div v-if="failureMessage" class="error-message">{{ failureMessage }}</div>
  </form>
</template>

<script setup>
import { onMounted, ref } from 'vue';
import Multiselect from 'vue-multiselect'
import "vue-multiselect/dist/vue-multiselect.min.css";
import api from "../lib/api.js";

//health form data - that will be given by user
const weight = ref(null);
const height = ref(null);
const numberOfMeals = ref(null);
const selectedIntolerances = ref([]);
const selectedPreferences = ref([]);
const medicaments = ref('');

//preferences, intolerances from spoonacular docs
const preferences = ref([])
const intolerances = ref([]);
const hasExistingForm = ref(false)

const populateForm = (data) => {
  height.value = data.height;
  weight.value = data.weight;
  numberOfMeals.value = data.number_of_meals_per_day;
  if (data.diet_preferences) {
    const prefNames = typeof data.diet_preferences === 'string' 
      ? data.diet_preferences.split(',') 
      : data.diet_preferences;
    selectedPreferences.value = preferences.value.filter(p => 
      prefNames.includes(p.name)
    );
  }
  
  if (data.intolerances) {
    const intolNames = typeof data.intolerances === 'string'
      ? data.intolerances.split(',')
      : data.intolerances;
    selectedIntolerances.value = intolerances.value.filter(i => 
      intolNames.includes(i.name)
    );
  }
  
  medicaments.value = data.medicament_usage || '';
  hasExistingForm.value = true;
}

const initializeDataFromDB = async ()=> {
  try{ 
    const [preferences_response, intolerances_response] = await Promise.all([
      api.get("api/v1/preferences"),
      api.get("api/v1/intolerances"),
    ]);
    preferences.value = preferences_response.data;
    intolerances.value = intolerances_response.data;
    try{
      const userFormResponse = await api.get("api/v1/health-form/me");
      if (userFormResponse.data) {
        populateForm(userFormResponse.data);
      }  
    }catch(error){
      if (error.response && error.response.status ===404){
        hasExistingForm.value = false;
        failureMessage.value = "Coulnd not load data"
      }
    }
  }catch (error){
    console.error("Failed to fetch initial data:", error);
  }finally {
        isLoading.value = false;
    }
}

onMounted(() => {
  initializeDataFromDB();
})

//UI variables
const isLoading = ref(false);
const successMessage = ref("");
const failureMessage = ref("");

const restartForm = () => {
  weight.value = null;
  height.value = null;
  numberOfMeals.value = null;
  selectedIntolerances.value = [];;
  selectedPreferences.value = [];
  medicaments.value = '';
}

const validateForm = () =>{
  if (weight.value <= 0 || !weight.value){
    failureMessage.value = "Enter valid weight"
    return false
  }

  if (height.value <= 0 || !height.value){
    failureMessage.value = "Enter valid height"
    return false
  }

  if (numberOfMeals.value <= 0 || !numberOfMeals.value){
    failureMessage.value = "Enter valid number of meals (range 1-6)"
    return false
  }
  return true
}

const handleSubmit = async () => {
  if (!validateForm() || isLoading.value){
    return;
  }
  isLoading.value = true;
  failureMessage.value = ""
  successMessage.value = ""
  try{
    const dataFormValues = {
      height: height.value,
      weight: weight.value,
      number_of_meals_per_day: numberOfMeals.value,
      diet_preferences: selectedPreferences.value.map(pref=>pref.name).join(','),
      intolerances: selectedIntolerances.value.map(pref=>pref.name).join(','),
      medicament_usage: medicaments.value,
    };
    const response = await api.put("/api/v1/health-form", dataFormValues)
    populateForm(response.data);
    successMessage.value = hasExistingForm.value 
      ? "Form updated successfully" 
      : "Form created successfully";
  }
  catch (error){
    console.log(error)
    failureMessage.value = "Failed to submit form."
  }
  finally{
    isLoading.value = false;
  }
}
</script>

<style>
.form{
  max-width: 400px;
  margin: 2rem auto;
  padding: 2rem;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
}
.button{
  display: flex;
  justify-content: center;
}
.btn-primary{
  background-color: var(--background-color);
  color: var(--color);
  padding: 12px 24px;
  border: none;
  border-radius: var(--border-radius-md);
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}
.btn-primary:hover {
  background-color: var(--background-color);
  transform: translateY(-2px);
}
input {
  padding: 0.6rem 0.8rem;
  border: 1px solid #ccc;
  border-radius: 8px;
  font-size: 0.95rem;
  transition: border 0.2s;
}
.multiselect__tag {
  background: var(--bg);
  color: var(--primary-color);
  border-color: var(--border-color);
  border-radius: 50px;
  padding: 4px 8px;
  box-shadow: var(--shadow-md);
  width: 25%;
}
.error-message{
  color: red;
}
.success-message{
  color: var(--primary-color)
}
</style>
