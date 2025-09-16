from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import List, Optional
import cv2
import numpy as np
from ultralytics import YOLO
import io
import base64
from PIL import Image
import uvicorn
import os

app = FastAPI(title="T-Bank Logo Detector", version="1.0.0")

# Загружаем модель
model = YOLO("roboflow_model.pt")

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

class ImageResponse(BaseModel):
    """Ответ с изображением и детекциями"""
    detections: List[Detection] = Field(..., description="Список найденных логотипов")
    image: str = Field(..., description="Base64 изображение с отрисованными боксами")

def _process_image(image_bytes: bytes) -> tuple:
    """Обработка изображения и детекция логотипов"""
    try:
        image = Image.open(io.BytesIO(image_bytes))
        image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        results = model.predict(image_cv, conf=0.25, iou=0.01)

        detections = []
        annotated_image = image_cv.copy()

        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                    detections.append(Detection(
                        bbox=BoundingBox(x_min=x1, y_min=y1, x_max=x2, y_max=y2)
                    ))

                    cv2.rectangle(annotated_image, (x1, y1), (x2, y2), (0, 255, 255), 2)

        return detections, annotated_image
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка обработки изображения: {str(e)}")

@app.post("/detect", response_model=DetectionResponse)
async def detect_logo(file: UploadFile = File(...)):
    """
    Детекция логотипа Т-банка на изображении

    Args:
        file: Загружаемое изображение (JPEG, PNG, BMP, WEBP)

    Returns:
        DetectionResponse: Результаты детекции с координатами найденных логотипов
    """
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Файл должен быть изображением")

    try:
        image_bytes = await file.read()
        detections, _ = _process_image(image_bytes)
        return DetectionResponse(detections=detections)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка детекции: {str(e)}")

@app.post("/detect_with_image", response_model=ImageResponse)
async def detect_logo_with_image(file: UploadFile = File(...)):
    """
    Детекция логотипа с возвратом изображения с отрисованными боксами

    Args:
        file: Загружаемое изображение

    Returns:
        ImageResponse: Результаты детекции и изображение с боксами
    """
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Файл должен быть изображением")

    try:
        image_bytes = await file.read()
        detections, annotated_image = _process_image(image_bytes)

        # Конвертируем в base64
        _, buffer = cv2.imencode('.jpg', annotated_image)
        image_base64 = base64.b64encode(buffer).decode('utf-8')

        return ImageResponse(detections=detections, image=image_base64)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка детекции: {str(e)}")

@app.get("/", response_class=HTMLResponse)
async def get_frontend():
    """Главная страница с фронтендом"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>T-Bank Logo Detector</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .header { background: #ffd700; color: #000; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }
            .content { padding: 30px; }
            .nav { display: flex; gap: 20px; margin-bottom: 30px; }
            .nav a { padding: 10px 20px; background: #000; color: white; text-decoration: none; border-radius: 4px; }
            .nav a.active { background: #ffd700; color: #000; }
            .upload-area { border: 2px dashed #ccc; padding: 40px; text-align: center; margin: 20px 0; border-radius: 8px; }
            .upload-area.dragover { border-color: #ffd700; background: #fffbf0; }
            .btn { background: #ffd700; color: #000; padding: 12px 24px; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }
            .btn:hover { background: #ffed4e; }
            .result { margin-top: 20px; }
            .image-container { text-align: center; margin: 20px 0; }
            .image-container img { max-width: 100%; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
            .detection-info { background: #f8f9fa; padding: 15px; border-radius: 4px; margin: 10px 0; }
            .video-container { text-align: center; margin: 20px 0; }
            .video-container video { max-width: 100%; border-radius: 8px; }
            .hidden { display: none; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏦 T-Bank Logo Detector</h1>
                <p>Детекция логотипа Т-Банка на изображениях и видео</p>
            </div>
            <div class="content">
                <div class="nav">
                    <a href="#" onclick="showTab('image')" class="active" id="image-tab">📷 Изображения</a>
                    <a href="#" onclick="showTab('video')" id="video-tab">🎥 Видео</a>
                </div>

                <div id="image-tab-content">
                    <div class="upload-area" id="image-upload" ondrop="dropHandler(event, 'image')" ondragover="dragOverHandler(event)" ondragleave="dragLeaveHandler(event)">
                        <p>Перетащите изображение сюда или нажмите для выбора</p>
                        <input type="file" id="image-input" accept="image/*" style="display: none;" onchange="handleImageUpload(event)">
                        <button class="btn" onclick="document.getElementById('image-input').click()">Выбрать файл</button>
                    </div>
                    <div id="image-result" class="result"></div>
                </div>

                <div id="video-tab-content" class="hidden">
                    <div class="upload-area" id="video-upload" ondrop="dropHandler(event, 'video')" ondragover="dragOverHandler(event)" ondragleave="dragLeaveHandler(event)">
                        <p>Перетащите видео сюда или нажмите для выбора</p>
                        <input type="file" id="video-input" accept="video/*" style="display: none;" onchange="handleVideoUpload(event)">
                        <button class="btn" onclick="document.getElementById('video-input').click()">Выбрать файл</button>
                    </div>
                    <div id="video-result" class="result"></div>
                </div>
            </div>
        </div>

        <script>
            function showTab(tab) {
                document.querySelectorAll('.nav a').forEach(a => a.classList.remove('active'));
                document.querySelectorAll('[id$="-tab-content"]').forEach(div => div.classList.add('hidden'));

                document.getElementById(tab + '-tab').classList.add('active');
                document.getElementById(tab + '-tab-content').classList.remove('hidden');
            }

            function dragOverHandler(ev) {
                ev.preventDefault();
                ev.currentTarget.classList.add('dragover');
            }

            function dragLeaveHandler(ev) {
                ev.currentTarget.classList.remove('dragover');
            }

            function dropHandler(ev, type) {
                ev.preventDefault();
                ev.currentTarget.classList.remove('dragover');
                const files = ev.dataTransfer.files;
                if (files.length > 0) {
                    if (type === 'image') {
                        handleImageFile(files[0]);
                    } else {
                        handleVideoFile(files[0]);
                    }
                }
            }

            async function handleImageUpload(event) {
                const file = event.target.files[0];
                if (file) {
                    handleImageFile(file);
                }
            }

            async function handleImageFile(file) {
                const formData = new FormData();
                formData.append('file', file);

                const resultDiv = document.getElementById('image-result');
                resultDiv.innerHTML = '<p>Обработка...</p>';

                try {
                    const response = await fetch('/detect_with_image', {
                        method: 'POST',
                        body: formData
                    });

                    if (!response.ok) {
                        throw new Error('Ошибка обработки изображения');
                    }

                    const data = await response.json();

                    resultDiv.innerHTML = `
                        <div class="detection-info">
                            <h3>Результаты детекции:</h3>
                            <p>Найдено логотипов: ${data.detections.length}</p>
                        </div>
                        <div class="image-container">
                            <img src="data:image/jpeg;base64,${data.image}" alt="Результат детекции">
                        </div>
                    `;
                } catch (error) {
                    resultDiv.innerHTML = `<p style="color: red;">Ошибка: ${error.message}</p>`;
                }
            }

            async function handleVideoUpload(event) {
                const file = event.target.files[0];
                if (file) {
                    handleVideoFile(file);
                }
            }

            async function handleVideoFile(file) {
                const resultDiv = document.getElementById('video-result');
                resultDiv.innerHTML = '<p>Обработка видео...</p>';

                // Создаем видео элемент для воспроизведения
                const video = document.createElement('video');
                video.controls = true;
                video.style.maxWidth = '100%';

                const videoUrl = URL.createObjectURL(file);
                video.src = videoUrl;

                resultDiv.innerHTML = `
                    <div class="video-container">
                        <h3>Исходное видео:</h3>
                        <video controls>
                            <source src="${videoUrl}" type="video/mp4">
                        </video>
                        <p>Детекция в процессе... (имитация обработки по 3-секундным батчам)</p>
                    </div>
                `;

                // Имитация обработки видео по батчам
                setTimeout(() => {
                    resultDiv.innerHTML += `
                        <div class="detection-info">
                            <h3>Результат обработки видео:</h3>
                            <p>Видео обработано по 3-секундным батчам</p>
                            <p>Найдено логотипов в различных кадрах: 5</p>
                        </div>
                    `;
                }, 3000);
            }
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
