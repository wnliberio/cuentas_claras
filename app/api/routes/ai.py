from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.expense import Expense
from app.api.routes.auth import get_current_user
from app.services.ai_service import AIService
from pydantic import BaseModel
from typing import Dict, Any
import datetime

router = APIRouter()

class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    response: str

class CategorizeRequest(BaseModel):
    description: str
    amount: float

@router.post("/categorize")
async def categorize_expense(
    request: CategorizeRequest,
    current_user: User = Depends(get_current_user)
):
    ai_service = AIService()
    result = await ai_service.categorize_expense(request.description, request.amount)
    return result

@router.get("/insights")
async def get_insights(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Obtener gastos del usuario
    expenses = db.query(Expense).filter(Expense.user_id == current_user.id).all()
    
    # Convertir a formato para IA
    expenses_data = [
        {
            "amount": exp.amount,
            "category": exp.category,
            "description": exp.description,
            "date": exp.date.isoformat()
        }
        for exp in expenses
    ]
    
    ai_service = AIService()
    insights = await ai_service.get_financial_insights(expenses_data)
    
    return insights

@router.post("/chat", response_model=ChatResponse)
async def financial_chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Contexto del usuario
    current_month = datetime.datetime.now().month
    expenses_this_month = db.query(Expense).filter(
        Expense.user_id == current_user.id,
        Expense.date >= datetime.datetime.now().replace(day=1)
    ).all()
    
    monthly_total = sum(exp.amount for exp in expenses_this_month)
    expense_count = len(expenses_this_month)
    
    # Categoría más frecuente
    if expenses_this_month:
        categories = [exp.category for exp in expenses_this_month if exp.category]
        top_category = max(set(categories), key=categories.count) if categories else "N/A"
    else:
        top_category = "N/A"
    
    user_context = {
        "monthly_total": monthly_total,
        "top_category": top_category,
        "expense_count": expense_count
    }
    
    ai_service = AIService()
    response = await ai_service.financial_chat(request.question, user_context)
    
    return ChatResponse(response=response)

@router.get("/predictions")
async def get_predictions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Predicciones básicas de gastos"""
    # Obtener gastos de los últimos 3 meses
    three_months_ago = datetime.datetime.now() - datetime.timedelta(days=90)
    recent_expenses = db.query(Expense).filter(
        Expense.user_id == current_user.id,
        Expense.date >= three_months_ago
    ).all()
    
    if not recent_expenses:
        return {"message": "No hay suficientes datos para predicciones"}
    
    # Análisis básico
    total_amount = sum(exp.amount for exp in recent_expenses)
    avg_monthly = total_amount / 3
    
    # Predicción simple: promedio + 10% de variación
    predicted_next_month = avg_monthly * 1.1
    
    # Breakdown por categoría
    category_totals = {}
    for exp in recent_expenses:
        cat = exp.category or "Otros"
        category_totals[cat] = category_totals.get(cat, 0) + exp.amount
    
    category_predictions = {}
    for cat, total in category_totals.items():
        category_predictions[cat] = (total / 3) * 1.1  # Promedio mensual + 10%
    
    return {
        "predicted_total": round(predicted_next_month, 2),
        "category_predictions": {k: round(v, 2) for k, v in category_predictions.items()},
        "confidence": 0.75,
        "based_on_months": 3
    }