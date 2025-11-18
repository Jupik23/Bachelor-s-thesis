<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <button class="close-button" @click="$emit('close')">&times;</button>
      
      <div v-if="meal">
        <h2>Edit Meal: {{ meal.description ? meal.description.split(".")[0] : 'Current Meal' }}</h2>
        <form @submit.prevent="saveChanges">
          
          <div class="form-group">
            <label for="meal-time">Time:</label>
            <input 
              id="meal-time" 
              type="time" 
              v-model="formData.time" 
              class="form-input"
              required 
            />
          </div>

          <div class="form-group">
            <label for="meal-type">Meal Type:</label>
            <select 
              id="meal-type" 
              v-model="formData.meal_type" 
              class="form-input"
            >
              <option value="breakfast">Breakfast</option>
              <option value="second_breakfast">Second Breakfast</option>
              <option value="lunch">Lunch</option>
              <option value="snack">Snack</option>
              <option value="dinner">Dinner</option>
              <option value="supper">Supper</option>
            </select>
          </div>
          
          <div class="form-actions">
            <button type="button" class="btn btn-secondary" @click="$emit('close')">Cancel</button>
            <button type="submit" class="btn btn-primary">Save Changes</button>
          </div>

        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watchEffect } from 'vue';

const props = defineProps({
  meal: {
    type: Object,
    required: true
  }
});

const emit = defineEmits(['close', 'save']);

const formData = ref({
  time: '',
  meal_type: 'breakfast',
});

watchEffect(() => {
  if (props.meal) {
    formData.value.time = props.meal.time;
    formData.value.meal_type = props.meal.meal_type; 
  }
});

const saveChanges = () => {
  emit('save', { 
    id: props.meal.id, 
    data: formData.value 
  });
};
</script>

<style scoped>
.modal-overlay {
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
.modal-content {
  background-color: var(--white-color);
  padding: 2rem;
  border-radius: var(--border-radius-md);
  box-shadow: var(--shadow-md);
  width: 90%;
  max-width: 450px;
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
.close-button:hover {
  color: var(--text-color-dark);
}
h2 {
  margin-top: 0;
  color: var(--text-color-dark);
  border-bottom: 2px solid var(--secondary-color);
  padding-bottom: 0.5rem;
  word-break: break-all;
}
.form-group {
  margin-bottom: 1.5rem;
}
.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: var(--text-color-light);
}
.form-input {
  width: 100%;
  padding: 12px 15px;
  font-size: 1rem;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-md);
  box-sizing: border-box; 
  background-color: var(--white-color);
}
.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 2rem;
}
.form-actions .btn {
  width: auto;
}
</style>