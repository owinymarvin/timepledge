FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -r requirements.txt

COPY frontend_app.py .

EXPOSE 8501

CMD ["streamlit", "run", "frontend_app.py", "--server.port=8501", "--server.address=0.0.0.0"]