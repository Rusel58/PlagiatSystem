from pydantic import BaseModel
from typing import Optional


class AnalysisResponse(BaseModel):
    file_id: str
    paragraphs: int
    words: int
    characters: int
    wordcloud_loc: Optional[str] = None

class ErrorResponse(BaseModel):
    detail: str
