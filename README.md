# T-Bank Logo Detector

REST API сервис для обнаружения логотипа Т-Банка на изображениях и видео с использованием YOLO.

## Архитектура

- **FastAPI** - веб-фреймворк для API
- **Ultralytics YOLO** - модель детекции объектов
- **OpenCV** - обработка изображений и видео
- **Pydantic** - валидация данных

## Структура проекта

```
├── app/
│   ├── __init__.py
│   ├── models.py          # Pydantic модели
│   ├── detector.py        # Логика детекции
│   └── api.py            # FastAPI эндпоинты
├── static/
│   ├── index.html        # Фронтенд для изображений
│   └── video.html        # Фронтенд для видео
├── main.py               # Точка входа
├── requirements.txt      # Зависимости
├── Dockerfile           # Docker конфигурация
└── README.md
```

## API Эндпоинты

### `/detect` (POST)
Основной эндпоинт согласно контракту для детекции логотипов на изображениях.

**Параметры:**
- `file`: Загружаемое изображение (JPEG, PNG, BMP, WEBP)

**Ответ:**
```json
{
  "detections": [
    {
      "bbox": {
        "x_min": 100,
        "y_min": 50,
        "x_max": 200,
        "y_max": 150
      }
    }
  ]
}
```

### `/detect-image` (POST)
Эндпоинт для фронтенда с визуализацией результатов.

**Ответ:**
```json
{
  "image_data": "base64_encoded_image",
  "detections": [...]
}
```

### `/detect-video` (POST)
Эндпоинт для обработки видео с визуализацией.

**Ответ:**
```json
{
  "video_data": "base64_encoded_video",
  "total_detections": 15
}
```

## Установка и запуск

### Локальная разработка

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Поместите модель `roboflow_yolov11s.pt` в папку `models/`

3. Запустите сервис:
```bash
python main.py
```

Сервис будет доступен по адресу: http://localhost:8000

### Docker

1. Соберите образ:
```bash
docker build -t tbank-detector .
```

2. Запустите контейнер с монтированием папки models:
```bash
docker run -d \
  --name tbank-detector \
  -p 8000:8000 \
  -v $(pwd)/models:/app/models:ro \
  -v $(pwd)/static:/app/static \
  --restart unless-stopped \
  tbank-detector
```

3. Проверьте статус контейнера:
```bash
docker ps
docker logs tbank-detector
```

### Управление контейнером

#### Запуск/остановка:
```bash
# Запустить контейнер
docker start tbank-detector

# Остановить контейнер
docker stop tbank-detector

# Перезапустить контейнер
docker restart tbank-detector
```

#### Вход в контейнер:
```bash
# Войти в контейнер для отладки
docker exec -it tbank-detector /bin/bash

# Войти в контейнер с root правами
docker exec -it --user root tbank-detector /bin/bash
```

#### Полезные команды в контейнере:
```bash
# Посмотреть логи приложения
tail -f app.log

# Проверить статус процессов
ps aux | grep python

# Посмотреть использование диска
df -h

# Проверить файлы в папке models
ls -la models/

# Перезапустить приложение внутри контейнера
pkill -f "python main.py" && python main.py &
```

#### Обновление модели:
```bash
# Остановить контейнер
docker stop tbank-detector

# Заменить файл модели в папке models/
cp new_model.pt models/roboflow_yolov11s.pt

# Запустить контейнер
docker start tbank-detector
```

#### Мониторинг:
```bash
# Посмотреть логи в реальном времени
docker logs -f tbank-detector

# Посмотреть использование ресурсов
docker stats tbank-detector

# Проверить здоровье контейнера
docker inspect tbank-detector | grep -A 5 "Health"
```

### Docker Compose (рекомендуется)

1. Создайте `docker-compose.yml`:
```yaml
version: '3.8'

services:
  tbank-detector:
    build: .
    container_name: tbank-detector
    ports:
      - "8000:8000"
    volumes:
      - ./models:/app/models:ro
      - ./static:/app/static
    restart: unless-stopped
    environment:
      - PYTHONUNBUFFERED=1
```

2. Запустите:
```bash
docker-compose up -d
```

3. Остановите:
```bash
docker-compose down
```

### Docker Hub

Образ доступен на Docker Hub:
```bash
docker pull your-username/tbank-detector:latest
docker run -d \
  --name tbank-detector \
  -p 8000:8000 \
  -v $(pwd)/models:/app/models:ro \
  -v $(pwd)/static:/app/static \
  --restart unless-stopped \
  your-username/tbank-detector:latest
```

## Использование

### Веб-интерфейс

1. Откройте http://localhost:8000 для работы с изображениями
2. Откройте http://localhost:8000/video для работы с видео
3. Загрузите файл и нажмите "Обработать"
4. Просмотрите результаты с нарисованными боксами

### API

```bash
# Детекция на изображении
curl -X POST "http://localhost:8000/detect" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@image.jpg"

# Детекция с визуализацией
curl -X POST "http://localhost:8000/detect-image" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@image.jpg"
```

## Параметры модели

- **Confidence threshold**: 0.25
- **IoU threshold**: 0.01
- **Цвет боксов**: Magenta
- **Толщина линий**: 2px

## Ограничения

- Время обработки: до 10 секунд на изображение
- Поддерживаемые форматы изображений: JPEG, PNG, BMP, WEBP
- Поддерживаемые форматы видео: MP4, AVI
- Порт сервиса: 8000

## Производительность

- Обработка изображений: ~1-2 секунды
- Обработка видео: зависит от длины и разрешения
- Оптимизация: прямая передача видео в YOLO без разбивки на кадры

## Технические детали

- Python 3.10.11
- FastAPI с автоматической документацией
- Асинхронная обработка файлов
- Валидация типов файлов
- Обработка ошибок
- Responsive веб-интерфейс
