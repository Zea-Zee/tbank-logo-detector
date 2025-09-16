#!/bin/bash

# Скрипт для сборки и отправки Docker образа

# Настройки
IMAGE_NAME="tbank-logo-detector"
DOCKERHUB_USERNAME="yourusername"  # Замените на ваш username
TAG="latest"

echo "Сборка Docker образа..."
docker build -t $IMAGE_NAME .

echo "Тегирование образа для Docker Hub..."
docker tag $IMAGE_NAME $DOCKERHUB_USERNAME/$IMAGE_NAME:$TAG

echo "Вход в Docker Hub..."
docker login

echo "Отправка образа на Docker Hub..."
docker push $DOCKERHUB_USERNAME/$IMAGE_NAME:$TAG

echo "Готово! Образ доступен по адресу:"
echo "docker pull $DOCKERHUB_USERNAME/$IMAGE_NAME:$TAG"
