<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <button class="close-button" @click="$emit('close')">&times;</button>
      
      <h2>Change Meal</h2>
      <p class="subtitle">Replacing: <strong>{{ meal.description.split('(')[0] }}</strong></p>

      <div class="search-box">
        <input 
          v-model="searchQuery" 
          @keyup.enter="performSearch"
          type="text" 
          placeholder="Search for new recipe (e.g. 'pasta')..." 
          class="form-input"
        />
        <button @click="performSearch" class="btn btn-primary" :disabled="isSearching">
          {{ isSearching ? 'Searching...' : 'Search' }}
        </button>
      </div>

      <div v-if="searchResults.length > 0" class="results-list">
        <div 
          v-for="recipe in searchResults" 
          :key="recipe.id" 
          class="recipe-item"
          @click="selectRecipe(recipe)"
          :class="{ 'selected': selectedRecipe?.id === recipe.id }"
        >
          <img :src="recipe.image" alt="Recipe" class="recipe-img" v-if="recipe.image"/>
          <div class="recipe-info">
            <h4>{{ recipe.title }}</h4>
          </div>
        </div>
      </div>
      <div v-else-if="hasSearched" class="no-results">
        No recipes found matching your criteria.
      </div>

      <div class="form-actions">
        <button class="btn btn-secondary" @click="$emit('close')">Cancel</button>
        <button 
          class="btn btn-primary" 
          @click="confirmChange" 
          :disabled="!selectedRecipe || isSaving"
        >
          {{ isSaving ? 'Saving...' : 'Replace Meal' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { searchRecipes } from '@/lib/api';

const props = defineProps({
  meal: { type: Object, required: true }
});
const emit = defineEmits(['close', 'replace']);

const searchQuery = ref('');
const searchResults = ref([]);
const isSearching = ref(false);
const hasSearched = ref(false);
const selectedRecipe = ref(null);
const isSaving = ref(false);

const performSearch = async () => {
  if (!searchQuery.value) return;
  isSearching.value = true;
  hasSearched.value = false;
  searchResults.value = [];
  selectedRecipe.value = null;

  try {
    const response = await searchRecipes(searchQuery.value);
    searchResults.value = response.data.results;
  } catch (e) {
    console.error(e);
  } finally {
    isSearching.value = false;
    hasSearched.value = true;
  }
};

const selectRecipe = (recipe) => {
  selectedRecipe.value = recipe;
};

const confirmChange = () => {
  if (!selectedRecipe.value) return;
  emit('replace', { 
    mealId: props.meal.id, 
    newRecipeId: selectedRecipe.value.id 
  });
  isSaving.value = true; 
};
</script>

<style scoped>
.modal-overlay { 
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background-color: rgba(0,0,0,0.6); display: flex; justify-content: center; align-items: center; z-index: 1000;
}
.modal-content {
  background-color: white; padding: 2rem; border-radius: 8px; width: 90%; max-width: 600px; max-height: 85vh; overflow-y: auto; position: relative;
}
.close-button { position: absolute; top: 1rem; right: 1rem; border: none; background: none; font-size: 1.5rem; cursor: pointer; }
.search-box { display: flex; gap: 10px; margin-bottom: 20px; }
.form-input { flex-grow: 1; padding: 10px; border: 1px solid #ccc; border-radius: 4px; }
.results-list { max-height: 300px; overflow-y: auto; margin-bottom: 20px; border: 1px solid #eee; }
.recipe-item { display: flex; gap: 10px; padding: 10px; border-bottom: 1px solid #eee; cursor: pointer; transition: background 0.2s; }
.recipe-item:hover { background-color: #f9f9f9; }
.recipe-item.selected { background-color: #e0f7fa; border-left: 4px solid #27ae60; }
.recipe-img { width: 60px; height: 60px; object-fit: cover; border-radius: 4px; }
.recipe-info h4 { margin: 0; font-size: 1rem; }
.subtitle { color: #666; margin-bottom: 20px; }
.form-actions { display: flex; justify-content: flex-end; gap: 10px; }
</style>