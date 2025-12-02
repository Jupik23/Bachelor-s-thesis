import os
import httpx
import logging
from typing import Dict, Any, List, Optional
from app.schemas.health_form import HealthFormCreate
from app.schemas.spoonacular import DailyPlanResponse, WeeklyPlanResponse, ComplexSearchResponse, RecipeResponse
from app.services.calculator import CalculatorService

class Spoonacular:
    ACCEPTABLE_DIETS = {
        "gluten free", "ketogenic", "vegetarian", "lacto-vegetarian",
        "ovo-vegetarian", "vegan", "pescetarian", "paleo", "primal", "whole30"
    }
    ACCEPTABLE_INTOLERANCES = {
        "dairy", "egg", "gluten", "grain", "peanut", "seafood",
        "sesame", "shellfish", "soy", "sulfite", "tree nut", "wheat"
    }

    def __init__(self):
        self.base = "https://api.spoonacular.com"
        self.api_key = os.getenv("SPOONACULAR_API_KEY")
        self.headers = {}

    async def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict:
        if params is None:
            params = {}
            
        params["apiKey"] = self.api_key
        endpoint = endpoint.lstrip("/")
        full_url = f"{self.base}/{endpoint}"

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    full_url, 
                    params=params, 
                    headers=self.headers,
                      timeout=15.0
                      )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logging.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
                raise e
            except Exception as e:
                logging.error(f"Request error: {str(e)}")
                raise e

    def _validate_list_param(self, items: Optional[List[str] | str], allowed_set: set) -> Optional[str]:
        if not items:
            return None
        if isinstance(items, str):
            items_list = items.split(',')
        else:
            items_list = items

        valid_items = [i.strip().lower() for i in items_list if i.strip().lower() in allowed_set]
        return ','.join(valid_items) if valid_items else None

    def _format_diet_params(self, health_form: HealthFormCreate) -> Dict[str, Any]:
        params = {}
        diet_str = self._validate_list_param(health_form.diet_preferences, self.ACCEPTABLE_DIETS)
        if diet_str:
            params['diet'] = diet_str

        intolerances_str = self._validate_list_param(health_form.intolerances, self.ACCEPTABLE_INTOLERANCES)
        if intolerances_str:
            params['intolerances'] = intolerances_str

        calc = CalculatorService()
        bmr = calc.calculate_bmr(
            gender=health_form.gender,
            height=health_form.height,
            weight=health_form.weight,
            age=health_form.age
        )
        target_calories = calc.calculate_target_calories(
            bmr,
            health_form.activity_level,
            health_form.calorie_goal
        )
        params["targetCalories"] = target_calories
        return params

    async def generate_meal_plan(self, health_form: HealthFormCreate, time_frame: str = "day"):
        if time_frame not in ["day", "week"]:
            raise ValueError("time_frame must be 'day' or 'week'.")

        params = self._format_diet_params(health_form)
        num_meals = health_form.number_of_meals_per_day

        if num_meals <= 3:
            params.update({"timeFrame": time_frame})
            data = await self._make_request("mealplanner/generate", params=params)
        else:
            params.update({"timeFrame": time_frame})
            data = await self._make_request("mealplanner/generate", params=params)

            target_calories = params["targetCalories"]
            base_meal_calories = target_calories / 3
            additional_meals_needed = num_meals - 3
            calories_per_meal = target_calories / num_meals

            search_queries = ["healthy snack", "light meal", "protein snack"]
            additional_meals = []

            for i in range(additional_meals_needed):
                query = search_queries[i % len(search_queries)]
                search_params = {
                    "query": query,
                    "number": 1,
                    "maxCalories": int(calories_per_meal * 1.2),
                    "minCalories": int(calories_per_meal * 0.8),
                    "addRecipeInformation": "true",
                    "instructionsRequired": "true"
                }
                if params.get('diet'):
                    search_params['diet'] = params['diet']
                if params.get('intolerances'):
                    search_params['intolerances'] = params['intolerances']

                search_result = await self._make_request("recipes/complexSearch", params=search_params)
                if search_result.get('results'):
                    recipe = search_result['results'][0]
                    additional_meals.append({
                        'id': recipe.get('id'),
                        'title': recipe.get('title'),
                        'readyInMinutes': recipe.get('readyInMinutes', 15),
                        'servings': recipe.get('servings', 1)
                    })

            if additional_meals:
                original_meals = data.get('meals', [])
                new_meals = []

                if original_meals:
                    new_meals.append(original_meals[0])

                meals_to_insert_morning = min(additional_meals_needed // 2, len(additional_meals))
                for i in range(meals_to_insert_morning):
                    new_meals.append(additional_meals[i])

                if len(original_meals) > 1:
                    new_meals.append(original_meals[1])

                for i in range(meals_to_insert_morning, len(additional_meals)):
                    new_meals.append(additional_meals[i])

                if len(original_meals) > 2:
                    new_meals.append(original_meals[2])

                data['meals'] = new_meals

                if 'nutrients' in data:
                    adjustment_factor = num_meals / 3
                    data['nutrients']['calories'] = int(data['nutrients'].get('calories', 0) * adjustment_factor)
                    data['nutrients']['protein'] = round(data['nutrients'].get('protein', 0) * adjustment_factor, 2)
                    data['nutrients']['fat'] = round(data['nutrients'].get('fat', 0) * adjustment_factor, 2)
                    data['nutrients']['carbohydrates'] = round(data['nutrients'].get('carbohydrates', 0) * adjustment_factor, 2)

        try:
            if time_frame == "day":
                return DailyPlanResponse(**data)
            else:
                return WeeklyPlanResponse(**data)
        except Exception as e:
            logging.error(f"Pydantic validation error: {e}")
            raise ValueError(f"Invalid response structure: {e}")

    async def search_recipies(
        self,
        query: str,
        diet: Optional[List[str]] = None,
        intolerances: Optional[List[str]] = None,
        number: int = 10
    ) -> ComplexSearchResponse:
        endpoint = "recipes/complexSearch"
        params = {
            "query": query,
            "number": number,
            "addRecipeInformation": "true",
            "instructionsRequired": "true"
        }

        diet_param = self._validate_list_param(diet, self.ACCEPTABLE_DIETS)
        if diet_param:
            params["diet"] = diet_param

        intolerances_param = self._validate_list_param(intolerances, self.ACCEPTABLE_INTOLERANCES)
        if intolerances_param:
            params["intolerances"] = intolerances_param

        data = await self._make_request(endpoint, params=params)
        return ComplexSearchResponse.model_validate(data) if data else ComplexSearchResponse(results=[], totalResults=0)

    async def get_recipe_information(self, recipe_id: int) -> Optional[RecipeResponse]:
        endpoint = f"recipes/{recipe_id}/information"
        params = {"includeNutrition": "false"}
        data = await self._make_request(endpoint, params=params)
        return RecipeResponse.model_validate(data) if data else None
