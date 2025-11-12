<template>
  <div class="add-dependent-form">
    <h2>Add New Dependent</h2>
    <p>Create a new account for the person you will be caring for.</p>
    
    <form @submit.prevent="handleSubmit">
      <div class="form-section">
        <h3>User Details</h3>
        <div class="form-group">
          <label for="name">Name:</label>
          <input type="text" id="name" v-model="formData.user_data.name" required>
        </div>
        <div class="form-group">
          <label for="surname">Surname:</label>
          <input type="text" id="surname" v-model="formData.user_data.surname" required>
        </div>
      </div>

      <div class="form-section">
        <h3>Account Credentials</h3>
        <div class="form-group">
          <label for="login">Login (Username):</label>
          <input type="text" id="login" v-model="formData.user_data.login" required>
        </div>
        <div class="form-group">
          <label for="email">Email:</label>
          <input type="email" id="email" v-model="formData.user_auth_data.email" required>
        </div>
        <div class="form-group">
          <label for="password">Password:</label>
          <input type="password" id="password" v-model="formData.user_auth_data.password" required>
        </div>
        <div class="form-group">
          <label for="confirmPassword">Confirm Password:</label>
          <input type="password" id="confirmPassword" v-model="confirmPassword" required>
        </div>
      </div>
      
      <div v-if="error" class="error-message">{{ error }}</div>
      <div v-if="successMessage" class="success-message">{{ successMessage }}</div>

      <button type="submit" :disabled="isLoading">
        {{ isLoading ? 'Creating...' : 'Create Dependent Account' }}
      </button>
    </form>
  </div>
</template>

<script>
import { createDependent } from '@/lib/api.js';

export default {
  name: 'AddDependentForm',
  data() {
    return {
      formData: {
        user_data: {
          name: '',
          surname: '',
          login: ''
        },
        user_auth_data: {
          email: '',
          password: ''
        }
      },
      confirmPassword: '',
      isLoading: false,
      error: null,
      successMessage: null
    };
  },
  methods: {
    async handleSubmit() {
      this.isLoading = true;
      this.error = null;
      this.successMessage = null;

      if (this.formData.user_auth_data.password !== this.confirmPassword) {
        this.error = 'Passwords do not match.';
        this.isLoading = false;
        return;
      }

      try {
        await createDependent(this.formData);
        this.successMessage = 'Dependent account created successfully!';
        
        this.$emit('dependent-created');
        this.formData.user_data = { name: '', surname: '', login: '' };
        this.formData.user_auth_data = { email: '', password: '' };
        this.confirmPassword = '';

      } catch (err) {
        this.error = err.response?.data?.detail || 'An error occurred during account creation.';
      } finally {
        this.isLoading = false;
      }
    }
  }
}
</script>

<style scoped>
.add-dependent-form {
  border: 1px solid #ccc;
  padding: 20px;
  border-radius: 8px;
  background-color: #f9f9f9;
}

.form-section {
  margin-bottom: 20px;
  border-bottom: 1px solid #eee;
  padding-bottom: 15px;
}

.form-section h3 {
  margin-top: 0;
  color: #333;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

.form-group input {
  width: 100%;
  padding: 8px;
  box-sizing: border-box;
  border: 1px solid #ddd;
  border-radius: 4px;
}

button {
  background-color: #007bff;
  color: white;
  padding: 10px 15px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
}

button:disabled {
  background-color: #aaa;
  cursor: not-allowed;
}

.error-message {
  color: red;
  margin-bottom: 15px;
}

.success-message {
  color: green;
  margin-bottom: 15px;
}
</style>