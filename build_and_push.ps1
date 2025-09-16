# PowerShell скрипт для сборки и отправки Docker образа

# Настройки
$IMAGE_NAME = "tbank-logo-detector"
$DOCKERHUB_USERNAME = "yourusername"  # Замените на ваш username
$TAG = "latest"

Write-Host "Сборка Docker образа..." -ForegroundColor Green
docker build -t $IMAGE_NAME .

Write-Host "Тегирование образа для Docker Hub..." -ForegroundColor Green
docker tag $IMAGE_NAME "$DOCKERHUB_USERNAME/$IMAGE_NAME`:$TAG"

Write-Host "Вход в Docker Hub..." -ForegroundColor Green
docker login

Write-Host "Отправка образа на Docker Hub..." -ForegroundColor Green
docker push "$DOCKERHUB_USERNAME/$IMAGE_NAME`:$TAG"

Write-Host "Готово! Образ доступен по адресу:" -ForegroundColor Yellow
Write-Host "docker pull $DOCKERHUB_USERNAME/$IMAGE_NAME`:$TAG" -ForegroundColor Cyan
