from typing import Optional, List, Callable, Any
import json
from functools import wraps

from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError

from onlyfilms import Session as SessionCreator
from onlyfilms.models.orm import Film, Review, User, Token


def orm_function(func: Callable[..., Any]):
    @wraps(func)
    def wrapper(*args, **kwargs):
        with SessionCreator() as session:
            return func(*args, session=session, **kwargs)

    return wrapper


@orm_function
def get_film_by_id(film_id: int, session: Session = None) -> Film:
    film = session.query(Film).filter(Film.id == film_id).first()

    return film


@orm_function
def get_films(
    query: Optional[str] = None,
    offset: int = 0,
    min_rating: float = 0.0,
    session: Session = None,
) -> List[Film]:
    films = session.query(Film).all()

    return films


@orm_function
def get_reviews(
    film_id: int, limit: int = 3, offset: int = 0, session: Session = None
) -> List[Review]:
    reviews = (
        session.query(Review)
        .options(joinedload(Review.author))
        .filter(Review.film_id == film_id)
        .order_by(Review.created)
        .offset(offset)
        .limit(limit)
        .all()
    )

    return reviews


@orm_function
def get_user(user_id: int, session: Session = None) -> User:
    return session.query(User).filter(User.id == user_id).first()


def load_films(path: str) -> None:
    with open(path, 'r') as file:
        data = json.load(file)

    films = []
    for json_film in data:
        films.append(Film(**json_film))

    with SessionCreator() as session:
        session.add_all(films)

        session.commit()


@orm_function
def regster_user(login: str, password: str, session: Session = None) -> bool:
    new_user = User(login, password)
    session.add(new_user)

    try:
        session.commit()
        session.expunge(new_user)
    except SQLAlchemyError:
        session.rollback()
        return False
    return True


@orm_function
def login_user(login: str, password: str, session: Session = None) -> Optional[str]:
    user: User = session.query(User).filter(User.login == login).first()

    if user and user.check_password(password):
        new_token = Token(user)
        token = new_token.token
        session.add(new_token)

        try:
            session.commit()
            return token
        except SQLAlchemyError:
            session.rollback()
    return None
