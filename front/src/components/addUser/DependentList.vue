<template>
  <div class="dependent-list">
    <h2>My Dependents</h2>
    
    <div v-if="!dependents || dependents.length === 0" class="no-dependents">
      You have not added any dependent accounts yet.
    </div>

    <ul v-else>
      <li v-for="dependent in dependents" :key="dependent.id" class="dependent-item">
        <div class="dependent-info">
          <span class="name">{{ dependent.name }} {{ dependent.surname }}</span>
          <span class="login">(@{{ dependent.login }})</span>
        </div>
        <div class="dependent-actions">
          <button @click="managePlan(dependent.id)">
            Manage Plan
          </button>
        </div>
      </li>
    </ul>
  </div>
</template>

<script>
export default {
  name: 'DependentList',
  props: {
    dependents: {
      type: Array,
      required: true
    }
  },
  methods: {
    managePlan(dependentId) {
      // this.$router.push(`/manage/${dependentId}/plan`);
    }
  }
}
</script>

<style scoped>
.dependent-list {
  margin-bottom: 30px;
}

.no-dependents {
  padding: 15px;
  background-color: #f0f0f0;
  border-radius: 4px;
  color: #555;
}

ul {
  list-style-type: none;
  padding: 0;
}

.dependent-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  margin-bottom: 10px;
}

.dependent-info .name {
  font-weight: bold;
  font-size: 1.1em;
}

.dependent-info .login {
  margin-left: 10px;
  color: #666;
  font-style: italic;
}

.dependent-actions button {
  background-color: #28a745;
  color: white;
  padding: 8px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.dependent-actions button:hover {
  background-color: #218838;
}
</style>