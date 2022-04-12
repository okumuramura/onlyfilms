from typing import Optional

from pydantic import BaseModel


class RegisterModel(BaseModel):
    login: str
    password: str


class RatingModel(BaseModel):
    score: int


class ReviewModel(BaseModel):
    text: str
    score: Optional[int] = None
