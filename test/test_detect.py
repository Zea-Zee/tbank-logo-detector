import requests
import os
import json
from pathlib import Path


def test_detect_api():
    """Тестирование API эндпоинта /detect"""
    base_url = "http://localhost:8000"
    media_dir = Path("./test/media")

    if not media_dir.exists():
        print(f"Папка {media_dir} не найдена")
        return

    image_files = []
    for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.webp']:
        image_files.extend(media_dir.glob(ext))

    if not image_files:
        print("Изображения не найдены в папке test/media")
        return

    print(f"Найдено {len(image_files)} изображений для тестирования")

    for image_path in image_files:
        print(f"\nТестирование: {image_path.name}")

        try:
            with open(image_path, 'rb') as f:
                files = {'file': (image_path.name, f, f'image/{image_path.suffix[1:]}')}

                response = requests.post(f"{base_url}/detect", files=files)

                if response.status_code == 200:
                    data = response.json()
                    detections = data.get('detections', [])

                    print(f"  Статус: {response.status_code}")
                    print(f"  Найдено детекций: {len(detections)}")

                    for i, detection in enumerate(detections):
                        bbox = detection['bbox']
                        print(f"    Бокс {i+1}: ({bbox['x_min']}, {bbox['y_min']}) - ({bbox['x_max']}, {bbox['y_max']})")

                else:
                    print(f"  Ошибка: {response.status_code}")
                    try:
                        error_data = response.json()
                        print(f"  Сообщение: {error_data.get('detail', 'Неизвестная ошибка')}")
                    except:
                        print(f"  Ответ: {response.text}")

        except requests.exceptions.ConnectionError:
            print("  Ошибка: Не удается подключиться к серверу")
            break
        except Exception as e:
            print(f"  Ошибка: {e}")


if __name__ == "__main__":
    test_detect_api()

