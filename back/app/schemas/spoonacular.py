from pydantic import BaseModel
from typing import Optional

class Recipe(BaseModel):
    id: int
    title: str
    summary: Optional[str] = None
    image: Optional[str] = None
    sourceUrl: Optional[str] = None
    readyInMinutes: Optional[int] = None
    servings: Optional[int] = None