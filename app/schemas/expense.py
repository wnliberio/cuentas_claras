from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ExpenseBase(BaseModel):
    amount: float
    description: str
    category: Optional[str] = None

class ExpenseCreate(ExpenseBase):
    pass

class ExpenseResponse(ExpenseBase):
    id: int
    user_id: int
    ai_categorized: bool
    date: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True

class ExpenseStats(BaseModel):
    total_expenses: float
    category_breakdown: dict
    monthly_average: float