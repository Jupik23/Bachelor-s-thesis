from app.services.spoonacular import suggest_recipes
from sqlalchemy.orm import Session
from app.crud.spoonacular import get_healthform_by_user_id

async def suggest_meal_for_user(db: Session, user_id: int, number_of_meals: int = 6):
    form = get_healthform_by_user_id(db, user_id)

    if not form: return []

    diets = (form.diet_preferences or {}).get("diets", [])
    cuisine_like = (form.diet_preferences or {}).get("cuisine_like", [])
    intolerances = form.intolerances or []
    allergies = form.allergies or []
    exclude = list(allergies)

    return await suggest_recipes(diets, intolerances, exclude, number=number_of_meals, cuisine_like=cuisine_like)