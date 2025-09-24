<template>
    <footer>
        WellPlan {{ year }}
    </footer>
</template> 

<script setup>
const today = new Date();
const year = today.getFullYear()
</script>

<style scoped>
footer{
    display: flex;
    justify-content: center;
    background-color: #f8f9fa;
}
</style>