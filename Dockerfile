# FROM python:3.10.11-slim
FROM ultralytics/ultralytics:latest-cpu

WORKDIR /app

# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt
RUN pip install fastapi==0.104.1 uvicorn[standard]==0.24.0 pydantic==2.5.0

COPY . .

EXPOSE 8000

CMD ["python", "main.py"]
