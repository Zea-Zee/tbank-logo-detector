import logging
import tempfile
import os
import shutil
from ultralytics import YOLO
from typing import List, Tuple
from .models import Detection, BoundingBox

logger = logging.getLogger(__name__)


class LogoDetector:
    """Детектор логотипа Т-Банка"""

    def __init__(self, model_path: str = "./models/model.pt"):
        logger.info(f"Инициализация детектора с моделью: {model_path}")
        try:
            self._model = YOLO(model_path)
            logger.info("Модель успешно загружена")
        except Exception as e:
            logger.error(f"Ошибка загрузки модели: {e}")
            raise

    def detect_image(self, image_bytes: bytes) -> Tuple[List[Detection], str]:
        """Детекция на изображении"""
        logger.info(f"Начало детекции изображения, размер: {len(image_bytes)} байт")

        try:
            # Сохраняем файл
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                temp_file.write(image_bytes)
                temp_path = temp_file.name

            logger.info(f"Временный файл создан: {temp_path}")

            # Передаем путь в YOLO
            results = self._model.predict(
                temp_path,
                conf=0.25,
                iou=0.01,
                save=True,
                project="temp",
                name="detection"
            )

            logger.info(f"Получено результатов: {len(results)}")

            detections = []
            if results[0].boxes is not None:
                logger.info(f"Найдено боксов: {len(results[0].boxes)}")

                for i, box in enumerate(results[0].boxes):
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    confidence = box.conf[0].cpu().numpy()
                    logger.debug(f"Бокс {i}: ({x1:.1f}, {y1:.1f}, {x2:.1f}, {y2:.1f}), conf: {confidence:.3f}")

                    detections.append(Detection(
                        bbox=BoundingBox(
                            x_min=int(x1),
                            y_min=int(y1),
                            x_max=int(x2),
                            y_max=int(y2)
                        )
                    ))
            else:
                logger.info("Боксы не найдены")

            # Читаем сохраненное изображение - ищем файл в папке результатов
            result_dir = results[0].save_dir
            result_files = os.listdir(result_dir)

            # Ищем изображение (обычно .jpg)
            image_file = None
            for file in result_files:
                if file.endswith(('.jpg', '.jpeg', '.png')):
                    image_file = file
                    break

            if not image_file:
                logger.error(f"Не найден файл изображения в {result_dir}")
                raise ValueError("Не найден результат обработки изображения")

            result_path = os.path.join(result_dir, image_file)
            logger.info(f"Найден результат изображения: {result_path}")

            # Копируем файл в static папку
            static_filename = f"result_{os.path.basename(image_file)}"
            static_path = os.path.join("static", static_filename)
            shutil.copy2(result_path, static_path)
            logger.info(f"Файл скопирован в static: {static_path}")

            # Удаляем временные файлы
            os.unlink(temp_path)
            os.unlink(result_path)
            os.rmdir(result_dir)

            logger.info(f"Детекция завершена, найдено: {len(detections)} объектов")
            return detections, static_filename

        except Exception as e:
            logger.error(f"Ошибка детекции изображения: {e}", exc_info=True)
            # Удаляем временные файлы в случае ошибки
            try:
                if 'temp_path' in locals():
                    os.unlink(temp_path)
            except:
                pass
            raise

    def detect_video(self, video_bytes: bytes) -> Tuple[int, str]:
        """Детекция на видео"""
        logger.info(f"Начало детекции видео, размер: {len(video_bytes)} байт")

        try:
            # Сохраняем файл
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
                temp_file.write(video_bytes)
                temp_path = temp_file.name

            logger.info(f"Временный файл создан: {temp_path}")

            # Передаем путь в YOLO БЕЗ stream=True для сохранения видео
            results = self._model.predict(
                temp_path,
                conf=0.25,
                iou=0.01,
                save=True,
                project="temp",
                name="detection"
            )

            logger.info(f"Получено результатов: {len(results)}")

            total_detections = 0
            for i, result in enumerate(results):
                if result.boxes is not None:
                    total_detections += len(result.boxes)
                    logger.debug(f"Кадр {i}: найдено {len(result.boxes)} объектов")

            logger.info(f"Общее количество детекций: {total_detections}")

            # Читаем сохраненное видео - ищем файл в папке результатов
            result_dir = results[0].save_dir
            result_files = os.listdir(result_dir)

            logger.info(f"Файлы в папке результатов: {result_files}")

            # Ищем видео файл (.mp4 или .avi)
            video_file = None
            for file in result_files:
                if file.endswith(('.mp4', '.avi')):
                    video_file = file
                    break

            if not video_file:
                logger.error(f"Не найден видео файл в {result_dir}")
                raise ValueError("Не найден результат обработки видео")

            result_path = os.path.join(result_dir, video_file)
            logger.info(f"Найден результат видео: {result_path}")

            # Копируем файл в static папку
            static_filename = f"result_{os.path.basename(video_file)}"
            static_path = os.path.join("static", static_filename)
            shutil.copy2(result_path, static_path)
            logger.info(f"Файл скопирован в static: {static_path}")

            # Удаляем временные файлы
            os.unlink(temp_path)
            os.unlink(result_path)
            os.rmdir(result_dir)

            logger.info(f"Детекция видео завершена, найдено: {total_detections} объектов")
            return total_detections, static_filename

        except Exception as e:
            logger.error(f"Ошибка детекции видео: {e}", exc_info=True)
            # Удаляем временные файлы в случае ошибки
            try:
                if 'temp_path' in locals():
                    os.unlink(temp_path)
            except:
                pass
            raise
