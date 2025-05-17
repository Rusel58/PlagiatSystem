from pydantic import BaseModel

class UploadResponse(BaseModel):
    file_id: str

class ErrorResponse(BaseModel):
    detail: str
