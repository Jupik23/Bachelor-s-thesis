<template>
    <div class="container">
        <h1>Health Dashboard!</h1>
            <div>
                <div class="date-change-log">
                    <p id="date">Today's overview: {{today}}</p>
                    <button>Change Health metrics</button>
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
    },
    {
        title: "Interaction alerts",
    },

])
</script>

<style scoped>
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

.date-change-log button {
  padding: 8px 16px;
  border-radius: var(--border-radius-md);
  border: none;
  background-color: var(--primary-color);
  color: var(--white-color);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
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

</style>