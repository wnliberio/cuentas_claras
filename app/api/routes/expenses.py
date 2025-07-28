from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from app.core.database import get_db
from app.models.user import User
from app.models.expense import Expense
from app.schemas.expense import ExpenseCreate, ExpenseResponse, ExpenseStats
from app.api.routes.auth import get_current_user
from app.services.ai_service import AIService
import datetime

router = APIRouter()

@router.post("/", response_model=ExpenseResponse)
async def create_expense(
    expense: ExpenseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Usar IA para categorizar si no viene categoría
    if not expense.category:
        ai_service = AIService()
        ai_result = await ai_service.categorize_expense(expense.description, expense.amount)
        expense.category = ai_result["category"]
        ai_categorized = True
    else:
        ai_categorized = False
    
    # Crear gasto
    db_expense = Expense(
        user_id=current_user.id,
        amount=expense.amount,
        description=expense.description,
        category=expense.category,
        ai_categorized=ai_categorized
    )
    
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    
    return db_expense

@router.get("/", response_model=List[ExpenseResponse])
async def get_expenses(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    expenses = db.query(Expense).filter(
        Expense.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    return expenses

@router.get("/stats", response_model=ExpenseStats)
async def get_expense_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Gastos del mes actual
    current_month = datetime.datetime.now().month
    current_year = datetime.datetime.now().year
    
    monthly_expenses = db.query(Expense).filter(
        Expense.user_id == current_user.id,
        extract('month', Expense.date) == current_month,
        extract('year', Expense.date) == current_year
    ).all()
    
    # Cálculos
    total_expenses = sum(exp.amount for exp in monthly_expenses)
    
    # Breakdown por categoría
    category_breakdown = {}
    for expense in monthly_expenses:
        category = expense.category or "Sin categoría"
        category_breakdown[category] = category_breakdown.get(category, 0) + expense.amount
    
    # Promedio mensual (últimos 3 meses)
    three_months_ago = datetime.datetime.now() - datetime.timedelta(days=90)
    all_expenses = db.query(Expense).filter(
        Expense.user_id == current_user.id,
        Expense.date >= three_months_ago
    ).all()
    
    monthly_average = sum(exp.amount for exp in all_expenses) / 3 if all_expenses else 0
    
    return ExpenseStats(
        total_expenses=total_expenses,
        category_breakdown=category_breakdown,
        monthly_average=monthly_average
    )

@router.delete("/{expense_id}")
async def delete_expense(
    expense_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    expense = db.query(Expense).filter(
        Expense.id == expense_id,
        Expense.user_id == current_user.id
    ).first()
    
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    db.delete(expense)
    db.commit()
    
    return {"message": "Expense deleted successfully"}