import pytest
from fastapi.testclient import TestClient
from file_service.main import app

client = TestClient(app)

def test_upload_and_download(tmp_path, monkeypatch):
    # заглушка: сохраняем файл во временную директорию
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    content = b"Hello\n\nWorld"
    resp = client.post("/upload", files={"file": ("test.txt", content)})
    assert resp.status_code == 200
    file_id = resp.json()["file_id"]

    dl = client.get(f"/download/{file_id}")
    assert dl.status_code == 200
    assert dl.content == content
