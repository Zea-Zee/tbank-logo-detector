#!/bin/bash

# Скрипт для сборки и отправки образа на Docker Hub

IMAGE_NAME="tbank-detector"
VERSION="latest"
DOCKER_USERNAME="your-username"  # Замените на ваш Docker Hub username

echo "Сборка Docker образа..."
docker build -t $DOCKER_USERNAME/$IMAGE_NAME:$VERSION .

echo "Тегирование образа..."
docker tag $DOCKER_USERNAME/$IMAGE_NAME:$VERSION $DOCKER_USERNAME/$IMAGE_NAME:latest

echo "Отправка на Docker Hub..."
docker push $DOCKER_USERNAME/$IMAGE_NAME:$VERSION
docker push $DOCKER_USERNAME/$IMAGE_NAME:latest

echo "Готово! Образ доступен как: $DOCKER_USERNAME/$IMAGE_NAME:latest"
