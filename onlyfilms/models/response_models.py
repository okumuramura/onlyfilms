from typing import List, Optional
import datetime

from pydantic import BaseModel


class FilmModel(BaseModel):
    id: int
    title: str
    director: Optional[str] = None
    cover: Optional[str] = None
    score: str = '0.0'


class FilmsListModel(BaseModel):
    films: List[FilmModel]
    total: int
    offset: int

    class Config:
        orm_mode = True


class Review(BaseModel):
    id: int
    author: str
    movie: str
    created: datetime.datetime
    text: str


class Reviews(BaseModel):
    movie: str
    reviews: List[Review]
    total: int
    offset: int
