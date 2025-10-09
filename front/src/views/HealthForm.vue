<template>
  <form class="form" @submit.prevent="handleSubmit">
    <input v-model="weight" placeholder="weight" type="number" min="1" step="1" />
    <input v-model="height" placeholder="height"  type="number" min="1" step="1"/>
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
    <br/>
    <input v-model="age" type="number" placeholder="Age" min="16" max="100"/>
    <multiselect
      v-model="selectedActivityGoal"
      :options="activityLevels"
      :multiple="false"
      label="label"
      track-by="value"
      placeholder="You daily activity"
    />
    <multiselect
      v-model="selectedCalorieGoal"
      :options="calorieGoals"
      :multiple="false"
      label="label"
      track-by="value"
      placeholder="You weight goal"
    />
    <multiselect
      v-model="gender"
      :options="sexOptions"
      :multiple="false"
      label="label"
      track-by="value"
      placeholder="Gender"
    />

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
const selectedLevel = ref('moderate');
const selectedGoal = ref('maintain');
const age = ref(null);
const gender = ref(null);

const activityLevels = ref([
  { label: "Sedentary (little or no exercise)", value: "sedentary" },
  { label: "Lightly active (light exercise/sports 1-3 days/week)", value: "light" },
  { label: "Moderately active (moderate exercise/sports 3-5 days/week)", value: "moderate" },
  { label: "Active (hard exercise/sports 6-7 days a week)", value: "active" },
  { label: "Very active (very hard exercise & physical job)", value: "very_active" }
]);
const calorieGoals = ref([
  { label: "Extreme weight loss (about 1kg per week)", value: "extreme_loss" },
  { label: "Weight loss (about 0.5kg per week)", value: "loss" },
  { label: "Mild weight loss (about 0.25kg per week)", value: "mild_loss" },
  { label: "Maintain weight", value: "maintain" },
  { label: "Mild weight gain (about 0.25kg per week)", value: "mild_gain" },
  { label: "Weight gain (about 0.5kg per week)", value: "gain" }
]);

const sexOptions = ref([ 
    { label: "Male", value: "male" },
    { label: "Female", value: "female" },
]);

//preferences, intolerances from spoonacular docs
const preferences = ref([])
const intolerances = ref([]);
const hasExistingForm = ref(false)

const populateForm = (data) => {
  height.value = data.height;
  weight.value = data.weight;
  numberOfMeals.value = data.number_of_meals_per_day;

  selectedIntolerances.value = intolerances.value.filter(i=> 
    data.intolerances?.includes(i.intolerance)
  )
  selectedPreferences.value = preferences.value.filter(p=> 
    data.diet_preferences?.includes(p.preference)
  )
  
  medicaments.value = data.medicament_usage || '';
  age.value = data.age;
  gender.value = data.gender;
  selectedActivityLevel.value = activityLevels.value.find(o => o.value === data.activity_level) || null;
  selectedCalorieGoal.value = calorieGoals.value.find(o => o.value === data.calorie_goal) || null;
  
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
      diet_preferences: selectedPreferences.value.map(pref=>pref.preference),
      intolerances: selectedIntolerances.value.map(pref=>pref.intolerance),
      medicament_usage: medicaments.value,
      age: age.value,
      gender: gender.value ? gender.value.value : null,
      activity_level: selectedActivityLevel.value?.value,
      calorie_goal: selectedCalorieGoal.value?.value,
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
