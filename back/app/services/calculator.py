from app.models.common import (Gender, ActivityLevel, 
                               CalorieGoal, 
                               ACTIVITY_LEVEL_MULTIPLIERS, 
                               CALORIE_GOAL_ADJUSTMENTS)
from app.schemas.health_form import HealthFormCreate, CalorieTargetResponse
class CalculatorService:
    @staticmethod
    def calculate_bmr(gender: Gender, height: int, weight: int, age: int):
        if gender == Gender.male:
            bmr = (10 * weight) + (6.25 * height )-(5*age) + 5
        elif gender == Gender.female:
            bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
        return bmr

    @staticmethod
    def calculate_target_calories(
            bmr: float,
            userActivityLevel: ActivityLevel,
            userGoal: CalorieGoal
            ):
        pal = ACTIVITY_LEVEL_MULTIPLIERS.get(userActivityLevel, 0)
        calories_adjustment = CALORIE_GOAL_ADJUSTMENTS.get(userGoal, 0)

        tdee = bmr * pal 
        return round(tdee + calories_adjustment,0)

    def get_result_for_user(self, health_form: HealthFormCreate):
        if not all([health_form.gender, health_form.age,
                    health_form.activity_level, health_form.weight, health_form.height]):
            bmr = 1500
            raise ValueError("BMR is rounded")
        
        bmr = self.calculate_bmr(
            gender=health_form.gender,
            weight=health_form.weight,
            height=health_form.height,
            age=health_form.age
        )
        target_calories = self.calculate_target_calories(
            bmr=bmr,
            userActivityLevel=health_form.activity_level,
            userGoal=health_form.calorie_goal
        )
        return CalorieTargetResponse(
            bmr=bmr,
            target_calories=target_calories
        )
