from sqlalchemy.orm import Session
from datetime import date, time
from app.services.spoonacular import Spoonacular
from app.services.health_form import HealthFormService
from app.schemas.health_form import HealthFormCreate
from app.schemas.plan import PlanCreate, PlanResponse
from app.schemas.spoonacular import DailyPlanResponse, WeeklyPlanResponse
from app.schemas.plan import ManualMealAddRequest, MealResponse
from app.models.common import MealType
from app.services.medication_service import DrugInteractionService, DrugInteractionResponse, MedicationResponse
from app.schemas.shopping_list import *
from app.crud.medication import get_medications_by_plan_id
from app.crud.plans import create_plan, get_plan_with_meals_by_user_id_and_date
from app.crud.meals import create_meal
import logging
from typing import List
from fastapi import HTTPException,status
import os
import asyncio

MEAL_MAPPING_3_MEALS = {
    0: (MealType.breakfast, time(8, 0)),
    1: (MealType.lunch, time(13, 0)),
    2: (MealType.dinner, time(18, 0)),
}
MEAL_MAPPING_5_MEALS = {
    0: (MealType.breakfast, time(7, 30)),
    1: (MealType.second_breakfast, time(10, 30)),
    2: (MealType.lunch, time(13, 30)),
    3: (MealType.snack, time(16, 30)),
    4: (MealType.dinner, time(19, 30)), 
}

class PlanCreationService:
    def __init__(self, db: Session):
        self.db = db
        self.spoonacular_service = Spoonacular()
        fda_key = os.getenv("OPEN_FDA_API_KEY")
        self.interaction_checker = DrugInteractionService(fda_api_key=fda_key)
        self.health_form_service = HealthFormService(db)

    async def generate_and_save_plan(self, created_by_id, user_id, time_frame: str = "day"):
        user_health_form_model = self.health_form_service.get_health_form(user_id=user_id)

        if not user_health_form_model:
            raise ValueError("No user health form")
        
        try:
            user_health_form_data = HealthFormCreate.model_validate(user_health_form_model.__dict__)
        except Exception as e:
            raise ValueError(f"Data from health_form are not correctly: {e}" )
        try:
            plan_response: DailyPlanResponse = await self.spoonacular_service.generate_meal_plan(
                health_form=user_health_form_data,
                time_frame=time_frame
            )
            if plan_response is None or not hasattr(plan_response, 'meals'):
                 raise ValueError("Received invalid plan data from Spoonacular.")
            plan_data = PlanCreate(
            user_id = user_id,
            created_by = created_by_id,
            day_start = date.today(),
            total_calories = plan_response.nutrients.calories,
            total_protein = plan_response.nutrients.protein,
            total_fat = plan_response.nutrients.fat,
            total_carbohydrates = plan_response.nutrients.carbohydrates,
            )
            new_plan = create_plan(db=self.db, plan_data=plan_data)
            num_meals = user_health_form_data.number_of_meals_per_day
            meal_mapping = MEAL_MAPPING_5_MEALS if num_meals > 3 else MEAL_MAPPING_5_MEALS

            for index, meal_data in enumerate(plan_response.meals):
                if index not in meal_mapping:
                    continue

                meal_type, meal_time = meal_mapping[index]

                create_meal(
                    db=self.db,
                    plan_id = new_plan.id,
                    meal_type=meal_type,
                    time=meal_time,
                    description=f"{meal_data.title}",
                    spoonacular_recipe_id=meal_data.id
                )
            return new_plan
        except ValueError as ve: 
             logging.error(f"Spoonacular API or validation error: {ve}")
             raise HTTPException(
                 status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                 detail=f"Spoonacular service error: {ve}"
             )
        except Exception as e: 
            logging.exception("Unexpected error during plan generation:") 
            raise HTTPException(
                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                 detail=f"An unexpected error occurred during plan generation: {e}"
             )
    
    async def get_todays_plan_for_user(self, user_id: int):
        user_plan = get_plan_with_meals_by_user_id_and_date(
            db=self.db,
            user_id=user_id,
            plan_date=date.today()
        )
        health_form_model = self.health_form_service.get_health_form(user_id=user_id)
        interactions: List[DrugInteractionResponse] = []
        medication_names_from_form: List[str] = []

        if health_form_model and health_form_model.medicament_usage:
            try:
                med_string = health_form_model.medicament_usage
                if isinstance(med_string, str):
                     medication_names_from_form = [name.strip() for name in med_string.split(',') if name.strip()]
                elif isinstance(med_string, list):
                     medication_names_from_form = [str(name).strip() for name in med_string if str(name).strip()]
            except Exception as e:
                logging.error(f"Error parsing medicament_usage from HealthForm: {e}")

        if medication_names_from_form:
            tasks = [self.interaction_checker.get_rxnorm_id(name) for name in medication_names_from_form]
            rxnorm_ids_results = await asyncio.gather(*tasks)
            rxnorm_ids = [rx_id for rx_id in rxnorm_ids_results if rx_id]
            if rxnorm_ids:
                interactions = await self.interaction_checker.check_drug_interaction(rxnorm_ids)

        if not user_plan:
            return PlanResponse(
                id=0,
                user_id=user_id,
                created_by=user_id,
                day_start=date.today(),
                meals=[],
                total_calories=0,
                total_protein=0,
                total_fat=0,
                total_carbohydrates=0,
                medications=[], 
                interactions=interactions
            )
        else:
            db_medications = get_medications_by_plan_id(self.db, user_plan.id)
            return PlanResponse(
                id=user_plan.id,
                user_id=user_plan.user_id,
                created_by=user_plan.created_by,
                day_start=user_plan.day_start,
                meals=[MealResponse.model_validate(meal) for meal in user_plan.meals],
                total_calories=user_plan.total_calories,
                total_protein=user_plan.total_protein,
                total_fat=user_plan.total_fat,
                total_carbohydrates=user_plan.total_carbohydrates,
                medications=[MedicationResponse.model_validate(med) for med in db_medications],
                interactions=interactions
            )

    
    async def add_meal_manually(self, plan_id: int, meal_request: ManualMealAddRequest) -> MealResponse:
        plan = get_plan_with_meals_by_user_id_and_date(self.db, plan_id)
        if not plan:
            raise ValueError(f"Plan o ID {plan_id} nie został znaleziony.")
        
        recipe_info = await self.spoonacular_service.get_recipe_information(
            meal_request.spoonacular_recipe_id
        )
        if not recipe_info:
             raise ValueError(f"Nie znaleziono przepisu o ID {meal_request.spoonacular_recipe_id}.")

        description = f"{recipe_info.title}" 
        if recipe_info.readyInMinutes:
            description += f" (Ready in {recipe_info.readyInMinutes} min)"

        new_meal_orm = create_meal(
            db=self.db,
            plan_id=plan_id,
            meal_type=meal_request.meal_type,
            time=meal_request.time,
            description=description,
            spoonacular_recipe_id=meal_request.spoonacular_recipe_id
        )

        return MealResponse.model_validate(new_meal_orm)
    
    async def get_shopping_list_for_user(self, user_id, plan_date:date):
        user_plan = get_plan_with_meals_by_user_id_and_date(self.db, user_id, plan_date)
        if not user_plan:
            return ShoppingListResponse(total_items = 0, categories = [])
        recipe_ids = [meal.spoonacular_recipe_id for meal in user_plan.meals
                       if meal.spoonacular_recipe_id]
        if not recipe_ids:
            return ShoppingListResponse(total_items = 0, categories = [])
        tasks = [ self.spoonacular_service.get_recipe_information(recipe_id=recipie_id)
                                                                  for recipie_id in recipe_ids]
        recipie_infos = await asyncio.gather(*tasks)

        all_ingredients = []
        for recipe in recipie_infos:
            if recipe and recipe.extendedIngredients:
                all_ingredients.extend(recipe.extendedIngredients)
        categorized_items = {}
        for ingredient in all_ingredients:
            category = ingredient.aisle if ingredient.aisle else "Other"
            item_text = ingredient.original

            if category not in categorized_items:
                categorized_items[category] = []
            categorized_items[category].append(item_text)

        response_categories: List[ShoppingListCategory] = []
        for category_name, items_list in categorized_items.items():
            unique_items = sorted(list(set(items_list)))
            response_categories.append(
                ShoppingListCategory(category=category_name, items=unique_items)
            )
        response_categories.sort(key=lambda x: x.category)
        return ShoppingListResponse(
            total_items=len(all_ingredients),
            categories=response_categories
        )