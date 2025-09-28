<template>
    <section class="features-section">
        <div class="container">
            <h2 class="section-title">Why Choose Our Platform?</h2>
            <p class="section-subtitle">
                The only solution that combines comprehensive diet and medication management<br>
                with intelligent interaction monitoring.
            </p>
            <div class="cards-container">
                <Card
                v-for="feature in features"
                :key="feature.title"
                :title="feature.title">
                <template #icon>{{ feature.icon }}</template>
                {{ feature.description }}
                </Card>
            </div>
      </div>
    </section>
</template> 

<script setup>
import Card from '@/components/Card.vue';
import { ref } from 'vue';

const features = ref([
    {
        icon: "",
        title: 'Smart Medication Tracking',
        description: 'Advanced medication management with interaction alerts and personalized reminders.'
    },
    {
        icon: "",
        title: 'Intelligent Diet Planning',
        description: 'Personalized meal plans considering allergies, intolerances, and nutritional needs.'
    },
    {
        icon: "",
        title: 'Interaction Monitoring',
        description: 'Real-time alerts for food-drug and drug-drug interactions to keep you safe.'
    },
    {
        icon: "",
        title: 'Calendar Integration',
        description: 'Seamless sync with Google Calendar for medication schedules and meal planning..'
    },
    {
        icon: "",
        title: 'Caregiver Support',
        description: 'Perfect for parents monitoring children or caregivers managing elderly health.'
    },
    {
        icon: "",
        title: 'HIPAA Compliant',
        description: 'Enterprise-grade security ensuring your health data remains private and secure.'
    },
])
</script>
<style scoped>
.features-section {
  background-color: var(--background-color-light);
  padding: 5rem 2rem;
  text-align: center;
}
.container {
  max-width: 1200px;
  margin: 0 auto;
}
.section-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--text-color-dark);
  margin-bottom: 1rem;
}
.section-subtitle {
  font-size: 1.1rem;
  color: var(--text-color-subtle);
  margin-bottom: 4rem;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}
.cards-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}
</style>