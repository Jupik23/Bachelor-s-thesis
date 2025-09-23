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
  background-color: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
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
  color: #27ae60;
  margin-bottom: 1rem;
}
.card-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 0.5rem;
}
.card-description {
  font-size: 1rem;
  color: #7f8c8d;
  line-height: 1.6;
}
</style>