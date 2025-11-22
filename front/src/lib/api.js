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

export const getMyDependents = () => {
  return api.get('api/v1/dependents/my');
};

export const createDependent = (dependentData) => {
  return api.post('api/v1/dependents/create', dependentData);
};

export const getDependentPlanByDate = (dependentId, dateString) => {
  return api.get(`/api/v1/dependents/${dependentId}/plan/date/${dateString}`);
};

export const getRecipeDetails = (recipeId) => {
  return api.get(`/api/v1/recipes/${recipeId}`);
};

export const updateMedDetails = (med_id, data) => {
  return api.patch(`/api/v1/medications/${med_id}`, data);
}

export const updateMedStatus = (med_id, data) => {
  return api.patch(`/api/v1/medications/${med_id}/medication`, data)
}

export const getMyNotification = () => {
  return api.get(`/api/v1/notifications/me`);
}

export const searchRecipes = (query) => {
  return api.get(`/api/v1/meals/search`, {params: {query}});
}

export const replaceMeal = (mealID, new_meal_id) => {
  return api.put(`/api/v1/meals/${mealID}/replace`, {
    spoonacular_recipe_id: new_meal_id,
    meal_type: 'breakfast',
    time: '08:00'
  });
}

export const updateMealDetails = (meal_id, data ) => {
  return api.patch(`/api/v1/meals/${meal_id}/details`, data)
}

export const updateMealsStatus = (meal_id, data) => {
  return api.patch(`/api/v1/meals/${meal_id}`, data)
}

export const getPlanByDate = (dateString) => {
    return api.get(`/api/v1/meals/date/${dateString}`);
}

export const getHealthForm_by_id = (user_id) => {
  return api.get(`/api/v1/health-form/${user_id}`);
}

export const saveHealthForm = (user_id, data) => {
  return api.put(`/api/v1/health-form/${user_id}`, data);
}
export default api;