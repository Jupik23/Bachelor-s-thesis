<template>
  <div class="profile-container">
    <h1>Your Profile</h1>

    <div class="grid-layout">
      <Card title="Integrations">
        <div class="integration-item">
          <div class="info">
            <span class="icon">📅</span>
            <span>Google Calendar</span>
          </div>
          <div class="status">
            <span v-if="googleStatus" class="badge connected">Connected</span>
            <span v-else class="badge disconnected">Disconnected</span>
          </div>
        </div>
        
        <div class="actions">
            <button v-if="!googleStatus" @click="connectGoogle" class="btn btn-google">
                Connect Google
            </button>
            <button v-else @click="disconnectGoogle" class="btn btn-danger">
                Disconnect
            </button>
        </div>
      </Card>

      <Card title="Security">
        <form @submit.prevent="handleChangePassword">
            <div class="form-group">
                <label>Current Password</label>
                <input v-model="passForm.current_password" type="password" required />
            </div>
            <div class="form-group">
                <label>New Password</label>
                <input v-model="passForm.new_password" type="password" minlength="6" required />
            </div>
            <div class="form-group">
                <label>Confirm New Password</label>
                <input v-model="passForm.confirm_password" type="password" minlength="6" required />
            </div>
            
            <p v-if="msg.text" :class="msg.type">{{ msg.text }}</p>
            
            <button type="submit" class="btn btn-primary" :disabled="isLoading">
                {{ isLoading ? 'Updating...' : 'Change Password' }}
            </button>
        </form>
      </Card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import Card from '@/components/Card.vue';
import api from '@/lib/api';

const googleStatus = ref(false);
const isLoading = ref(false);
const msg = ref({ text: '', type: '' });
const passForm = ref({
    current_password: '',
    new_password: '',
    confirm_password: ''
});

const checkStatus = async () => {
    try {
        const res = await api.get('/api/v1/integrations/google/status');
        googleStatus.value = res.data.is_connected;
    } catch (e) {
        console.error("Status check failed", e);
    }
};

const connectGoogle = async () => {
    try {
        const res = await api.get('/api/v1/integrations/google/auth-url');
        window.location.href = res.data.authorization_url;
    } catch (e) {
        alert("Error initiating connection");
    }
};

const disconnectGoogle = async () => {
    if(!confirm("Are you sure you want to stop syncing with Google Calendar?")) return;
    try {
        await api.delete('/api/v1/integrations/google/disconnect');
        googleStatus.value = false;
        alert("Disconnected successfully.");
    } catch (e) {
        alert("Failed to disconnect.");
    }
};

const handleChangePassword = async () => {
    msg.value = { text: '', type: '' };
    if (passForm.value.new_password !== passForm.value.confirm_password) {
        msg.value = { text: "New passwords do not match!", type: 'error-msg' };
        return;
    }
    
    isLoading.value = true;
    try {
        await api.put('/api/v1/users/me/password', passForm.value);
        msg.value = { text: "Password changed successfully!", type: 'success-msg' };
        passForm.value = { current_password: '', new_password: '', confirm_password: '' };
    } catch (e) {
        msg.value = { text: e.response?.data?.detail || "Error changing password", type: 'error-msg' };
    } finally {
        isLoading.value = false;
    }
};

onMounted(() => {
    checkStatus();
});
</script>

<style scoped>
.profile-container { max-width: 900px; margin: 0 auto; padding: 2rem; }
.grid-layout { display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 2rem; margin-top: 2rem; }
.integration-item { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; padding-bottom: 1rem; border-bottom: 1px solid #eee; }
.info { display: flex; align-items: center; gap: 10px; font-weight: 600; }
.badge { padding: 4px 10px; border-radius: 12px; font-size: 0.8rem; text-transform: uppercase; font-weight: bold; }
.badge.connected { background-color: #d4edda; color: #155724; }
.badge.disconnected { background-color: #f8d7da; color: #721c24; }
.btn-google { background-color: #DB4437; color: white; border: none; width: 100%; }
.btn-danger { background-color: #dc3545; color: white; border: none; width: 100%; }
.form-group { margin-bottom: 1rem; }
.form-group label { display: block; margin-bottom: 0.5rem; font-weight: 500; }
.form-group input { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
.error-msg { color: red; margin-bottom: 1rem; }
.success-msg { color: green; margin-bottom: 1rem; }
</style>