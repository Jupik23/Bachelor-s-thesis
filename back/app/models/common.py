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