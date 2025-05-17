from sqlalchemy.orm import Session
import os
from fastapi.responses import FileResponse
from fastapi import HTTPException, Depends, FastAPI, UploadFile, File
from database import SessionLocal, init_db, FileMeta
from storage import save_file, get_file_path
from models import UploadResponse, ErrorResponse
import hashlib

init_db()
app = FastAPI(title="File Storing Service", version="1.0")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/upload", response_model=UploadResponse, responses={400: {"model": ErrorResponse}})
async def upload(
        file: UploadFile = File(...),
        db: Session = Depends(get_db),  # <-- исправлено
):
    if not file.filename.endswith(".txt"):
        raise HTTPException(status_code=400, detail="Only .txt files allowed")
    content = await file.read()

    # 1) вычисляем хэш
    digest = hashlib.sha256(content).hexdigest()
    # 2) проверяем, не загружали ли уже
    existing = db.query(FileMeta).filter_by(digest=digest).first()

    if existing:
        return UploadResponse(file_id=existing.file_id)


    file_id, _ = save_file(content, file.filename)
    # сохраняем мета в БД
    meta = FileMeta(file_id=file_id, filename=file.filename, digest=digest)
    db.add(meta)
    db.commit()
    return UploadResponse(file_id=file_id)


@app.get("/download/{file_id}")
def download(file_id: str, db: Session = Depends(get_db)):
    # 1) находим путь к файлу
    path = get_file_path(file_id)
    if not path:
        raise HTTPException(status_code=404, detail="File not found")

    # 2) отдаём файл с правильными HTTP-заголовками
    filename = os.path.basename(path)
    return FileResponse(
        path,
        media_type="text/plain",
        filename=filename,
    )
