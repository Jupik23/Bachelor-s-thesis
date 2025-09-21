<template>
    <transition name="slider">
        <aside v-show="isVisible" class="sidebar">
            <nav class="sidebar__nav">
                <RouterLink to="/dashboard">
                    <span class=sidebar__text>Dashboard</span>
                </RouterLink>
                <RouterLink to="/profile">
                    <span class="sidebar__text">Profile</span>
                </RouterLink>
                <RouterLink to="/settings">
                    <span class=sidebar__text>Settings</span>
                </RouterLink>
                <button class="sidebar__logout" @click="handleLogout">
                    <span class="sidebar__text">Logout</span>
                </button>
            </nav>
        </aside>
    </transition>
</template> 

<script setup>
import { useRouter } from 'vue-router';
import { userAuthStore } from '@/lib/auth';
const props = defineProps({
  isVisible: {
    type: Boolean,
    required: true,
  },
});
const emit = defineEmits(['close']);
const router = useRouter();
const authStore = userAuthStore();
const handleLogout = () => {
    authStore.handleLogout();
    router.push("/login");
}
</script>