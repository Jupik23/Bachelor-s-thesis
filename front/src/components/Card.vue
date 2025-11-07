<template>
    <div class="card">
        <div class="card-icon">
            <slot name="icon"></slot>
        </div>
        <h3 class="card-title">{{ title }}</h3>
        <div class="card-content">
          <slot></slot>
        </div>
    </div>
</template> 
<script setup>
defineProps({
    title:{
        type: String,
        required: true
    }
})
</script>
<style scoped>
</style>