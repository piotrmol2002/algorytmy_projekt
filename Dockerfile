# ====================================================================
# DOCKERFILE dla Firefly Queueing Optimizer
# ====================================================================

# Bazowy obraz Python
FROM python:3.11-slim

# Ustaw zmienne środowiskowe
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Katalog roboczy
WORKDIR /app

# Instaluj zależności systemowe (dla matplotlib)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Kopiuj requirements.txt
COPY requirements.txt .

# Instaluj zależności Python
RUN pip install --no-cache-dir -r requirements.txt

# Kopiuj cały projekt
COPY . .

# Eksponuj port
EXPOSE 5000

# Zdrowie kontenera
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000')" || exit 1

# Uruchom aplikację
CMD ["python", "app.py"]
