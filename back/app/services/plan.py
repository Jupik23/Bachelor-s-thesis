from sqlalchemy.orm import Session
from datetime import date, time
import logging
from typing import List, Optional
import os
import asyncio
from fastapi import HTTPException, status

from app.services.spoonacular import Spoonacular
from app.services.health_form import HealthFormService
from app.schemas.health_form import HealthFormCreate
from app.schemas.plan import PlanCreate, PlanResponse, ManualMealAddRequest, MealResponse
from app.schemas.spoonacular import DailyPlanResponse, ComplexSearchResponse
from app.models.common import MealType, WithMealRelation
from app.services.medication_service import DrugInteractionService, DrugInteractionResponse, MedicationResponse
from app.schemas.shopping_list import ShoppingListResponse, ShoppingListCategory
from app.crud.medication import get_medications_by_plan_id, create_medication
from app.crud.plans import create_plan, get_plan_with_meals_by_user_id_and_date
from app.crud.meals import create_meal, get_meal_by_id
from app.schemas.medication import MedicationCreate


MEAL_MAPPING_1 = {
    0: (MealType.lunch, time(13, 0)),
}

MEAL_MAPPING_2 = {
    0: (MealType.breakfast, time(8, 0)),
    1: (MealType.dinner, time(18, 0)),
}

MEAL_MAPPING_3 = {
    0: (MealType.breakfast, time(8, 0)),
    1: (MealType.lunch, time(13, 0)),
    2: (MealType.dinner, time(18, 0)),
}

MEAL_MAPPING_4 = {
    0: (MealType.breakfast, time(7, 30)),
    1: (MealType.second_breakfast, time(10, 30)),
    2: (MealType.lunch, time(13, 30)),
    3: (MealType.dinner, time(19, 0)),
}

MEAL_MAPPING_5 = {
    0: (MealType.breakfast, time(7, 30)),
    1: (MealType.second_breakfast, time(10, 30)),
    2: (MealType.lunch, time(13, 30)),
    3: (MealType.snack, time(16, 30)),
    4: (MealType.dinner, time(19, 30)), 
}

MEAL_MAPPING_6 = {
    0: (MealType.breakfast, time(7, 0)),
    1: (MealType.second_breakfast, time(10, 0)),
    2: (MealType.lunch, time(13, 0)),
    3: (MealType.snack, time(16, 0)),
    4: (MealType.dinner, time(19, 0)),
    5: (MealType.supper, time(21, 30)),
}

MEAL_TEMPLATES = {
    1: [(0, "lunch", "main course")],
    2: [(0, "breakfast", "breakfast"), (1, "dinner", "main course")],
    3: [(0, "breakfast", "breakfast"), (1, "lunch", "main course"), (2, "dinner", "main course")],
    4: [(0, "breakfast", "breakfast"), (1, "second_breakfast", "snack"), (2, "lunch", "main course"), (3, "dinner", "main course")],
    5: [(0, "breakfast", "breakfast"), (1, "second_breakfast", "snack"), (2, "lunch", "main course"), (3, "snack", "snack"), (4, "dinner", "main course")],
    6: [(0, "breakfast", "breakfast"), (1, "second_breakfast", "snack"), (2, "lunch", "main course"), (3, "snack", "snack"), (4, "dinner", "main course"), (5, "supper", "snack")]
}

def get_meal_mapping(num_meals: int):
    mappings = {
        1: MEAL_MAPPING_1,
        2: MEAL_MAPPING_2,
        3: MEAL_MAPPING_3,
        4: MEAL_MAPPING_4,
        5: MEAL_MAPPING_5,
        6: MEAL_MAPPING_6,
    }
    return mappings.get(num_meals, MEAL_MAPPING_3)


class PlanCreationService:
    def __init__(self, db: Session):
        self.db = db
        self.spoonacular_service = Spoonacular()
        fda_key = os.getenv("OPEN_FDA_API_KEY")
        self.interaction_checker = DrugInteractionService(db=self.db, fda_api_key=fda_key)
        self.health_form_service = HealthFormService(db)

    async def generate_and_save_plan(self, created_by_id, user_id, time_frame: str = "day", plan_date: Optional[date] = None):
        if plan_date is None:
            plan_date = date.today()

        user_health_form_model = self.health_form_service.get_health_form(user_id=user_id)

        if not user_health_form_model:
            raise ValueError("No user health form")
        
        try:
            user_health_form_data = HealthFormCreate.model_validate(user_health_form_model.__dict__)
        except Exception as e:
            raise ValueError(f"Data from health_form are not correctly: {e}")
        
        num_meals = max(1, min(6, user_health_form_data.number_of_meals_per_day))
        template = MEAL_TEMPLATES.get(num_meals, MEAL_TEMPLATES[3])
        spoonacular_query_types = [item[2] for item in template]

        try:
            plan_response_spoonacular: DailyPlanResponse = await self.spoonacular_service.generate_structured_plan(
                health_form=user_health_form_data,
                meal_types=spoonacular_query_types
            )

            if plan_response_spoonacular is None or not plan_response_spoonacular.meals:
                 raise ValueError("Spoonacular returned no meals matching the criteria.")

            plan_data = PlanCreate(
                user_id=user_id,
                created_by=created_by_id,
                day_start=plan_date, 
                total_calories=plan_response_spoonacular.nutrients.calories,
                total_protein=plan_response_spoonacular.nutrients.protein,
                total_fat=plan_response_spoonacular.nutrients.fat,
                total_carbohydrates=plan_response_spoonacular.nutrients.carbohydrates,
            )
            new_plan = create_plan(db=self.db, plan_data=plan_data)
            num_meals = user_health_form_data.number_of_meals_per_day
            meal_mapping = get_meal_mapping(num_meals)
            
            for index, meal_data in enumerate(plan_response_spoonacular.meals):
                if index not in meal_mapping:
                    logging.warning(f"Meal index {index} not in mapping for {num_meals} meals")
                    continue
                
                meal_type, meal_time = meal_mapping[index]
                
                create_meal(
                    db=self.db,
                    plan_id=new_plan.id,
                    meal_type=meal_type,
                    time=meal_time,
                    description=f"{meal_data.title}",
                    spoonacular_recipe_id=meal_data.id
                )
            
            self.db.commit()
            self.db.refresh(new_plan)            
            
            interactions: List[DrugInteractionResponse] = []
            db_medications = []
            
            try:
                medication_names_from_form: List[str] = []
                
                if user_health_form_model.medicament_usage:
                    try:
                        med_string = user_health_form_model.medicament_usage
                        if isinstance(med_string, str):
                            medication_names_from_form = [name.strip() for name in med_string.split(',') if name.strip()]
                        elif isinstance(med_string, list):
                            medication_names_from_form = [str(name).strip() for name in med_string if str(name).strip()]
                    except Exception as e:
                        logging.error(f"Error parsing medicament_usage from HealthForm: {e}")
                
                if medication_names_from_form:
                    for med_name in medication_names_from_form:
                        try:
                            detected_relation = await self.interaction_checker.get_medication_timing(med_name=med_name)
                        except Exception as e:
                            logging.error(f"Failed to detect meal-med relation: {med_name} : {e}")
                            detected_relation = WithMealRelation.unknown
                        
                        relation_map = {
                            WithMealRelation.unknown: "no data",
                            WithMealRelation.empty_stomach: "on an empty stomach",
                            WithMealRelation.before: "before meal",
                            WithMealRelation.during: "during meal",
                            WithMealRelation.after: "after meal",
                        }
                        default_desc_text = relation_map.get(detected_relation, "as directed")
                        med_data = MedicationCreate(
                            name=med_name,
                            time=time(8, 0),
                            with_meal_relation=detected_relation,
                            description=f"Take: {default_desc_text}. (Auto-detected from FDA label)"
                        )
                        
                        create_medication(
                            db=self.db,
                            plan_id=new_plan.id, 
                            medication_data=med_data,
                        )
                    
                    self.db.commit()

                    try:
                        interactions = await self.interaction_checker.check_drug_interaction(medication_names_from_form)
                    except Exception as e:
                        logging.error(f"Error checking drug interactions: {e}")
                        interactions = []
                
                db_medications = get_medications_by_plan_id(self.db, new_plan.id)

            except Exception as e:
                logging.error(f"Error processing medications, rolling back med section: {e}")
                self.db.rollback()
                interactions = []
                db_medications = []

            final_plan_response = PlanResponse(
                id=new_plan.id,
                user_id=new_plan.user_id,
                created_by=new_plan.created_by,
                day_start=new_plan.day_start,
                meals=[MealResponse.model_validate(meal) for meal in new_plan.meals],
                total_calories=new_plan.total_calories,
                total_protein=new_plan.total_protein,
                total_fat=new_plan.total_fat,
                total_carbohydrates=new_plan.total_carbohydrates,
                medications=[MedicationResponse.model_validate(med) for med in db_medications],
                interactions=interactions
            )
            
            return final_plan_response

        except ValueError as ve: 
            self.db.rollback()
            logging.error(f"Spoonacular API or validation error: {ve}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Spoonacular service error: {ve}"
            )
        except Exception as e: 
            self.db.rollback()
            logging.exception("Unexpected error during plan generation:") 
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An unexpected error occurred during plan generation: {e}"
            )
    
    async def get_plan_by_date(self, user_id: int, plan_date: date):
        try:
            user_plan = get_plan_with_meals_by_user_id_and_date(
                db=self.db,
                user_id=user_id,
                plan_date=plan_date
            )
            
            if not user_plan:
                return PlanResponse(
                    id=0,
                    user_id=user_id,
                    created_by=user_id,
                    day_start=plan_date,
                    meals=[],
                    total_calories=0,
                    total_protein=0,
                    total_fat=0,
                    total_carbohydrates=0,
                    medications=[], 
                    interactions=[]
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
                try:
                    interactions = await self.interaction_checker.check_drug_interaction(medication_names_from_form)
                except Exception as e:
                    logging.error(f"Error checking drug interactions: {e}")
                    interactions = []
            
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
        except Exception as e:
            logging.error(f"Error fetching plan: {e}")
            return PlanResponse(
                id=0,
                user_id=user_id,
                created_by=user_id,
                day_start=plan_date,
                meals=[],
                total_calories=0,
                total_protein=0, total_fat=0, total_carbohydrates=0,
                medications=[], interactions=[]
            )

    async def add_meal_manually(self, plan_id: int, meal_request: ManualMealAddRequest) -> MealResponse:
        plan = get_plan_with_meals_by_user_id_and_date(self.db, plan_id) 
        recipe_info = await self.spoonacular_service.get_recipe_information(
            meal_request.spoonacular_recipe_id
        )
        if not recipe_info:
            raise ValueError(f"Recipe ID {meal_request.spoonacular_recipe_id} not found.")

        description = f"{recipe_info.title}" 

        new_meal_orm = create_meal(
            db=self.db,
            plan_id=plan_id,
            meal_type=meal_request.meal_type,
            time=meal_request.time,
            description=description,
            spoonacular_recipe_id=meal_request.spoonacular_recipe_id
        )

        return MealResponse.model_validate(new_meal_orm)

    async def get_shopping_list_for_user(self, user_id, plan_date: date):
        user_plan = get_plan_with_meals_by_user_id_and_date(self.db, user_id, plan_date)
        if not user_plan:
            return ShoppingListResponse(total_items=0, categories=[])
        
        recipe_ids = [meal.spoonacular_recipe_id for meal in user_plan.meals
                        if meal.spoonacular_recipe_id]
        if not recipe_ids:
            return ShoppingListResponse(total_items=0, categories=[])
        
        tasks = [self.spoonacular_service.get_recipe_information(recipe_id=recipe_id)
                 for recipe_id in recipe_ids]
        recipe_infos = await asyncio.gather(*tasks)

        all_ingredients = []
        for recipe in recipe_infos:
            if recipe and recipe.extendedIngredients:
                all_ingredients.extend(recipe.extendedIngredients)
        
        categorized_items = {}
        for ingredient in all_ingredients:
            category = ingredient.aisle if ingredient.aisle else "Other"
            item_text = ingredient.original if ingredient.original else ingredient.name

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

    async def search_alternative_recipe(self, user_id: int, query: str) -> ComplexSearchResponse:
        health_form = self.health_form_service.get_health_form(user_id=user_id)
        diets = []
        intolerances = []
        
        if health_form:
            if health_form.diet_preferences:
                if isinstance(health_form.diet_preferences, str):
                    diets = health_form.diet_preferences.split(',')
                else:
                    diets = health_form.diet_preferences

            if health_form.intolerances:
                if isinstance(health_form.intolerances, str):
                    intolerances = health_form.intolerances.split(',')
                else:
                    intolerances = health_form.intolerances

        return await self.spoonacular_service.search_recipies(
            query=query,
            diet=diets,
            intolerances=intolerances,
            number=10
        )
    
    async def replace_meal(self, meal_id: int, new_meal_id: int):
        old_meal = get_meal_by_id(db=self.db, meal_id= meal_id)
        if not old_meal:
            raise ValueError("Meal not found")
        plan_id = old_meal.plan_id
        meal_time = old_meal.time
        meal_type = old_meal.meal_type
        recipe_info = await self.spoonacular_service.get_recipe_information(new_meal_id)
        if not recipe_info:
            raise ValueError("New recipe not found")
        description = f"{recipe_info.title}"
        self.db.delete(old_meal)
        self.db.commit()
        new_meal = create_meal(
            db=self.db,
            plan_id=plan_id,
            meal_type=meal_type,
            time=meal_time,
            description=description,
            spoonacular_recipe_id=new_meal_id
        )
        return MealResponse.model_validate(new_meal)