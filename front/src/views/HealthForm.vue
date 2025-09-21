<template>
<BaseLayout>
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
     <button class="submit" type="submit" :disabled="isLoading">
      {{ isLoading ? 'Submitting...' : 'Submit' }}
    </button>
    <div v-if="successMessage" class="success-message">{{ successMessage }}</div>
    <div v-if="failureMessage" class="error-message">{{ failureMessage }}</div>
  </form>
  </BaseLayout>
</template>
<script setup>
import BaseLayout from '../layouts/Base.vue'
</script>

<script>
import { ref } from 'vue';
import Multiselect from 'vue-multiselect'
import "vue-multiselect/dist/vue-multiselect.min.css";
import api from "../lib/api.js"
export default {
  name: 'HealthForm',
  components:{
    BaseLayout,
    Multiselect,
  },
  data(){
    return {
      formData:{
        weight: null,
        height: null,
        numberOfMeals: null,
        selectedIntolerances: [],
        selectedPreferences: [],
        medicaments: '' //to do :)
      },
      preferences: [
        { name: 'Vegetarian' },
        { name: 'Vegan' },
        { name: 'Keto' },
        { name: 'Low Carb' },
        { name: 'Mediterranean' },
        { name: 'Paleo' }
      ],
      intolerances:[
        { name: 'Lactose' },
        { name: 'Gluten' },
        { name: 'Nuts' },
        { name: 'Shellfish' },
        { name: 'Eggs' },
        { name: 'Soy' }
      ],
      isLoading: false,
      successMessage: "",
      failureMessage: ""
    }
  },
  methods:{
    async handleSubmit(){
      if (!this.validateForm()){
        return
      }
      if (this.isLoading){
        console.log("loading")
        return
      }
      this.failureMessage = "";
      this.successMessage = "";
      this.isLoading = true
      try{
        const healthDataFromForm={
          height: this.height,
          weight: this.weight,
          number_of_meals_per_day: this.numberOfMeals,
          diet_preferences: this.selectedPreferences.map(pref=>pref.name),
          intolerances: this.selectedIntolerances.map(pref=>pref.name),
          medicament_usage: this.medicaments,
        }
        const response = await api.post("/api/v1/health-form", healthDataFromForm)
        this.successMessage = "Form submitted!"
        this.resetForm()
      }catch (error) {
        console.error("Submission error:", error);
        this.failureMessage = "Failed to submit form."
      }finally{
        this.isLoading = false
      }
    },
    validateForm(){
      if (!this.weight || this.weight <= 0){
        this.failureMessage = "Enter valid weight"
        return false;s
      }
      if (!this.height || this.height <= 0) {
        this.failureMessage = "Please enter a valid height.";
        return false;
      }
      if (!this.numberOfMeals || this.numberOfMeals < 1 || this.numberOfMeals > 6) {
        this.failureMessage = "Please enter a valid number of meals (1-6).";
        return false;
      }
      return true;
    },
    resetForm(){
      this.weight = null;
      this.height = null;
      this.numberOfMeals = null;
      this.selectedIntolerances = [];
      this.selectedPreferences = [];
      this.medicaments = '';
    }
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
