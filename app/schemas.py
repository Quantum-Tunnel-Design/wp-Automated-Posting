from pydantic import BaseModel, Field
from typing import List, Optional

class BlogRequest(BaseModel):
    topic: str = Field(..., min_length=3, max_length=100)
    word_count: int = Field(..., ge=50, le=2000)
    background: Optional[str] = Field(None, max_length=500)
    keywords: List[str] = []
    status: str = Field(default="publish", pattern="^(publish|draft|pending)$")


class PostRequest(BaseModel):
    title: str
    content: str
    status: str = "publish"

