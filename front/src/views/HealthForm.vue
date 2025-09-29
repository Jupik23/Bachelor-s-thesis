<template>
  <form class="form" @submit.prevent="handleSubmit">
    <input v-model="weight" placeholder="weight" type="number" min="1" step="0.1" />
    <input v-model="height" placeholder="height"  type="number" min="1" step="0.1"/>
    <input v-model="numberOfMeals" placeholder="number of meals" type="number" min="1"  max="6"/>
    
    <multiselect
      v-model="selectedPreferences"
      :options="preferences"
      :multiple="true"
      label="name"
      track-by="name"
      placeholder="Select preferences"
    />
    
    <multiselect
      v-model="selectedIntolerances"
      :options="intolerances"
      :multiple="true"
      label="name"
      track-by="name"
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
import { ref } from 'vue';
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
const preferences = ref([
    { name: 'Vegetarian' }, { name: 'Vegan' }, { name: 'Keto' },
    { name: 'Low Carb' }, { name: 'Mediterranean' }, { name: 'Paleo' }
]);
const intolerances = ref([
    { name: 'Lactose' }, { name: 'Gluten' }, { name: 'Nuts' },
    { name: 'Shellfish' }, { name: 'Eggs' }, { name: 'Soy' }
]);

//UI variables
const isLoading = ref(false);
const successMessage = ref("");
const failureMessage = ref("");

const restartForm = () => {
  weight.value = null;
  height.value = null;
  numberOfMeals.value = null;
  selectedIntolerances.value = null;;
  selectedPreferences.value = null;
  medicaments.value = '';
}

const validateForm = () =>{
  if (weight.value <= 0 || !weight.value){
    failureMessage.value = "Enter valid weight"
    return false
  }

  if (height.value <= 0 || !height.value){
    failureMessage.value = "Enter valid heght"
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
      diet_preferences: selectedPreferences.value.map(pref=>pref.name),
      intolerances: selectedIntolerances.value.map(pref=>pref.name),
      medicament_usage: medicaments.value,
    };
    await api.post("/api/v1/health-form", dataFormValues)

    successMessage.value = "Form submitted"
    restartForm()
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
  background: radial-gradient(1200px 600px at 10% -10%, rgba(59,130,246,.08), transparent 60%),
             radial-gradient(900px 500px at 110% 110%, rgba(16,185,129,.07), transparent 60%),
             var(--bg);
  color: white;
  border-radius: 8px;
  padding: 4px 8px;
}
</style>
