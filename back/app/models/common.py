from enum import Enum 
from typing import Literal
class Gender(str, Enum):
    male = "male"
    female = "female"

class ActivityLevel(str, Enum):
    sedentary = "sedentary"
    light = "light"
    moderate = "moderate"
    active = "active"
    very_active = "very_active"

class CalorieGoal(str, Enum):
    maintain = "maintain"
    mild_loss = "mild_loss"
    loss = "loss"
    extreme_loss = "extreme_loss"
    mild_gain = "mild_gain"
    gain = "gain"

class MealType(str, Enum):
    breakfast = "breakfast"
    second_breakfast = "second_breakfast"
    lunch = "lunch"
    snack = "snack"
    dinner = "dinner"
    supper = "supper"

class WithMealRelation(str, Enum):
    unknown = "no_data"
    before = "before"
    during = "during"
    after = "after"
    empty_stomach = "empty_stomach"

ACTIVITY_LEVEL_MULTIPLIERS = {
    ActivityLevel.sedentary: 1.2, 
    ActivityLevel.light: 1.375,   
    ActivityLevel.moderate: 1.55, 
    ActivityLevel.active: 1.725,  
    ActivityLevel.very_active: 1.9 
}

CALORIE_GOAL_ADJUSTMENTS = {
    CalorieGoal.maintain: 0,   
    CalorieGoal.mild_loss: -300,
    CalorieGoal.loss: -500,     
    CalorieGoal.extreme_loss: -800, 
    CalorieGoal.mild_gain: 300,
    CalorieGoal.gain: 500       
}