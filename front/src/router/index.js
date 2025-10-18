import { createRouter, createWebHistory } from "vue-router";
import { userAuthStore } from "@/lib/auth";

const routes = [
    { path: "/", name: "home", 
        component: () => import("@/views/Home.vue") ,
        meta: {
            requiresAuth: false,
            forVisitors: true,
        }
    },
    { path: "/login", name: "login",
        component: () => import("@/views/Login.vue"), 
        props: { initialMode: "login" },
        meta: {
            requiresAuth: false,
            forVisitors: true,
        }
    },
    { path: "/register", name: "register",
        component: () => import("@/views/Register.vue"), 
        props: { initialMode: "register" },
        meta: {
            requiresAuth: false,
            forVisitors: true,
        }
    },
    { path: "/health-form", 
        name: "healthform", 
        component: () => import("@/views/HealthForm.vue"),
        meta: {
            // uncomment after building FE
            // requiresAuth: true,
            // forVisitors: false,
            forVisitors: true,
        }
    },
    {path: "/dashboard",
        name: "dashboard",
        component: () => import("@/views/Dashboard.vue"),
        meta: {
            forVisitors: true
        }
    },
    {path: "/meal-plan",
        name: "mealplan",
        component: () => import("@/views/MealPlan.vue")
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes,
})

router.beforeEach(async (to, from, next) => {
    const authStore = userAuthStore();
    if (!authStore.isAuthenticated && authStore.token) {
        await authStore.checkToken();
    }
    const requiresAuth = to.matched.some(record => record.meta.requiresAuth);
    const isAuthenticated = authStore.isLoggedIn;
    if (requiresAuth && !isAuthenticated) {
        next({
            name: 'login',
            query: { redirect: to.fullPath }
        });
    }
    else if (to.name === 'login' && isAuthenticated) {
        const redirectPath = to.query.redirect || { name: 'health_form' };
        next(redirectPath);
    }
    else {
        next();
    }
})

export default router;