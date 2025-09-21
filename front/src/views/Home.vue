<template>
  <BaseLayout>
    <section class="section">
      <div class="container stack-6">
        <div class="grid-2">
          <section class="hero">
            <h2>Calories Counter and ingredients reactions</h2>
            <p>Lorem ipsum dolor sit amet…</p>
          </section>
          <section class="hero">
            <h2>Reactions between medicaments and ingredients</h2>
            <p>Lorem ipsum dolor sit amet…</p>
          </section>
        </div>

        <div class="card ta-center stack-6 mt-8">
          <p>So if you want to join the awesome community, join us right now!</p>
          <div class="center" style="gap: var(--space-4);">
            <RouterLink class="button" to="/login">Login</RouterLink>
            <RouterLink class="button button--outline" to="/register">Register</RouterLink>
          </div>
        </div>
      </div>
    </section>
  </BaseLayout>
</template>

<script setup>
import { RouterLink } from 'vue-router'
import BaseLayout from '../layouts/Base.vue'
</script>
