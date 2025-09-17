FROM ultralytics/ultralytics:latest-cpu

WORKDIR /app

RUN pip install fastapi==0.104.1 uvicorn[standard]==0.24.0 pydantic==2.5.0 python-multipart

COPY . .

EXPOSE 8000

CMD ["python", "main.py"]

