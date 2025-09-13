import { createRouter, createWebHashHistory } from "vue-router";
import { userAuthStore } from "@/lib/auth";

const routes = [
    { path: "/", name: "home", 
        component: () => import("../views/Home.vue") ,
        meta: {
            requiresAuth: false,
            forVisitors: true,
        }
    },
    { path: "/login", name: "login",
        component: () => import("../views/Login.vue"), 
        props: { initialMode: "login" },
        meta: {
            requiresAuth: false,
            forVisitors: true,
        }
    },
    { path: "/register", name: "register",
        component: () => import("../views/Register.vue"), 
        props: { initialMode: "register" },
        meta: {
            requiresAuth: false,
            forVisitors: true,
        }
    },
    { path: "/about", 
        name: "about", 
        component: () => import("../views/About.vue"),
        meta: {
            requiresAuth: false,
            forVisitors: true,
        }
    },
    { path: "/health_form", 
        name: "health_form", 
        component: () => import("../views/HealthForm.vue"),
        meta: {
            requiresAuth: true,
            forVisitors: false,
        }
    }
]

const router = createRouter({
    history: createWebHashHistory(),
    routes,
})

router.beforeEach(async (to ,from , next) => {
    const authStore = userAuthStore()

    if (!authStore.isAuthenticated && !authStore.token){
        await authStore.checkToken()
    }
    const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
    const forVisitors = to.matched.some(record => record.meta.forVisitors)
    const isAuthenticated = authStore.isLoggedIn

    if(requiresAuth && !isAuthenticated){
        next({
            name: 'login',
            query: {redirect: to.fullPath}
        })
    }else if(forVisitors && isAuthenticated && (to.name === 'login' || to.name === 'register')){
        next({
            name: "about"
        })
    }else{
        next()
    }
})

export default router;