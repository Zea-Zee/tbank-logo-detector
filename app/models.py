from pydantic import BaseModel, Field
from typing import List, Optional


class BoundingBox(BaseModel):
    """Абсолютные координаты BoundingBox"""
    x_min: int = Field(..., description="Левая координата", ge=0)
    y_min: int = Field(..., description="Верхняя координата", ge=0)
    x_max: int = Field(..., description="Правая координата", ge=0)
    y_max: int = Field(..., description="Нижняя координата", ge=0)


class Detection(BaseModel):
    """Результат детекции одного логотипа"""
    bbox: BoundingBox = Field(..., description="Результат детекции")


class DetectionResponse(BaseModel):
    """Ответ API с результатами детекции"""
    detections: List[Detection] = Field(..., description="Список найденных логотипов")


class ErrorResponse(BaseModel):
    """Ответ при ошибке"""
    error: str = Field(..., description="Описание ошибки")
    detail: Optional[str] = Field(None, description="Дополнительная информация")


class ImageDetectionResponse(BaseModel):
    """Ответ с изображением и детекциями"""
    image_data: str = Field(..., description="Путь к файлу изображения с боксами")
    detections: List[Detection] = Field(..., description="Список найденных логотипов")


class VideoDetectionResponse(BaseModel):
    """Ответ с видео и детекциями"""
    video_data: str = Field(..., description="Путь к файлу видео с боксами")
    total_detections: int = Field(..., description="Общее количество детекций")
