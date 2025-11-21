<template>
    <div class="container">
        <h1>Health Dashboard!</h1>
            <div>
                <div class="date-change-log">
                    <p id="date">Today's overview: {{todayDisplay}}</p>
                    <RouterLink to="/health-form">Change Health metrics</RouterLink>
                </div>
                <div v-if="isLoading" class="loading-state">
                    <p>Loading your dashboard...</p>
                    <div class="spinner"></div>
                </div>
                <div v-else-if="error" class="error-state">
                    <p>{{ error }}</p>
                    <p>Could not load dashboard data. Please try again later.</p>
                    <RouterLink to="/health-form" class="btn-primary">Check Health Metrics</RouterLink>
                </div>
                <div v-else class="dashboard-content">
                    <Stats :stats="stats"></Stats>
                    <TodayInfo :cardsData="cards_data"></TodayInfo>
                </div>
                
            </div> 
    </div>

</template>
<script setup>
import {onMounted, ref, renderSlot} from "vue"
import Stats from "@/components/dashboard/Stats.vue";
import TodayInfo from "@/components/dashboard/TodayInfo.vue";
import api, {getMyNotification, getPlanByDate} from "@/lib/api.js"
const isLoading = ref(true);
const error = ref(null)
const today = new Date().toDateString();
const todayDisplay = new Date().toDateString();
const todayApi = new Date().toISOString().split('T')[0];

const formatTime = (inputTime) => {
    if (!inputTime) return '';
    try {
        if (inputTime.includes('T')) {
            inputTime = inputTime.split('T')[1];
        }
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
    {
        title: "Notifications",
        content: [],
    }
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
    isLoading.value = true;
    error.value = null;
    const results = await Promise.allSettled([
        getPlanByDate(todayApi),
        getMyNotification()
    ]);
    const planResult = results[0];
    const notificationResult = results[1];
    if (planResult.status === 'fulfilled') {
        const planData = planResult.value.data;
        if (planData.medications?.length > 0) {
            const takenCount = planData.medications.filter(med => med.taken).length;
            const totalCount = planData.medications.length;
            stats.value[0].value = takenCount;
            stats.value[0].unit = `/${totalCount}`;
        }
        if (planData.total_calories > 0) {
            stats.value[1].value = planData.total_calories;
        } else {
            try {
                const calorieResponse = await api.get("/api/v1/health-form/me/calories");
                stats.value[1].value = calorieResponse?.data?.target_calories ?? 0;
            } catch (e) {}
        }
        if (planData.medications?.length > 0) {
            cards_data.value[0].content = planData.medications.map(med => ({
                id: med.id,
                text: `${med.name} at ${formatTime(med.time)}`
            }));
        } else {
            cards_data.value[0].content = [{ id: 'med-empty', text: "No medications for today." }];
        }
        if (planData.meals?.length > 0) {
            cards_data.value[1].content = planData.meals.map(meal => ({
                id: meal.id,
                text: `${meal.meal_type.toUpperCase()}: ${meal.description.split('.')[0]}`
            }));
        } else {
            cards_data.value[1].content = [{ id: 'meal-empty', text: "No meals planned for today." }];
        }

        if (planData.interactions?.length > 0) {
            cards_data.value[2].content = planData.interactions.map((alert, index) => ({
                id: `int-${index}`,
                text: `${alert.severity}: ${alert.medication_1} & ${alert.medication_2}`
            }));
        } else {
            cards_data.value[2].content = [{ id: 'int-empty', text: "No significant interactions found." }];
        }

    } else {
        cards_data.value[0].content = [{ id: 'no-plan-med', text: "Plan not created yet." }];
        cards_data.value[1].content = [{ id: 'no-plan-meal', text: "Plan not created yet." }];
        cards_data.value[2].content = [{ id: 'no-plan-int', text: "No data available." }];
    }

    if (notificationResult.status === 'fulfilled') {
        const notifications = notificationResult.value.data;
        if (notifications?.length > 0) {
            cards_data.value[3].content = notifications.map(n => ({
                id: n.id,
                text: `[${formatTime(n.sent_at.split('T')[1])}] ${n.message}`
            }));
        } else {
            cards_data.value[3].content = [{ id: 'notify-empty', text: "No new notifications." }];
        }
    } else {
        cards_data.value[3].content = [{ id: 'notify-err', text: "Could not load notifications." }];
    }

    isLoading.value = false;
}
onMounted(() => {
    getStats()
})
</script>

<style scoped>
.date-change-log {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
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