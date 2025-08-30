import os, httpx
from typing import List, Optional
from app.schemas.spoonacular import Recipe

SPOONACULAR_API_KEY = os.getenv("SPOONACULAR_API_KEY")
BASE = "https://api.spoonacular.com"

async def suggest_recipes(diets: List[str], intolerances: List[str], exclude: List[str],
                          number: int = 6, cuisine_like: Optional[List[str]] = None) -> List[Recipe]:
    if not SPOONACULAR_API_KEY:
        return []
    params = {
        "apiKey": SPOONACULAR_API_KEY,
        "addRecipeInformation": "true",
        "instructionsRequired": "true",
        "number": str(number),
    }
    if diets: params["diet"] = diets[0]
    if intolerances: params["intolerances"] = ",".join(intolerances)
    if exclude: params["excludeIngredients"] = ",".join(exclude)
    if cuisine_like: params["cuisine"] = ",".join(cuisine_like)

    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(f"{BASE}/recipes/complexSearch", params=params)
        r.raise_for_status()
        data = r.json().get("results", [])
        return [Recipe(**{
            "id": d.get("id"), "title": d.get("title"), "summary": d.get("summary"),
            "image": d.get("image"), "sourceUrl": d.get("sourceUrl"),
            "readyInMinutes": d.get("readyInMinutes"), "servings": d.get("servings")
        }) for d in data]