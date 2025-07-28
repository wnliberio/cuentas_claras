from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import auth, expenses, ai
from app.core.database import engine, Base
import uvicorn

# Crear tablas
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Financia AI",
    description="App financiera personal con IA",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://tu-frontend.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rutas
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(expenses.router, prefix="/api/expenses", tags=["expenses"])
app.include_router(ai.router, prefix="/api/ai", tags=["ai"])

@app.get("/")
async def root():
    return {"message": "Financia AI Backend", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)