<template>
  <form class="form" @submit.prevent="handleSubmit">
    <h1> Health Form</h1>
    <h2>1. Basic Information</h2>
    <label for="age-input">Age</label>
    <input v-model="age" type="number" placeholder="Age (e.g., 30)" min="16" max="100"/>  

    <label for="gender-select">Gender</label>
    <multiselect
      v-model="gender"
      :options="sexOptions"
      :multiple="false"
      label="label"
      track-by="value"
      placeholder="Gender"
    />
    
    <h2>2. Physical Parameters</h2>
    <label for="weight-input">Weight (kg)</label>
    <input v-model="weight" placeholder="Weight (e.g., 75)" type="number" min="1" step="1" />
    <label for="height-input">Height (cm)</label>
    <input v-model="height" placeholder="Height (e.g., 180)"  type="number" min="1" step="1"/>

    <h2>3. Activity and Calorie Goals</h2>
    <label for="activity-select">Daily Activity Level</label>
    <multiselect
      v-model="selectedActivityLevel"
      :options="activityLevels"
      :multiple="false"
      label="label"
      track-by="value"
      placeholder="You daily activity"
    />
    <label for="calorie-goal-select">Weight Goal</label>
    <multiselect
      v-model="selectedCalorieGoal"
      :options="calorieGoals"
      :multiple="false"
      label="label"
      track-by="value"
      placeholder="You weight goal"
    />
    <label for="meals-input">Number of Meals Per Day</label>
    <input v-model="numberOfMeals" placeholder="Number of meals per day" type="number" min="1"  max="6"/>
    
    <h2>4. Dietary and Medical Requirements</h2>
    <label for="preferences-select">Dietary Preferences</label>
    <multiselect
      v-model="selectedPreferences"
      :options="preferences"
      :multiple="true"
      label="preference"
      track-by="preference"
      placeholder="Select preferences"
    />
    
    <label for="inrolerances-select">Food Intolerances</label>
    <multiselect
      v-model="selectedIntolerances"
      :options="intolerances"
      :multiple="true"
      label="intolerance"
      track-by="intolerance"
      placeholder="Select intolerances"
    />
    <label for="medicaments-taken">Medicaments</label>
    <multiselect
      v-model="medicaments"
      :options="[]"
      :multiple="true"
      :taggable="true"
      @tag="addTag"
      placeholder="Type medication names (press Enter after each)"
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
const medicaments = ref([]);
const selectedActivityLevel = ref(null);
const selectedCalorieGoal = ref(null);
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

const addTag = async (newTag) => {
  const normalizedTag = newTag.trim().toLowerCase();
  if (!normalizedTag || medicaments.value.includes(normalizedTag)){
    failureMessage.value = "Drug name cannot be empty or duplicated!"
    return;
  }
  isLoading.value = true;
  failureMessage.value = "";
  try{
    const validationResponse = await api.post("api/v1/medications/validate", {drug_name: newTag});
    if (validationResponse.data.is_valid){
      medicaments.value.push(normalizedTag)
      successMessage.value = "Medication validated and added"
    }else{
      failureMessage.value = "Medication could not be validated and added"
    }
  }catch (error) {
        failureMessage.value = `Validation failed: ${error.response?.data?.detail || 'Server error'}`;
    } finally {
        isLoading.value = false;
    }
};

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
  medicaments.value = data.medicament_usage 
                     ? data.medicament_usage.split(',')
                         .map(med => med.trim())
                         .filter(med => med.length > 0)
                     : [];
  age.value = data.age;
  gender.value = sexOptions.value.find(o=>o.value===data.gender) || null;
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

//UI variables need to implement popup's
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
      medicament_usage: medicaments.value.join(', ') || '',
      age: age.value,
      gender: gender.value?.value || gender.value,
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
.form h2{
  font-size: 1.2rem;
  color: var(--primary-color);
  margin-top: 1rem;
  margin-bottom: 0.5rem;
  padding-bottom: 0.3rem;
  border-bottom: 2px solid #eee;
}
.form label{
  font-weight: 600; 
  font-size: 0.8rem;
  color: #333;
  margin-top: 0.5rem;
  margin-bottom: -0.5rem;
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
