from sqlalchemy.orm import Session
from datetime import date, time
from app.services.spoonacular import Spoonacular
from app.services.health_form import HealthFormService
from app.schemas.health_form import HealthFormCreate
from app.schemas.plan import PlanCreate
from app.schemas.spoonacular import DailyPlanResponse, WeeklyPlanResponse
from app.models.common import MealType
from app.crud.plans import create_plan
from app.crud.meals import create_meal

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
        except Exception as e:
            raise Exception(f"Can't generate plan: {e}")
        
        plan_data = PlanCreate(
            user_id = user_id,
            created_by = created_by_id,
            day_start = date.today()
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