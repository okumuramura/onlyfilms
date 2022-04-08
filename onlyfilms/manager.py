from typing import Optional, List, Callable, Any
import json
from functools import wraps

from sqlalchemy.orm import Session, contains_eager

from onlyfilms import Session as SessionCreator
from onlyfilms.models.orm import Film, Review


def orm_function(func: Callable[[Session, Any, Any], Any]):
    @wraps(func)
    def wrapper(*args, **kwargs):
        with SessionCreator() as session:
            return func(session, *args, **kwargs)

    return wrapper


@orm_function
def get_film_by_id(session: Session, film_id: int) -> Film:
    film = session.query(Film).filter(Film.id == film_id).first()

    return film


@orm_function
def get_films(
    session: Session,
    query: Optional[str] = None,
    offset: int = 0,
    min_rating: float = 0.0,
) -> List[Film]:
    films = session.query(Film).all()

    return films


@orm_function
def get_reviews(
    session: Session, film_id: int, limit: int = 3, offset: int = 0
) -> List[Review]:
    reviews = (
        session.query(Review)
        .options(contains_eager(Review.author))
        .filter(Review.film_id == film_id)
        .order_by(Review.created)
        .offset(offset)
        .limit(limit)
        .all()
    )

    return reviews


def load_films(path: str) -> None:
    with open(path, 'r') as file:
        data = json.load(file)

    films = []
    for json_film in data:
        films.append(Film(**json_film))

    with SessionCreator() as session:
        session.add_all(films)

        session.commit()
