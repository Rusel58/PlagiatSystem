import os
import uuid

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

def save_file(file_bytes: bytes, original_filename: str) -> str:
    file_id = str(uuid.uuid4())
    ext = os.path.splitext(original_filename)[1] or ".txt"
    path = os.path.join(DATA_DIR, file_id + ext)
    with open(path, "wb") as f:
        f.write(file_bytes)
    return file_id, path

def get_file_path(file_id: str) -> str:
    # Находит файл с нужным префиксом
    for name in os.listdir(DATA_DIR):
        if name.startswith(file_id):
            return os.path.join(DATA_DIR, name)
    return None
