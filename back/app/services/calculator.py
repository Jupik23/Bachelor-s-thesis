from app.models.common import (Gender, ActivityLevel, 
                               CalorieGoal, 
                               ACTIVITY_LEVEL_MULTIPLIERS, 
                               CALORIE_GOAL_ADJUSTMENTS)

def calculate_bmr(gender: Gender, height: float, weight: float, age: int):
    if gender == Gender.male:
        bmr = (10 * weight) + (6,25 * height )-(5*age) + 5
    elif gender == Gender.female:
        bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
    return bmr

def calculate_target_calories(
        bmr: float,
        userActivityLevel: ActivityLevel,
        userGoal = CalorieGoal
        ):
    pal = ACTIVITY_LEVEL_MULTIPLIERS.get(userActivityLevel, 0)
    calories_adjustment = CALORIE_GOAL_ADJUSTMENTS.get(userGoal, 0)

    tdee = bmr * pal 
    return tdee + calories_adjustment