from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import logging
from .models import DetectionResponse, ImageDetectionResponse, VideoDetectionResponse, ErrorResponse
from .detector import LogoDetector

logger = logging.getLogger(__name__)

app = FastAPI(title="T-Bank Logo Detector", version="1.0.0")

detector = LogoDetector()

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def root():
    """Главная страница"""
    return FileResponse("static/index.html")


@app.get("/video", response_class=HTMLResponse)
async def video_page():
    """Страница обработки видео"""
    return FileResponse("static/video.html")


@app.get("/static/{file_path:path}")
async def serve_static_file(file_path: str):
    """Отдача статических файлов"""
    return FileResponse(f"static/{file_path}")


@app.get("/temp/{file_path:path}")
async def serve_temp_file(file_path: str):
    """Отдача временных файлов"""
    return FileResponse(f"temp/{file_path}")


@app.post("/detect", response_model=DetectionResponse)
async def detect_logo(file: UploadFile = File(...)):
    """
    Детекция логотипа Т-банка на изображении

    Args:
        file: Загружаемое изображение (JPEG, PNG, BMP, WEBP)

    Returns:
        DetectionResponse: Результаты детекции с координатами найденных логотипов
    """
    logger.info(f"Запрос детекции: {file.filename}, тип: {file.content_type}")
    try:
        image_bytes = await file.read()
        logger.info(f"Файл прочитан, размер: {len(image_bytes)} байт")

        detections, _ = detector.detect_image(image_bytes)
        logger.info(f"Детекция завершена, найдено: {len(detections)} объектов")

        return DetectionResponse(detections=detections)
    except Exception as e:
        logger.error(f"Ошибка детекции: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ошибка обработки: {str(e)}")


@app.post("/detect-image", response_model=ImageDetectionResponse)
async def detect_image_with_visualization(file: UploadFile = File(...)):
    """Детекция с визуализацией для фронтенда"""
    logger.info(f"Запрос детекции с визуализацией: {file.filename}, тип: {file.content_type}")

    try:
        image_bytes = await file.read()
        logger.info(f"Файл прочитан, размер: {len(image_bytes)} байт")

        detections, result_path = detector.detect_image(image_bytes)
        logger.info(f"Детекция завершена, найдено: {len(detections)} объектов")
        logger.info(f"Результат сохранен: {result_path}")

        return ImageDetectionResponse(image_data=result_path, detections=detections)
    except Exception as e:
        logger.error(f"Ошибка детекции с визуализацией: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ошибка обработки: {str(e)}")


@app.post("/detect-video", response_model=VideoDetectionResponse)
async def detect_video_with_visualization(file: UploadFile = File(...)):
    """Детекция на видео с визуализацией"""
    logger.info(f"Запрос детекции видео: {file.filename}, тип: {file.content_type}")

    try:
        video_bytes = await file.read()
        logger.info(f"Видео прочитано, размер: {len(video_bytes)} байт")

        total_detections, result_path = detector.detect_video(video_bytes)
        logger.info(f"Детекция видео завершена, найдено: {total_detections} объектов")
        logger.info(f"Результат сохранен: {result_path}")

        return VideoDetectionResponse(video_data=result_path, total_detections=total_detections)
    except Exception as e:
        logger.error(f"Ошибка детекции видео: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ошибка обработки: {str(e)}")
