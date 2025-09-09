import os, httpx, asyncio, logging
from typing import Dict, Any
from app.schemas.spoonacular import Recipe
from app.schemas.health_form import HealthFormCreate, DietPreferences

class Spoonacular():
    def __init__(self):
        self.base = "https://api.spoonacular.com"
        self.api_key = os.getenv("SPOONACULAR_API_KEY")
        self.headers = {
            "Content-Type": "application/json"
        }

    async def _make_request(self, endpoint: str, params: Dict[str, Any] = None):
        if params is None:
            params = {}

        params["apiKey"] = self.api_key

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base}/{endpoint}",
                    params = params,
                    headers = self.headers,
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logging.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
                raise 
            except Exception as e:
                logging.error(f"Request error: {str(e)}")
                raise 

    def _format_diet_params(self, health_form: HealthFormCreate):
        params = {}

        if health_form.diet_preferences:
            preferences = [
                "gluten free", "ketogenic", "vegetarian", "lacto-vegetarian", 
                "ovo-vegetarian", "vegan", "pescetarian", "paleo", "primal"
                ]
            user_diet_input = [d.strip().lower() for d in health_form.diet_preferences.split(",")]
            valid_diet = [d for d in user_diet_input if d in preferences]

            if valid_diet:
                params["diet"] = ",".join(valid_diet)

        if health_form.intolerances:
            intolerances = [
                "dairy", "egg", "gluten", "grain", "peanut", "seafood", 
                "sesame", "shellfish", "soy", "sulfite", "tree nut", "wheat"
            ]
            user_intolerances_input = [i.strip().lower() for i in health_form.intolerances.split(",")]
            valid_intolerances = [i for i in user_intolerances_input if i in intolerances]

            if valid_intolerances:
                params["intolerances"] = ",".join(valid_intolerances)
        if (health_form.height and health_form.weight):
            target_calories = int((10 * health_form.weight) + int(6.25*health_form.height) - 100)
            params["targetCalories"] = target_calories
        return params


    async def generate_meal_plan(self, health_form: HealthFormCreate, days: int= 1):
        params = self._format_diet_params(health_form)
        params.update({
            "timeFrame": "day" if days == 1 else "week"
        })
        print(self.api_key)
        print(params)
        #trzeba jakiegos handlera zaimplemntaować + inicjalizacja tutaj obiektów Meal :))) 
        data = await self._make_request("mealplanner/generate", params)
        return data
        

        