# Python leve
FROM python:3.11-slim

# Evita bytecode e buffers
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8080

# Dependências nativas (psycopg2, cffi, cryptography, pyzmq etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    unixodbc \
    unixodbc-dev \
    libffi-dev \
    libssl-dev \
    libzmq3-dev \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instalar deps antes (melhor cache)
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# Código da aplicação
# Código da aplicação
COPY ./src /app/src
COPY ./main.py /app/main.py

EXPOSE 8080
# Use shell form p/ expandir $PORT e $WEB_CONCURRENCY
CMD exec gunicorn main:app \
  -k uvicorn.workers.UvicornWorker \
  -b 0.0.0.0:${PORT:-8080} \
  --timeout 120 \
  --workers ${WEB_CONCURRENCY:-2}
