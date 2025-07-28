import google.generativeai as genai
import json
import pandas as pd
from typing import Dict, List
from app.core.config import settings

# Configurar Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)

class AIService:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-pro')
    
    async def categorize_expense(self, description: str, amount: float) -> Dict:
        """Categoriza un gasto automáticamente"""
        prompt = f"""
        Categoriza este gasto financiero:
        
        Descripción: {description}
        Monto: ${amount}
        
        Responde SOLO con JSON válido:
        {{
            "category": "categoria_principal",
            "subcategory": "subcategoria",
            "confidence": 0.95,
            "suggested_budget": 500.00
        }}
        
        Categorías válidas: Alimentación, Transporte, Vivienda, Entretenimiento, Salud, Educación, Ropa, Tecnología, Servicios, Otros
        """
        
        try:
            response = self.model.generate_content(prompt)
            result = json.loads(response.text)
            return result
        except Exception as e:
            # Fallback si falla la IA
            return {
                "category": "Otros",
                "subcategory": "Sin categorizar",
                "confidence": 0.5,
                "suggested_budget": amount * 10
            }
    
    async def get_financial_insights(self, expenses_data: List[Dict]) -> Dict:
        """Genera insights financieros"""
        if not expenses_data:
            return {"message": "No hay datos suficientes para generar insights"}
        
        # Convertir a DataFrame para análisis
        df = pd.DataFrame(expenses_data)
        total_expenses = df['amount'].sum()
        avg_expense = df['amount'].mean()
        top_category = df['category'].mode().iloc[0] if len(df) > 0 else "N/A"
        
        prompt = f"""
        Analiza estos datos financieros y da recomendaciones:
        
        - Total gastado: ${total_expenses:.2f}
        - Promedio por gasto: ${avg_expense:.2f}
        - Categoría principal: {top_category}
        - Número de transacciones: {len(df)}
        
        Responde en JSON:
        {{
            "summary": "resumen_breve",
            "recommendations": ["recomendación1", "recomendación2"],
            "alerts": ["alerta1"],
            "savings_potential": 150.00
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            return json.loads(response.text)
        except Exception as e:
            return {
                "summary": f"Has gastado ${total_expenses:.2f} en {len(df)} transacciones",
                "recommendations": ["Revisa tus gastos en " + top_category],
                "alerts": ["Sin alertas por ahora"],
                "savings_potential": total_expenses * 0.1
            }
    
    async def financial_chat(self, question: str, user_context: Dict) -> str:
        """Chat financiero conversacional"""
        prompt = f"""
        Eres un asistente financiero personal. Responde de manera conversacional y útil.
        
        Contexto del usuario:
        - Total gastado este mes: ${user_context.get('monthly_total', 0):.2f}
        - Categoría principal: {user_context.get('top_category', 'N/A')}
        - Número de gastos: {user_context.get('expense_count', 0)}
        
        Pregunta del usuario: {question}
        
        Responde de manera natural y específica, usando los datos del contexto cuando sea relevante.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return "Lo siento, no puedo procesar tu pregunta en este momento. ¿Podrías intentar de nuevo?"