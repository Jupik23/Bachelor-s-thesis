<template>
    <div class="container">
        <h1>Shopping List</h1>
        <p>Your shopping list for today's plan!</p>
        <RouterLink to="/todays-plan" class="btn-secondary">Back to plan</RouterLink>
        <div v-if="isLoading" class="loading-state">
            <p>Generating your shopping list...</p>
            <div class="spinner"></div>
        </div>
        <div v-else-if="error" class="error-state">
            <p>Error generating list: {{ error }}</p>
            <p>Please ensure you have a plan generated for today.</p>
        </div>
        <div v-else-if="shoppingList && shoppingList.categories.length > 0" class="shopping-list-container">
            <Card v-for="category in shoppingList.categories" :key="category.category" :title="category.category">
                <ul class="item-list">
                    <li v-for="(item, index) in category.items" :key="index" class="list-item">
                        <input type="checkbox" :id="`item-${category.category}-${index}`" class="item-checkbox" />
                        <label :for="`item-${category.category}-${index}`">{{ item }}</label>
                    </li>
                </ul>
            </Card>
        </div>
        <div v-else="no-data">
            <p>Your shopping list is empty</p>
            <p>Make sure you have generated plan for today!</p>
            <RouterLink to="/todays-plan" class="btn-secondary">Generate it now!</RouterLink>
        </div>

    </div>
</template> 
<script setup>
import {onMounted, ref} from 'vue'
import api from '@/lib/api';
import Card from '@/components/Card.vue';

const isLoading = ref(true);
const error = ref(null);
const shoppingList = ref(null);

const getShoppingList = async () => {
    isLoading.value = true;
    error.value = null;
    try{
        const reponse = await api.get('api/v1/meals/shopping-list');
        shoppingList.value = reponse.data;
    }catch(error){
        error.value = "Error while generating shopping list"
    }finally{
        isLoading.value = false;
    }
};
onMounted(() => {
    getShoppingList();
})
</script>
<style scoped>
.container {
    max-width: 900px;
    margin: 2rem auto;
    padding: 1rem;
}

.shopping-list-container {
    display: grid;
    /* Tworzy responsywną siatkę kart */
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1.5rem;
    margin-top: 2rem;
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
    border-bottom: 1px solid var(--border-color);
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
    background-color: var(--white-color);
    border-radius: var(--border-radius-md);
    box-shadow: var(--shadow-sm);
    margin-top: 1.5rem;
}
.error-state {
    color: #b91c1c;
    background-color: #fff1f2;
    border: 1px solid #fecaca;
}
.spinner {
    border: 4px solid #f3f3f3;
    border-top: 4px solid var(--primary-color);
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