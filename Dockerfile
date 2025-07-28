FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Variables de entorno
ENV PYTHONPATH=/app
ENV PORT=8000

# Exponer puerto
EXPOSE $PORT

# Comando de inicio
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT