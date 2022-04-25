from typing import List, Optional

from pydantic import BaseModel
from pydantic_sqlalchemy import sqlalchemy_to_pydantic

from onlyfilms.models.orm import Film, Review, User

FilmModelBase = sqlalchemy_to_pydantic(Film)
UserModel = sqlalchemy_to_pydantic(User, exclude=['password', 'register_date'])
ReviewModelBase = sqlalchemy_to_pydantic(Review, exclude=['author_id'])


class ReviewModel(ReviewModelBase):  # type: ignore
    author: Optional[UserModel] = None  # type: ignore


class FilmModel(FilmModelBase):  # type: ignore
    score: Optional[float] = None
    evaluators: Optional[int] = None


class Films(BaseModel):
    films: List[FilmModel]
    total: int
    offset: int


class Reviews(BaseModel):
    reviews: List[ReviewModel]
    total: int
    offset: int


class FilmInfoModel(BaseModel):
    film: FilmModel
    reviews: List[ReviewModel]
    score: Optional[float]
