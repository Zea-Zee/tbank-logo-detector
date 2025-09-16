# 1. Остановить контейнер
docker stop tbank-detector

# 2. Удалить старый контейнер
docker rm tbank-detector

# 3. Пересобрать образ с новым кодом
docker build -t tbank-detector .

# 4. Запустить новый контейнер
docker run -d --name tbank-detector -p 8000:8000 -v $(pwd)/models:/app/models:ro -v $(pwd)/static:/app/static --restart unless-stopped tbank-detector
