<template>
    <div class="container">
        <h1>Shopping List</h1>
        <div class="header-actions">
            <RouterLink to="/todays-plan" class="btn-secondary">Back to plan</RouterLink>
        </div>
        
        <div class="controls">
            <div class="control-group">
                <label>Duration:</label>
                <select v-model="settings.days">
                    <option :value="1">Today only</option>
                    <option :value="3">Next 3 days</option>
                    <option :value="7">Next 7 days</option>
                </select>
            </div>
            <div class="control-group checkbox">
                <input type="checkbox" id="dep" v-model="settings.include_dependents">
                <label for="dep">Include Dependents</label>
            </div>
            <button @click="generateList" class="btn-primary" :disabled="isLoading">
                {{ isLoading ? 'Generating...' : 'Generate New List' }}
            </button>
        </div>

        <div v-if="isLoading" class="loading-state">
            <p>Processing your shopping list...</p>
            <div class="spinner"></div>
        </div>
        
        <div v-else-if="error" class="error-state">
            <p>Error: {{ error }}</p>
        </div>

        <div v-else-if="shoppingList && shoppingList.categories.length > 0" class="shopping-list-container">
            <div class="meta-info">
                <p><strong>Date Range:</strong> {{ shoppingList.from_date }} to {{ shoppingList.to_date }}</p>
                <p><strong>Total Items:</strong> {{ shoppingList.total_items }}</p>
            </div>

            <Card v-for="category in shoppingList.categories" :key="category.category" :title="category.category">
                <ul class="item-list">
                    <li v-for="(item, index) in category.items" :key="index" class="list-item">
                        <input type="checkbox" :id="`item-${category.category}-${index}`" class="item-checkbox" />
                        <label :for="`item-${category.category}-${index}`">{{ item }}</label>
                    </li>
                </ul>
            </Card>
        </div>

        <div v-else class="no-data">
            <p>Your shopping list is empty or hasn't been generated yet.</p>
            <p>Select options above and click "Generate New List".</p>
        </div>

    </div>
</template> 

<script setup>
import { onMounted, ref } from 'vue';
import api from '@/lib/api';
import Card from '@/components/Card.vue';

const isLoading = ref(false);
const error = ref(null);
const shoppingList = ref(null);

const settings = ref({
    days: 1,
    include_dependents: false
});

const loadLatest = async () => {
    isLoading.value = true;
    error.value = null;
    try {
        const response = await api.get('api/v1/meals/shopping-list/latest');
        
        if (response.data.total_items > 0) {
            shoppingList.value = response.data;
        }
    } catch (err) {
        console.error(err);
        if (err.response?.status !== 404) {
             error.value = "Could not load saved list.";
        }
    } finally {
        isLoading.value = false;
    }
};

const generateList = async () => {
    isLoading.value = true;
    error.value = null;
    try {
        const response = await api.post('api/v1/meals/shopping-list', settings.value);
        shoppingList.value = response.data;
    } catch (err) {
        console.error(err);
        error.value = err.response?.data?.detail || "Error generating list. Ensure plans exist for selected dates.";
    } finally {
        isLoading.value = false;
    }
};

onMounted(() => {
    loadLatest();
});
</script>

<style scoped>
.container {
    max-width: 900px;
    margin: 2rem auto;
    padding: 1rem;
}

.header-actions {
    margin-bottom: 1rem;
}

.controls {
    background: #f8f9fa;
    padding: 1.5rem;
    border-radius: 8px;
    border: 1px solid #e9ecef;
    margin-bottom: 2rem;
    display: flex;
    gap: 1.5rem;
    align-items: flex-end;
    flex-wrap: wrap;
}

.control-group {
    display: flex;
    flex-direction: column;
    gap: 5px;
}

.control-group label {
    font-size: 0.9rem;
    font-weight: 600;
    color: #555;
}

.control-group select {
    padding: 8px 12px;
    border: 1px solid #ccc;
    border-radius: 4px;
    font-size: 0.95rem;
    min-width: 150px;
}

.control-group.checkbox {
    flex-direction: row;
    align-items: center;
    padding-bottom: 8px; 
}

.control-group.checkbox input {
    width: 18px;
    height: 18px;
    margin-right: 8px;
    cursor: pointer;
}

.control-group.checkbox label {
    cursor: pointer;
}

.btn-primary {
    background-color: var(--primary-color, #27ae60);
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 4px;
    cursor: pointer;
    font-weight: 600;
}
.btn-primary:disabled {
    background-color: #9ca3af;
    cursor: not-allowed;
}

.btn-secondary {
    text-decoration: none;
    color: #666;
    font-size: 0.9rem;
}

.meta-info {
    background: #e8f5e9;
    color: #2e7d32;
    padding: 10px 15px;
    border-radius: 6px;
    margin-bottom: 1.5rem;
    display: flex;
    gap: 2rem;
    font-size: 0.95rem;
}

.meta-info p {
    margin: 0;
}

.shopping-list-container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1.5rem;
}

.item-list {
    list-style: none;
    padding: 0;
    margin: 0;
    text-align: left;
}

.list-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.5rem 0;
    border-bottom: 1px solid #eee;
}
.list-item:last-child {
    border-bottom: none;
}

.item-checkbox {
    width: 1.15rem;
    height: 1.15rem;
    flex-shrink: 0;
    cursor: pointer;
}

.list-item label {
    font-size: 0.95rem;
    cursor: pointer;
    transition: all 0.2s;
}

.item-checkbox:checked + label {
    text-decoration: line-through;
    opacity: 0.6;
}

.loading-state, .error-state, .no-data {
    padding: 2rem;
    text-align: center;
    background-color: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    margin-top: 1.5rem;
}

.error-state {
    color: #b91c1c;
    background-color: #fff1f2;
    border: 1px solid #fecaca;
}

.spinner {
    border: 4px solid #f3f3f3;
    border-top: 4px solid var(--primary-color, #27ae60);
    border-radius: 50%;
    width: 30px;
    height: 30px;
    animation: spin 1s linear infinite;
    display: inline-block;
    margin-top: 1rem;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}
</style>