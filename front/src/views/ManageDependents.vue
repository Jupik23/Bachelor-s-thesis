<template>
  <div class="manage-dependents-view">
    <h1>Manage Dependents</h1>
    
    <div v-if="isLoading" class="loading">
      Loading dependents...
    </div>

    <div v-if="error" class="error-message">
      {{ error }}
    </div>

    <div v-if="!isLoading && !error" class="content-wrapper">
      <DependentList :dependents="dependents" />

      <AddDependentForm @dependent-created="fetchDependents" />
    </div>
  </div>
</template>

<script>
import DependentList from '@/components/addUser/DependentList.vue'; 
import AddDependentForm from '@/components/addUser/AddDependentForm.vue'; 
import { getMyDependents } from '@/lib/api.js'; 

export default {
  name: 'ManageDependents',
  components: {
    DependentList,
    AddDependentForm
  },
  data() {
    return {
      dependents: [],
      isLoading: false,
      error: null
    };
  },
  methods: {
    async fetchDependents() {
      this.isLoading = true;
      this.error = null;
      try {
        const response = await getMyDependents();
        this.dependents = response.data;
      } catch (err) {
        this.error = 'Failed to load dependents. Please try again later.';
        console.error(err);
      } finally {
        this.isLoading = false;
      }
    }
  },
  created() {
    this.fetchDependents();
  }
}
</script>

<style scoped>
.manage-dependents-view {
  max-width: 800px;
  margin: 20px auto;
  padding: 0 15px;
}

.loading {
  font-size: 1.2em;
  color: #555;
  text-align: center;
  padding: 20px;
}

.error-message {
  color: red;
  background-color: #ffe0e0;
  border: 1px solid red;
  padding: 15px;
  border-radius: 4px;
}
</style>