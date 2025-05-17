from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import requests
import os

from database import init_db, SessionLocal, AnalysisResult
from analysis import compute_stats, hash_text, generate_wordcloud
from models import AnalysisResponse, ErrorResponse

# URL File Service внутри Docker-сети
FILE_SERVICE_URL = os.getenv("FILE_SERVICE_URL", "http://file-service:8001")

# Папка для сохранения облаков слов
DATA_DIR = os.getenv("DATA_DIR", "data")
os.makedirs(DATA_DIR, exist_ok=True)

# создаём таблицы при старте
init_db()

app = FastAPI(title="File Analysis Service", version="1.0")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post(
    "/analyze/{file_id}",
    response_model=AnalysisResponse,
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
def analyze(
    file_id: str,
    with_wordcloud: bool = False,
    db: Session = Depends(get_db),
):
    # 0) Проверяем кэш
    existing = db.query(AnalysisResult).get(file_id)
    if existing and not with_wordcloud:
        return AnalysisResponse(
            file_id=existing.file_id,
            paragraphs=existing.paragraphs,
            words=existing.words,
            characters=existing.characters,
            is_plagiarized=existing.is_plagiarized,
            wordcloud_loc=existing.wordcloud_loc,
        )

    # 1) Скачиваем текст из File Service
    resp = requests.get(f"{FILE_SERVICE_URL}/download/{file_id}")
    if resp.status_code == 404:
        raise HTTPException(status_code=404, detail="File not found")
    if resp.status_code != 200:
        raise HTTPException(status_code=500, detail="Error contacting storage service")
    text = resp.text

    # 2) Анализируем текст
    paragraphs, words, characters = compute_stats(text)
    digest = hash_text(text)

    # 3) Генерируем облако слов, если нужно
    wc_loc = None
    if with_wordcloud:
        img_bytes = generate_wordcloud(text)
        wc_loc = f"{file_id}.png"
        path = os.path.join(DATA_DIR, wc_loc)
        with open(path, "wb") as f:
            f.write(img_bytes)

    # 4) Проверяем плагиат (сравниваем digest со всеми остальными)
    others = db.query(AnalysisResult).filter(AnalysisResult.file_id != file_id).all()
    is_plag = any(r.digest == digest for r in others)

    # 5) Сохраняем или обновляем результат
    result = AnalysisResult(
        file_id=file_id,
        paragraphs=paragraphs,
        words=words,
        characters=characters,
        wordcloud_loc=wc_loc,
    )
    db.merge(result)
    db.commit()

    # 6) Возвращаем ответ
    return AnalysisResponse(
        file_id=file_id,
        paragraphs=paragraphs,
        words=words,
        characters=characters,
        is_plagiarized=is_plag,
        wordcloud_loc=wc_loc,
    )


@app.get(
    "/wordcloud/{loc}",
    responses={404: {"model": ErrorResponse}}
)
def serve_wordcloud(loc: str):
    path = os.path.join(DATA_DIR, loc)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Wordcloud not found")
    return FileResponse(path, media_type="image/png")
