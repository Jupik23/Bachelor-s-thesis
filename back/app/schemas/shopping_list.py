from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class ShoppingListCategory(BaseModel):
    category: str
    items: List[str]

class ShoppingListResponse(BaseModel):
    id: Optional[int] = None
    from_date: date
    to_date: date
    total_items: int
    categories: List[ShoppingListCategory]
    class Config:
        from_attributes = True
class ShoppingListGenerateRequest(BaseModel):
    days: int = 1 
    include_dependents: bool = False 
    start_date: Optional[date] = None 