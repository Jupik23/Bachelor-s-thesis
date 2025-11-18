import os, httpx, asyncio, logging
from typing import Dict, Any
from app.schemas.health_form import HealthFormCreate
from app.schemas.spoonacular import DailyPlanResponse, WeeklyPlanResponse, Recipe, ComplexSearchResponse, RecipeResponse
from app.services.calculator import CalculatorService

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
        ACCEPTABLE_DIETS = {
            "gluten free", "ketogenic", "vegetarian", "lacto-vegetarian", 
            "ovo-vegetarian", "vegan", "pescetarian", "paleo", "primal"
        }
        ACCEPTABLE_INTOLERANCES = {
            "dairy", "egg", "gluten", "grain", "peanut", "seafood", 
            "sesame", "shellfish", "soy", "sulfite", "tree nut", "wheat"
        }
        if health_form.diet_preferences:
            valid_diet = [
                d for d in (p.strip().lower() for p in health_form.diet_preferences) 
                if d in ACCEPTABLE_DIETS     
            ]
            if valid_diet:
                params['diet'] = ','.join(valid_diet)
        
        if health_form.intolerances:
            valid_intolerance = [
                i for i in (p.strip().lower() for p in health_form.intolerances) 
                if i in ACCEPTABLE_INTOLERANCES     
            ]
            if valid_intolerance:
                params['intolerances'] = ','.join(valid_intolerance)
        
        calc = CalculatorService()
        bmr = calc.calculate_bmr(gender = health_form.gender, 
                                 height=health_form.height,
                                 weight=health_form.weight,
                                 age=health_form.age)
        target_calories = calc.calculate_target_calories(bmr, health_form.activity_level,
                                                         health_form.calorie_goal)
        params["targetCalories"] = target_calories

        return params

    async def generate_meal_plan(self, health_form: HealthFormCreate, time_frame: str = "day"):
        if time_frame not in ["day", "week"]:
            raise ValueError("time_frame must be 'day' or 'week'.")
        
        params = self._format_diet_params(health_form)
        params.update({
            "timeFrame": time_frame
        })

        data = await self._make_request("mealplanner/generate/", params=params)
        if data is None:
            raise ValueError("Failed to retrieve data from Spoonacular API. Check API limits or connection.")
        try:
            if time_frame == "day":
                validated_plan  = DailyPlanResponse(**data)
                return validated_plan
            else:
                validated_plan = WeeklyPlanResponse(**data)
                return validated_plan
        except Exception as e:
            logging.error(f"Pydantic validation error for Spoonacular response: {e}")
            raise ValueError(f"Invalid response structure from Spoonacular API: {e}")
        
    async def search_recipies(self, query: str, 
                              diet: str = None,
                              intolerances: str = None, 
                              number: int = 3
    ):
        endpoint = "recipies/complexSearch"
        params = {
            "query": query,
            "number": number,
            "addRecipeInformation": True
        }
        if diet:
            params["diet"] = diet 
        if preferences:
            params["preferences"] = preferences 

        data = await self._make_request(endpoint, params=params)
        
        if data:
            return ComplexSearchResponse.model_validate(data)
        else:
            return ComplexSearchResponse(results=[], totalResults=0)
        
    async def get_recipe_information(self, recipe_id: int):
        endpoint = f"recipes/{recipe_id}/information"
        params = {"includeNutrition": False} 
        
        data = await self._make_request(endpoint, params=params)
        
        if data:
            return RecipeResponse.model_validate(data)
        else:
            return None