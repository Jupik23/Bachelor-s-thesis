import os, httpx
from typing import List, Optional
from app.schemas.spoonacular import Recipe
from app.schemas.health_form import DietPreferences

class Spoonacular():
    def __init__(self):
        self.base = "https://api.spoonacular.com"
        self.api_key = os.getenv("SPOONACULAR_API_KEY")
        self.client = httpx.AsyncClient()

    #w przyszlosci dac tutaj liczbe posilkow dziennie * 7 (*2? - zeby
    #zamienniki byly
    async def search_recipies(self, preferences: DietPreferences, number = 15):
        params = [
            "apiKey": self.api_key,
            "number": number,
            "includeIngredients": True,
            "instructionsRequired": True,
            "addRecipeInformation": True,
        ]
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base}/recipies/complexSearch"
            )
