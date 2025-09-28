<template>
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
    </template>     

<script setup>
import Card from "@/components/Card.vue"
defineProps({
  stats: {
    type: Array,
    required: true,
  },
});
</script>

<style scoped>
.stats-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem; 
}
.stat-card {
  background-color: var(--secondary-color, #e0f7fa);
  box-shadow: var(--shadow-sm);
  padding: 1rem;
  text-align: center;
}

.stat-data-row {
  display: flex;
  flex-direction: row;
  align-items: baseline;
  justify-content: center;
  gap: 0.5rem;
  margin-top: 0.2rem;
}

.stat-value {
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--primary-color);
  line-height: 1;
  margin: 0;
}

.stat-unit {
  font-size: 0.9rem;
  color: var(--text-color-subtle);
  margin: 0;
  font-weight: 600;
}
</style>