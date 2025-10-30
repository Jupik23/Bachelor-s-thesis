from pydantic import BaseModel
from typing import List

class ShoppingListItem(BaseModel):
    id: int
    original: str
    aisle: str

class ShoppingListCategory(BaseModel):
    category: str
    items: List[str]

class ShoppingListResponse(BaseModel):
    total_items: int
    categories: List[ShoppingListCategory]