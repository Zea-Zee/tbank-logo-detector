#!/usr/bin/env python3
"""
Тестовый скрипт для проверки детектора
"""
import logging
import sys
import os

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_detector():
    """Тестирование детектора"""
    try:
        from app.detector import LogoDetector

        logger.info("Инициализация детектора...")
        detector = LogoDetector()
        logger.info("Детектор успешно инициализирован")

        # Проверяем, что модель загружена
        if hasattr(detector, '_model') and detector._model is not None:
            logger.info("Модель загружена успешно")
        else:
            logger.error("Модель не загружена")
            return False

        return True

    except Exception as e:
        logger.error(f"Ошибка тестирования детектора: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    logger.info("Запуск тестирования...")
    success = test_detector()

    if success:
        logger.info("Тест прошел успешно!")
        sys.exit(0)
    else:
        logger.error("Тест не прошел!")
        sys.exit(1)
