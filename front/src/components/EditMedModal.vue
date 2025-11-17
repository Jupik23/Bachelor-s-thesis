<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <button class="close-button" @click="$emit('close')">&times;</button>
      <div v-if="medication">
        <h2>Edit: {{ medication.name }}</h2>
        <form @submit.prevent="saveChanges">
          
          <div class="form-group">
            <label for="med-time">Time:</label>
            <input 
              id="med-time" 
              type="time" 
              v-model="formData.time" 
              class="form-input"
              required 
            />
          </div>
          <div class="form-group">
            <label for="med-relation">Relation to Meal:</label>
            <select 
              id="med-relation" 
              v-model="formData.with_meal_relation" 
              class="form-input"
            >
              <option value="empty_stomach">Empty Stomach</option>
              <option value="before">Before Meal</option>
              <option value="during">During Meal</option>
              <option value="after">After Meal</option>
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
  medication: {
    type: Object,
    required: true
  }
});
const emit = defineEmits(['close', 'save']);
const formData = ref({
  time: '',
  with_meal_relation: 'empty_stomach', 
  description: '',
});
watchEffect(() => {
  if (props.medication) {
    formData.value.time = props.medication.time;
    formData.value.with_meal_relation = props.medication.with_meal_relation; 
    formData.value.description = props.medication.description;
  }
});
const saveChanges = () => {
  emit('save', { 
    id: props.medication.id, 
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