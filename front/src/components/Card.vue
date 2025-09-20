<template>
    <div class="card">
        <slot> </slot>
    </div>
</template>

<style scoped>
.card {
  background: var(--surface);
  border-radius: var(--radius);
  box-shadow: var(--shadow-md);
  padding: var(--space-8);
  border-color: cyan
}
</style>