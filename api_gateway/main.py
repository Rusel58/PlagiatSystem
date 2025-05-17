from fastapi import FastAPI, UploadFile, File, Query
from fastapi.responses import Response, JSONResponse
import httpx
import os

app = FastAPI(title="API Gateway", version="1.0")

# URL-ы из докера: file-service и analysis-service
FILE_SVC     = os.getenv("FILE_SERVICE_URL",     "http://file-service:8001")
ANALYSIS_SVC = os.getenv("ANALYSIS_SERVICE_URL", "http://analysis-service:8002")


@app.post("/upload")
async def proxy_upload(file: UploadFile = File(...)):
    file_bytes = await file.read()
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{FILE_SVC}/upload",
            files={"file": (file.filename, file_bytes)},
        )
    if 200 <= resp.status_code < 300:
        return JSONResponse(status_code=resp.status_code, content=resp.json(), headers=dict(resp.headers))
    return Response(content=resp.content, status_code=resp.status_code,
                    media_type=resp.headers.get("content-type", "application/json"))


@app.get("/download/{file_id}")
async def proxy_download(file_id: str):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{FILE_SVC}/download/{file_id}")
    if 200 <= resp.status_code < 300:
        return Response(content=resp.content, status_code=resp.status_code,
                        media_type=resp.headers.get("content-type", "application/octet-stream"),
                        headers=dict(resp.headers))
    return Response(content=resp.content, status_code=resp.status_code,
                    media_type=resp.headers.get("content-type", "application/json"))


@app.post("/analyze/{file_id}")
async def proxy_analyze(
    file_id: str,
    with_wordcloud: bool = Query(False, description="Include word cloud generation"),
):
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{ANALYSIS_SVC}/analyze/{file_id}",
            params={"with_wordcloud": str(with_wordcloud).lower()}
        )
    if 200 <= resp.status_code < 300:
        return JSONResponse(status_code=resp.status_code, content=resp.json(), headers=dict(resp.headers))
    return Response(content=resp.content, status_code=resp.status_code,
                    media_type=resp.headers.get("content-type", "application/json"))


@app.get("/wordcloud/{location}")
async def proxy_wordcloud(location: str):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{ANALYSIS_SVC}/wordcloud/{location}")
    if 200 <= resp.status_code < 300:
        return Response(content=resp.content, status_code=resp.status_code,
                        media_type=resp.headers.get("content-type", "image/png"),
                        headers=dict(resp.headers))
    return Response(content=resp.content, status_code=resp.status_code,
                    media_type=resp.headers.get("content-type", "application/json"))
