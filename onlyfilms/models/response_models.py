from typing import List, Optional

from pydantic import BaseModel


class FilmModel(BaseModel):
    id: int
    title: str
    director: Optional[str] = None
    rating: str = '0.0'


class FilmsListModel(BaseModel):
    films: List[FilmModel]
    total: int
    offset: int
