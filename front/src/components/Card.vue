<template>
    <div class="card">
        <div class="card-icon">
            <slot name="icon"></slot>
        </div>
        <h3 class="card-title">{{ title }}</h3>
        <p class="card-description">{{ description }}</p>
    </div>
</template> 
<script setup>
defineProps({
    title:{
        type: String,
        required: true
    }, 
    description:{
        type: String,
        required: true
    }
})
</script>
<style scoped>
.card {
  background-color: var(--white-color);
  padding: 2rem;
  border-radius: var(--border-radius-md);
  box-shadow: var(--shadow-md);
  text-align: left;
  max-width: 350px;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 16px rgba(0,0,0,0.12);
}
.card-icon {
  font-size: 2rem;
  color: var(--primary-color);
}
.card-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-color-dark);
  margin-bottom: 0.5rem;
}
.card-description {
  font-size: 1rem;
  color: var(--text-color-subtle);
  line-height: 1.6;
}
</style>