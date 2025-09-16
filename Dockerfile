FROM python:3.10.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Копирование requirements и установка Python зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование файлов приложения
COPY main.py .
COPY roboflow_model.pt .

# Создание директории для статических файлов
RUN mkdir -p static

# Открытие порта
EXPOSE 8000

# Запуск приложения
CMD ["python", "main.py"]
