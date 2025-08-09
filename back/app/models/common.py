import enum 
from sqlalchemy import Enum as ASEnum

class MealType(str, enum.Enum):
    breakfast = "breakfast"
    second_breakfast = "second_breakfast"
    lunch = "lunch"
    snack = "snack"
    dinner = "dinner"
    supper = "supper"

class WithMealRelation(str, enum.Enum):
    before = "before"
    during = "during"
    after = "after"
    empty_stomach = "empty_stomach"
