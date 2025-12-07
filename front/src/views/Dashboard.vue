<template>
    <div class="dashboard-container">
        <header class="header">
            <h1>Health Dashboard</h1>
            <p>Overview for <span class="highlight">{{ todayDisplay }}</span></p>
        </header>
        <div class="grid-actions">
            <RouterLink to="/health-form" class="card action primary">
                <span>Update Metrics</span>
            </RouterLink>
            <RouterLink to="/todays-plan" class="card action">
                <span>Today's Plan</span>
            </RouterLink>
            <RouterLink to="/dependents" class="card action">
                <span>Dependents</span>
            </RouterLink>
        </div>

        <div v-if="isLoading" class="loading">Loading...</div>
        <div v-else-if="error" class="error">{{ error }}</div>
        
        <div v-else class="content-wrapper">
            <div v-if="dependentsData.length > 0" class="dependents-section">
                <div class="card info-card">
                    <h3>Dependents Overview (Today)</h3>
                    <div class="dep-grid">
                        <div v-for="dep in dependentsData" :key="dep.id" class="dep-card">
                            <div class="dep-header">
                                <strong>{{ dep.name }} {{ dep.surname }}</strong>
                                <span :class="['status-badge', dep.plan_status.toLowerCase().replace(' ', '-')]">
                                    {{ dep.plan_status }}
                                </span>
                            </div>
                            
                            <div v-if="dep.plan_status !== 'No Plan'" class="dep-stats">
                                <div class="stat-row">
                                    <span>🍽️ Meals:</span>
                                    <div class="progress-bar">
                                        <div class="fill" :style="{width: (dep.meals_total ? (dep.meals_done/dep.meals_total)*100 : 0) + '%'}"></div>
                                    </div>
                                    <span>{{ dep.meals_done }}/{{ dep.meals_total }}</span>
                                </div>
                                
                                <div class="stat-row">
                                    <span>💊 Meds:</span>
                                    <div class="progress-bar">
                                        <div class="fill meds" :style="{width: (dep.meds_total ? (dep.meds_taken/dep.meds_total)*100 : 0) + '%'}"></div>
                                    </div>
                                    <span>{{ dep.meds_taken }}/{{ dep.meds_total }}</span>
                                </div>
                            </div>
                            <div v-else class="no-plan-msg">
                                <RouterLink :to="`/dependents/${dep.id}/plan`">Generate Plan</RouterLink>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="stats-row">
                <div v-for="(s, i) in stats" :key="i" class="card stat-card">
                    <small>{{ s.title }}</small>
                    <div class="value">{{ s.value }} <span class="unit">{{ s.unit }}</span></div>
                </div>
            </div>
            <div class="grid-info">
                <div v-for="(card, i) in cards_data" :key="i" class="card info-card">
                    <h3>{{ card.title }}</h3>
                    <ul>
                        <li v-for="item in card.content" :key="item.id">
                            {{ item.text }}
                            <button v-if="card.title === 'Notifications' && item.id !== 'notify-empty'" 
                                    @click="handleMarkAsRead(item.id)" class="btn-check">✓</button>
                        </li>
                    </ul>
                    <RouterLink v-if="['Todays medication', 'Todays meals'].includes(card.title)" to="/todays-plan" class="footer-link">
                        View Full Schedule!
                    </RouterLink>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { onMounted, ref } from "vue"
import { useRoute, useRouter } from "vue-router"
import api, { getMyNotification, getPlanByDate, markNotificationAsRead } from "@/lib/api.js"

const route = useRoute();
const router = useRouter();
const isLoading = ref(true);
const error = ref(null)
const todayDisplay = new Date().toDateString();
const todayApi = new Date().toISOString().split('T')[0];
const dependentsData = ref([]);

const formatTime = (t) => {
    if (!t) return '';
    try { return t.includes('T') ? t.split('T')[1].substring(0, 5) : String(t).substring(0, 5); } 
    catch (e) { return ''; }
};

const getDependentsSummary = async () => {
    try {
        const res = await api.get('/api/v1/dependents/dashboard-summary');
        dependentsData.value = res.data;
    } catch (e) {
        console.error("Error fetching dependents:", e);
    }
};

const cards_data = ref([
    { title: "Todays medication", content: [] },
    { title: "Todays meals", content: [] },
    { title: "Interaction alerts", content: [] },
    { title: "Notifications", content: [] }
])

const stats = ref([
    { title: "Medications Taken", value: 0, unit: "/0" },
    { title: "Target Calories", value: 0, unit: "kcal" },
    { title: "Health Score", value: 95, unit: "%" },
])

const getStats = async () => {
    isLoading.value = true;
    error.value = null;
    
    const [planResult, notifResult] = await Promise.allSettled([
        getPlanByDate(todayApi),
        getMyNotification()
    ]);

    if (planResult.status === 'fulfilled') {
        const data = planResult.value.data;
        if (data.medications?.length) {
            stats.value[0].value = data.medications.filter(m => m.taken).length;
            stats.value[0].unit = `/${data.medications.length}`;
        }
        
        if (data.total_calories > 0) {
            stats.value[1].value = data.total_calories;
        } else {
            try {
                const cal = await api.get("/api/v1/health-form/me/calories");
                stats.value[1].value = cal?.data?.target_calories ?? 0;
            } catch (e) {}
        }
        cards_data.value[0].content = data.medications?.length 
            ? data.medications.map(m => ({ id: m.id, text: `${m.name} at ${formatTime(m.time)}` }))
            : [{ id: 'empty', text: "No medications for today." }];

        cards_data.value[1].content = data.meals?.length 
            ? data.meals.map(m => ({ id: m.id, text: `${m.meal_type.toUpperCase()}: ${m.description.split('.')[0]}` }))
            : [{ id: 'empty', text: "No meals planned for today." }];

        cards_data.value[2].content = data.interactions?.length 
            ? data.interactions.map((a, i) => ({ id: i, text: `${a.severity}: ${a.medication_1} & ${a.medication_2}` }))
            : [{ id: 'empty', text: "No significant interactions found." }];
    } else {
        ['medication', 'meals', 'alerts'].forEach((k, i) => cards_data.value[i].content = [{id: 'err', text: "Plan not created yet."}]);
    }

    if (notifResult.status === 'fulfilled' && notifResult.value.data?.length) {
        cards_data.value[3].content = notifResult.value.data.map(n => ({
            id: n.id, text: `[${formatTime(n.sent_at)}] ${n.message}`
        }));
    } else {
        cards_data.value[3].content = [{ id: 'empty', text: "No new notifications." }];
    }

    isLoading.value = false;
}

const handleMarkAsRead = async (id) => {
    try { 
        await markNotificationAsRead(id);
        const notiCard = cards_data.value.find(c => c.title === "Notifications");
        if (notiCard){
            notiCard.content = notiCard.content.filter(n => n.id !== id);
            if (notiCard.content.length === 0) {
                notiCard.content.push({ id: 'notify-empty', text: "No new notifications." });
            }
        }
    }catch (e) {
        alert("Failed to mark notification as read.");
    }
};

const handleGoogleConnection = async (code) => {
    try {
        isLoading.value = true;
        await api.post('/api/v1/integrations/google/connect', { code: code });
        alert("Successfully connected to Google Calendar!");
        router.replace('/dashboard');
    } catch (e) {
        error.value = "Failed to connect Google: " + (e.response?.data?.detail || e.message);
    }
};

onMounted(async () => {
    if (route.query.google_code) {
        await handleGoogleConnection(route.query.google_code);
    }
    await getStats();
    await getDependentsSummary();
});
</script>

<style scoped>
.dashboard-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
    font-family: sans-serif;
    color: #333;
}
.header { margin-bottom: 2rem; border-bottom: 1px solid #eee; padding-bottom: 1rem; }
.header h1 { margin: 0; font-size: 1.8rem; }
.highlight { color: var(--primary-color, #4CAF50); font-weight: bold; }
.grid-actions, .grid-info, .stats-row {
    display: grid;
    gap: 1.5rem;
}
.grid-actions { grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); margin-bottom: 2rem; }
.grid-info { grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); }
.stats-row { grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); margin-bottom: 2rem; }
.card {
    background: #fff;
    padding: 1.5rem;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    transition: transform 0.2s;
    border: 1px solid #f0f0f0;
}
.card:hover { transform: translateY(-2px); border-color: var(--primary-color, #4CAF50); }
.action { 
    display: flex; align-items: center; gap: 10px; 
    text-decoration: none; color: #333; font-weight: 600; 
}
.action.primary { border-left: 4px solid var(--primary-color, #4CAF50); }
.stat-card { text-align: center; }
.stat-card .value { font-size: 2rem; font-weight: bold; color: var(--primary-color, #4CAF50); }
.stat-card .unit { font-size: 1rem; color: #888; }
.info-card h3 { margin-top: 0; border-bottom: 1px solid #eee; padding-bottom: 10px; }
.info-card ul { padding-left: 0; list-style: none; }
.info-card li { padding: 8px 0; border-bottom: 1px solid #f9f9f9; display: flex; justify-content: space-between; }
.footer-link { display: block; margin-top: 1rem; color: var(--primary-color, #4CAF50); text-decoration: none; font-weight: bold; font-size: 0.9rem; }

.btn-check { border: none; background: none; color: green; cursor: pointer; font-weight: bold; }
.loading, .error { text-align: center; padding: 2rem; }
.error { color: red; }

.dependents-section { margin-bottom: 2rem; }
.dep-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1rem;
    margin-top: 1rem;
}
.dep-card {
    background: #f8f9fa;
    border: 1px solid #eee;
    border-radius: 8px;
    padding: 1rem;
}
.dep-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
}
.status-badge {
    font-size: 0.75rem;
    padding: 2px 8px;
    border-radius: 12px;
    font-weight: bold;
}
.status-badge.completed { background: #d4edda; color: #155724; }
.status-badge.in-progress { background: #fff3cd; color: #856404; }
.status-badge.no-plan, .status-badge.empty { background: #f8d7da; color: #721c24; }

.stat-row {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 8px;
    font-size: 0.9rem;
}
.progress-bar {
    flex-grow: 1;
    height: 8px;
    background: #e9ecef;
    border-radius: 4px;
    overflow: hidden;
}
.fill { height: 100%; background: #4CAF50; }
.fill.meds { background: #2196F3; }
.no-plan-msg a { color: #2196F3; font-size: 0.9rem; font-weight: bold; text-decoration: none; }
</style>