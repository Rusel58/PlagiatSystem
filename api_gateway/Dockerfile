FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FILE_SERVICE_URL=http://file-service:8001
ENV ANALYSIS_SERVICE_URL=http://analysis-service:8002

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
