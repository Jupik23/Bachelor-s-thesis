import os, httpx, asyncio, logging
from typing import List, Optional, Dict
from app.schemas.spoonacular import Recipe
from app.schemas.health_form import DietPreferences, HealthFormCreate, DietPreferences

class Spoonacular():
    def __init__(self):
        self.base = "https://api.spoonacular.com"
        self.api_key = os.getenv("SPOONACULAR_API_KEY")
        self.headers = {
            "Content-Type": "application/json"
        }

    async def _make_request(self, endpoint: str, params: Dict[str] = None):
        if params in None:
            params = {}

        params["api_key"] = self.api_key

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
                raise logging.error(f"Request error: {str(e)}")

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
            user_intolerances_input = [i.strip().lower() for i in health_form.allergies.split(",")]
            valid_intolerances = [i for i in user_intolerances_input if i in intolerances]

            if valid_intolerances:
                params["intolerances"] = ",".join(valid_intolerances)
        
        return params


    async def generate_plan(self, healt_form: HealthFormCreate, days: int= 1):
        params = self._format_diet_params(healt_form)
        params.update({
            "timeFrame": "day" if days == 1 else "week",
            "targetCalories" : 2000
        })
        #trzeba jakiegos handlera zaimplemntaować + inicjalizacja tutaj obiektów Meal :))) 
        data = await self._make_request("mealplanner/generate", params)
        return data.json()
        

        