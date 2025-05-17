# Plagiat_System: Микросервисная архитектура текстового сканера

Этот проект реализует микросервисную серверную часть веб‑приложения для текстового сканера. Функционал включает:

* загрузку отчётов студентов (`.txt`),
* анализ текста (подсчёт абзацев, слов и символов),
* выявление 100% плагиата среди ранее присланных отчётов,
* генерацию облака слов.

## Описание архитектуры

Система состоит из трёх FastAPI‑микросервисов и API Gateway:

1. **API Gateway**

   * Единая точка входа: `/upload`, `/download/{file_id}`, `/analyze/{file_id}`, `/wordcloud/{location}`
   * Проксирует запросы к File-Service и Analysis-Service
   * Автоматически генерирует документацию OpenAPI (Swagger) на `/docs`

2. **File-Service**

   * Отвечает за хранение и выдачу файлов
   * Дедупликация содержимого по SHA-256
   * Метаданные хранятся в PostgreSQL, сами файлы — на диске

3. **Analysis-Service**

   * Проводит анализ текста (абзацы, слова, символы)
   * Опциональная генерация облака слов (параметр `with_wordcloud`)
   * Результаты анализа сохраняются в PostgreSQL, а изображение облака — на диске

Все сервисы используют одну базу PostgreSQL и взаимодействуют через Docker Compose с двумя сетями (`internal`, `external`). Внешне доступен только API Gateway.

## Требования

* Docker Engine (v20+)
* Docker Compose (v1.27+)
* (Опционально) Python 3.11 для локальной разработки без Docker

## Структура проекта

```
KPO_KR2/
├── api_gateway/
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
├── file_service/
│   ├── Dockerfile
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── storage.py
│   └── requirements.txt
├── analysis_service/
│   ├── Dockerfile
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── analysis.py
│   └── requirements.txt
├── docker-compose.yml
└── README.md
```

## Технологии и решения

* **Python 3.11** и **FastAPI** для высокопроизводительных HTTP-сервисов.
* **PostgreSQL** как надёжная реляционная БД для метаданных.
* **SQLAlchemy** / **Alembic** (миграции при необходимости) для ORM и управления схемой.
* **httpx.AsyncClient** в API Gateway для асинхронного проксирования запросов.
* **docker-compose** с двумя сетями (`internal`, `external`) для жёсткой изоляции.
* **SHA-256** для дедупликации в File-Service.
* **wordcloud** для генерации PNG-облака слов в Analysis-Service.
* **Pydantic** для строгой валидации и авто‑документации моделей запроса/ответа.

## Локальная разработка

1. Клонируйте репозиторий и перейдите в папку:

   ```bash
   git clone https://github.com/Rusel58/Plagiat_System.git
   cd KPO_KR2
   ```

2. (Опционально) Создайте venv и установите зависимости для каждого сервиса:

   ```bash
   cd file_service && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
   cd ../analysis_service && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
   cd ../api_gateway && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
   ```

3. Запустите сервисы вручную (без Docker):

   ```bash
   export DATABASE_URL=postgresql+psycopg2://kpo_user:kpo_pass@localhost:5432/kpo_db
   # В одном терминале: uvicorn main:app --reload --port 8001  (file-service)
   # В другом: uvicorn main:app --reload --port 8002  (analysis-service)
   # И в третьем (Gateway):
   export FILE_SERVICE_URL=http://localhost:8001
   export ANALYSIS_SERVICE_URL=http://localhost:8002
   uvicorn main:app --reload --port 8000
   ```

## Docker: сборка и запуск

1. Соберите образы и запустите все контейнеры:

   ```bash
   docker-compose build
   docker-compose up -d
   ```

2. Проверьте статус:

   ```bash
   docker-compose ps
   ```

3. Логи сервисов:

   ```bash
   docker-compose logs -f api-gateway
   docker-compose logs -f file-service
   docker-compose logs -f analysis-service
   ```

### Открытые порты

* **API Gateway**: `localhost:8000`
* **PostgreSQL**, **File-Service**, **Analysis-Service**: недоступны внешне (только во внутренней сети)

### Остановка и очистка

* Остановить и удалить контейнеры и сети:

  ```bash
  docker-compose down
  ```
* Удалить тома с данными (Postgres, файлы):

  ```bash
  docker-compose down -v
  ```
* Очистить все неиспользуемые образы и контейнеры:

  ```bash
  docker system prune -a
  ```

## Использование API

Откройте документацию Swagger:

```
http://localhost:8000/docs
```

**Основные endpoint'ы:**

* `POST /upload` — загрузить `.txt` (multipart/form-data, поле `file`)

  * Ответ: `{ "file_id": "<uuid>" }`

* `GET /download/{file_id}` — скачать содержимое файла

* `POST /analyze/{file_id}?with_wordcloud={true|false}` — провести анализ текста

  * Параметр `with_wordcloud=true` генерирует и сохраняет облако слов
  * JSON-ответ: количество абзацев, слов, символов и путь `wordcloud_loc`

* `GET /wordcloud/{location}` — получить PNG‑изображение облака слов

## Тестирование

* Используйте Swagger UI или `curl` для проверки всех запросов.
* В репозитории есть пример коллекции Postman в папке `/postman`.

## Качество кода

* Обработка ошибок и retry при подключении к БД.
* Чистая модульная архитектура: разделение File-Service, Analysis-Service и Gateway.

---

*README подготовлен для запуска и поддержки микросервисного приложения Plagiat_System.*
