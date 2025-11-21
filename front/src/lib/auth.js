import api, { setAuthToken, clearAuthToken } from "./api";
import { defineStore } from "pinia"

export const userAuthStore = defineStore("auth", {
    state: () => ({
        user: null,
        token: localStorage.getItem("token") || null,
        isAuthenticated: false,
    }),
    getters: {
        isLoggedIn: (state) => state.isAuthenticated && state.token !== null,
    },
    actions: {
        async login(credentials) {
            try{
                const response = await api.post("api/v1/auth/session", credentials)
                const {access_token} = response.data
                this.token = access_token
                this.isAuthenticated = true

                localStorage.setItem("token", access_token)
                setAuthToken(access_token)
                return {success:true} 
            }catch(error){
                return {success: false, error: error.response?.data?.message || "Login failed"}
            }   
    },
    async logout(){
        this.token = null
        this.isAuthenticated = false;
        localStorage.removeItem("token")
        clearAuthToken()
    },
    async checkToken(){
        const token = localStorage.getItem("token")
        if(!token){
            this.logout()
            return false
        }
        try {
            setAuthToken(token)
            const response = await api.get("/api/v1/users/me")
            this.user = response.data
            this.token = token
            this.isAuthenticated = true
            return true
        }catch(error){
            this.logout()
            return false
        }
    },
    async initializeAuth(){
        const token = localStorage.getItem("token")
        if(token){
            setAuthToken(token)
            this.token = token
            await this.checkToken()
        }
    }
    }
})