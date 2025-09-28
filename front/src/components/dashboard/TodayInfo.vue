<template>
<div class="cards-container">
    <Card 
    v-for="card_data in cardsData"
    :key="card_data.title"
    :title="card_data.title">
    <ul
        v-if="card_data.content && card_data.content.length > 0">
        <li v-for="item in card_data.content"
            :key="item.id">
            {{ item.text }}
        </li>
    </ul>
    <p v-else>No data to show</p>
    <button 
            v-if="card_data.title !== 'Interaction alerts'" 
            class="btn-primary"
            @click="viewFullSchedule(card_data.title)">
            View Full Schedule!
        </button>
    </Card>
</div>
</template> 

<script setup>
import Card from '@/components/Card.vue';
defineProps({
    cardsData:{
        type: Array,
        required: true,
    },
})
const emit = defineEmits(['view-full-schedule']);
const viewFullSchedule = (title) => {
  emit('view-full-schedule', title);
};
</script>

<style scoped>
.cards-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  margin: 5% 0 5% 0;
}

.btn-primary{
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    padding: 8px 16px;
    border-radius: var(--border-radius-md);
    border: none;
    background-color: var(--primary-color);
    color: var(--white-color);
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    }
</style>