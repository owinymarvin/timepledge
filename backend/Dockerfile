FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app_backend.py .

EXPOSE 8000

CMD ["fastapi", "dev", "app_backend.py"]
