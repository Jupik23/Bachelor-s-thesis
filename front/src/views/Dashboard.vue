<template>
    <div class="container">
        <h1>Health Dashboard!</h1>
            <div>
                <div class="date-change-log">
                    <p id="date">Today's overview: {{today}}</p>
                    <button>Change Health metrics</button>
                </div>
                <div class="stats-container">
                    <Card
                        class="stat-card`"
                        v-for="stat in stats"
                        :key="stat.title"
                        :title="stat.title">
                        <div class="stat-data-row"> 
                            <p class="stat-value">{{ stat.value }}</p>
                            <p class="stat-unit" v-if="stat.unit">{{ stat.unit }}</p>
                        </div>
                    </Card>
                </div>
                <div class="cards-container">
                    <Card 
                    v-for="card_data in cards_data"
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

            </div> 
    </div>

</template>
<script setup>
import {ref} from "vue"
import Card from "@/components/Card.vue"
const today = new Date().toDateString();
const cards_data = ref([
    {
        title: "Todays medication",
        content: [
            { id: 1, text: "Vitamin D (1 tab) at 08:00" },
            { id: 2, text: "Magnessium (2 tabs) at 20:00" },
        ],
    },
    {
        title: "Todays meals",
        content: [
            { id: 1, text: "Breakfast 400 kcal"},
            { id: 2, text: "Lunch 300 kcal"},
            { id: 3, text: "Dinner 900 kcal"},
        ]
    },
    {
        title: "Interaction alerts",
    },

])

const stats = ref([
    {
        title: "Medications Taken",
        value: 2,
        unit: "/3",
    },
    {
        title: "Remaining Calories",
        value: 1200,
        unit: "kcal",
    },
    {
        title: "Health Score",
        value: 95,
        unit: "%",
    },
])
</script>

<style scoped>

.stats-card {
    background-color: var(--secondary-color, #e0f7fa); 
    box-shadow: var(--shadow-sm);
    padding: 1rem; 
    text-align: center;
    max-width: none; 
}
.date-change-log {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background-color: var(--white-color);
  border-radius: var(--border-radius-md);
  box-shadow: var(--shadow-sm);
}

.date-change-log p {
  margin: 0;
  font-size: 1rem;
  color: var(--text-color-dark);
}

.date-change-log button, .btn-primary {
  padding: 8px 16px;
  border-radius: var(--border-radius-md);
  border: none;
  background-color: var(--primary-color);
  color: var(--white-color);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary{
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
}

.date-change-log button:hover {
  background-color: var(--primary-color-hover);
  transform: translateY(-2px);
}

.cards-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  margin: 5% 0 5% 0;
}

.stats-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); 
  gap: 1rem;
}

.stats-card .card-title {
    font-size: 0.9rem;
    color: var(--text-color-dark);
    font-weight: 500;
    margin-bottom: 0.5rem;
}

.stat-value {
    font-size: 2rem; 
    font-weight: 700;
    color: var(--primary-color);
    line-height: 1;
    margin: 0;
}

.stat-unit {
    font-size: 0.8rem;
    color: var(--text-color-subtle);
    margin: 0;
}

</style>