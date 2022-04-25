from typing import Optional

from pydantic import BaseModel, Field


class RegisterModel(BaseModel):
    login: str = Field(..., min_length=6, max_length=25)
    password: str = Field(..., min_length=5, max_length=20)


class ReviewModel(BaseModel):
    text: str
    score: Optional[int] = Field(None, ge=0.0, le=10.0)
