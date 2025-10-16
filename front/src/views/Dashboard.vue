<template>
    <div class="container">
        <h1>Health Dashboard!</h1>
            <div>
                <div class="date-change-log">
                    <p id="date">Today's overview: {{today}}</p>
                    <RouterLink to="/health_form">Change Health metrics</RouterLink>
                </div>
                <Stats :stats="stats"></Stats>
                <TodayInfo :cardsData="cards_data"></TodayInfo>
            </div> 
    </div>

</template>
<script setup>
import {onMounted, ref, renderSlot} from "vue"
import Stats from "@/components/dashboard/Stats.vue";
import TodayInfo from "@/components/dashboard/TodayInfo.vue";
import api from "@/lib/api.js"
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
        content: [{id: 1, text: "None!"},]
    },
])

const stats = ref([
    {
        title: "Medications Taken",
        value: 2,
        unit: "/3",
    },
    {
        title: "Target Calories",
        value: 0,
        unit: "kcal",
    },
    {
        title: "Health Score",
        value: 95,
        unit: "%",
    },
])
const getStats = async () => {
    try{
        const response = await api.get("/api/v1/health-form/me/calories");
        const response2 = await api.post("/api/v1/meals/generate");
        const targetCalories = response?.data?.target_calories ?? 0;
        stats.value[1].value = targetCalories;
        console.log(response2)
    }catch(error){
        console.log(error)
    }
}
onMounted(() => {
    getStats()
})
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
</style>