import { isProxy } from "vue";
import { createRouter, createWebHashHistory } from "vue-router";

const routes = [
    { path: "/", name: "home", component: () => import("../views/Home.vue") },
    { path: "/login", name: "login", component: () => import("../views/Login.vue"), props: { initialMode: "login" } },
    { path: "/register", name: "register", component: () => import("../views/Register.vue"), props: { initialMode: "register" } },
    { path: "/about", name: "about", component: () => import("../views/About.vue") },
    { path: "/health_form", name: "healt_form", component: () => import("../views/HealthForm.vue")}
]

const router = createRouter({
    history: createWebHashHistory(),
    routes,
})

export default router;