FROM python:3.11-slim

WORKDIR /app
COPY ./app_backend.py /app/app_backend.py
COPY ./main.py /app/
COPY ./schemas.py /app/
COPY ./requirements.txt /app/

# RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -r requirements.txt


CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
