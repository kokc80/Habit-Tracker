
FROM python:3.12-slim

# Системные зависимости для PostgreSQL и сборки некоторых пакетов
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Сначала копируем requirements, чтобы кэш слоёв работал
COPY requirements.txt .

# Обновляем pip и ставим зависимости
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копируем весь код
COPY . .

EXPOSE 8000