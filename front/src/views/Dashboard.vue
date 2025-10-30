<template>
    <div class="container">
        <h1>Health Dashboard!</h1>
            <div>
                <div class="date-change-log">
                    <p id="date">Today's overview: {{today}}</p>
                    <RouterLink to="/health-form">Change Health metrics</RouterLink>
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
const formatTime = (inputTime) => {
    if (!inputTime) return '';
    try {
        const parts = inputTime.split(":");
        return `${parts[0]}:${parts[1]}`;
    } catch (e) {
        return String(inputTime).substring(0, 5);
    }
};
const cards_data = ref([
    {
        title: "Todays medication",
        content: [],
    },
    {
        title: "Todays meals",
        content: []
    },
    {
        title: "Interaction alerts",
        content: []
    },
])

const stats = ref([
    {
        title: "Medications Taken",
        value: 0,
        unit: "/0",
    },
    {
        title: "Target Calories",
        value: 0,
        unit: "kcal",
    },
    {
        title: "Health Score",
        value: 95, //in future there will be algorithm for this :keku:
        unit: "%",
    },
])
const getStats = async () => {
    try{
        const response = await api.get("/api/v1/meals/today");
        const planData = response.data;
        if (planData.medications && planData.medications.length > 0) {
            const takenCount = planData.medications.filter(med => med.taken).length;
            const totalCount = planData.medications.length;
            stats.value[0].value = takenCount;
            stats.value[0].unit = `/${totalCount}`;
        }
        if (planData.total_calories > 0){
            stats.value[1].value = planData.total_calories
        }
        else{
            const calorieResponse = await api.get("/api/v1/health-form/me/calories");
            stats.value[1].value = calorieResponse?.data?.target_calories ?? 0; 
        }

        if (planData.medications && planData.medications.length > 0) {
            cards_data.value[0].content = planData.medications.map(med => ({
                id: med.id,
                text: `${med.name} at ${formatTime(med.time)}`
            }));
        } else {
            cards_data.value[0].content = [{ id: 1, text: "No medications for today." }];
        }

        if (planData.meals && planData.meals.length > 0) {
            cards_data.value[1].content = planData.meals.map(meal => ({
                id: meal.id,
                text: `${meal.meal_type.toUpperCase()}: ${meal.description.split('.')[0]}`
            }));
        } else {
            cards_data.value[1].content = [{ id: 1, text: "No meals planned for today." }];
        }

        if (planData.interactions && planData.interactions.length > 0) {
            cards_data.value[2].content = planData.interactions.map((alert, index) => ({
                id: index,
                text: `${alert.severity}: ${alert.medication_1} & ${alert.medication_2}`
            }));
        } else {
            cards_data.value[2].content = [{ id: 1, text: "No significant interactions found." }];
        }
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