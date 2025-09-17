import axios from 'axios';

const api = axios.create({
    baseURL: 'http://localhost:8081',
    timeout: 15000,
    withCredentials: false,
})

let _token = null;

export function setAuthToken(token) {
    _token = token;
}
export function clearAuthToken(token){
    _token = null;
}

api.interceptors.request.use((config) => {
    if (_token) {
        config.headers.Authorization = `Bearer ${_token}`;
    }
    return config;
},
    (err)=> Promise.reject(err)
);

api.interceptors.response.use(
    (res) => res,
    (err) => {
        if (err?.response?.status == 401){
            clearAuthToken()
            window.location.href = "/login"          
        }
        return Promise.reject(err);
    }
);

export const healtFormApi = {
    create: (data) => api.post('api/v1/health_form/create/', data)
}

export default api;