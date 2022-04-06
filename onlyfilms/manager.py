from typing import Optional, List
import json

from onlyfilms import Session
from onlyfilms.models.orm import Film


def get_films(query: Optional[str] = None, offset: int = 0, min_rating: float = 0.0) -> List[Film]:
    with Session() as session:
        films = session.query(Film).all()

    return films


def load_films(path: str) -> None:
    with open(path, 'r') as file:
        data = json.load(file)

    films = []
    for json_film in data:
        films.append(Film(**json_film))

    with Session() as session:
        session.add_all(films)

        session.commit()
