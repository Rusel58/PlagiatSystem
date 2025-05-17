FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# создаём локальную папку для хранения txt-файлов
RUN mkdir /data

ENV DATA_DIR=/data
ENV DATABASE_URL=postgresql+psycopg2://kpo_user:kpo_pass@postgres:5432/kpo_db

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
