from typing import List, Optional

from pydantic import BaseModel
from pydantic_sqlalchemy import sqlalchemy_to_pydantic

from onlyfilms.models.orm import Film, Review, User

FilmModelBase = sqlalchemy_to_pydantic(Film)
UserModel = sqlalchemy_to_pydantic(User, exclude=['password', 'register_date'])
ReviewModelBase = sqlalchemy_to_pydantic(Review, exclude=['author_id'])


class ReviewModel(ReviewModelBase):
    author: Optional[UserModel] = None


class Films(BaseModel):
    films: List[FilmModelBase]
    total: int
    offset: int


class FilmModel(FilmModelBase):
    score: Optional[float] = None


class Reviews(BaseModel):
    movie: str
    reviews: List[ReviewModel]
    total: int
    offset: int


class FilmInfoModel(BaseModel):
    film: FilmModel
    reviews: List[ReviewModel]
    score: Optional[float]
