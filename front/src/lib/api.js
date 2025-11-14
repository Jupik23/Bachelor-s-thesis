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

export const getMyDependents = () => {
  return api.get('api/v1/dependents/my');
};

export const createDependent = (dependentData) => {
  return api.post('api/v1/dependents/create', dependentData);
};

export const getDependentPlan = (dependentId) => {
  return api.get(`api/v1/dependents/${dependentId}/plan/today`);
};

export const getRecipeDetails = (recipeId) => {
  return api.get(`/api/v1/recipes/${recipeId}`);
};
export default api;