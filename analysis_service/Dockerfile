FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV DATABASE_URL=postgresql+psycopg2://kpo_user:kpo_pass@postgres:5432/kpo_db
ENV FILE_SERVICE_URL=http://file-service:8001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]

