import json
from functools import wraps
from http import HTTPStatus
from typing import Any, Callable, List, Optional, Tuple

from sqlalchemy import func as sql_func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, joinedload

from onlyfilms import Session as SessionCreator
from onlyfilms.models import response_models
from onlyfilms.models.orm import Film, Review, Token, User


def orm_function(func: Callable[..., Any]):  # type: ignore
    @wraps(func)
    def wrapper(*args, **kwargs):  # type: ignore
        if kwargs.get('session') is None:
            with SessionCreator() as session:
                return func(*args, session=session, **kwargs)
        else:
            return func(*args, session=kwargs.get('session'), **kwargs)

    return wrapper


@orm_function
def get_film_by_id(
    film_id: int, session: Session = None
) -> Tuple[Film, float, int]:
    data = (
        session.query(
            Film, sql_func.avg(Review.score), sql_func.count(Review.id)
        )
        .filter(Film.id == film_id)
        .outerjoin(Film.reviews)
        .group_by(Film)
        .first()
    )

    return data


@orm_function
def get_films(
    query: str = "",
    offset: int = 0,
    limit: int = 10,
    min_rating: float = 0.0,
    session: Session = None,
) -> Tuple[List[Tuple[Film, float, int]], int]:

    query_filter = Film.title.ilike('%' + query + '%')
    offset_filter = Film.id > offset

    films = (
        session.query(
            Film, sql_func.avg(Review.score), sql_func.count(Review.id)
        )
        .filter(query_filter & offset_filter)
        .outerjoin(Film.reviews)
        .group_by(Film)
        .limit(limit)
        .all()
    )

    total = session.query(Film).filter(query_filter).count()

    return films, total


@orm_function
def get_reviews(
    film_id: int, limit: int = 3, offset: int = 0, session: Session = None
) -> Tuple[List[Review], int]:
    reviews = (
        session.query(Review)
        .options(joinedload(Review.author))
        .filter(Review.film_id == film_id)
        .order_by(Review.created)
        .offset(offset)
        .limit(limit)
        .all()
    )

    total = session.query(Review).filter(Review.film_id == film_id).count()

    return reviews, total


@orm_function
def get_film_score(film_id: int, session: Session = None) -> Optional[float]:
    score = (
        session.query(Review)
        .filter((Review.score.is_not(None)) & (Review.film_id == film_id))
        .with_entities(sql_func.avg(Review.score))
        .scalar()
    )
    return score if score is None else round(score, 1)


@orm_function
def get_user(user_id: int, session: Session = None) -> User:
    return session.query(User).filter(User.id == user_id).first()


def load_films(path: str) -> None:
    with open(path, 'r', encoding='utf-8') as file:
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
def login_user(
    login: str, password: str, session: Session = None
) -> Optional[str]:
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


@orm_function
def post_review(
    film_id: int,
    author: User,
    text: str,
    score: Optional[int] = None,
    session: Session = None,
) -> HTTPStatus:
    film = session.query(Film).filter(Film.id == film_id).first()
    if film is None:
        return HTTPStatus.NOT_FOUND

    new_review = Review(author, film, text)

    session.add(new_review)
    try:
        session.commit()
        return HTTPStatus.CREATED
    except SQLAlchemyError:
        session.rollback()
    return HTTPStatus.BAD_REQUEST


@orm_function
def get_review_by_id(
    review_id: int, film_id: int, session: Session = None
) -> Optional[response_models.ReviewModel]:
    review = (
        session.query(Review)
        .filter((Review.id == review_id) & (Review.film_id == film_id))
        .first()
    )
    if review is None:
        return None
    return response_models.ReviewModel.from_orm(review)


@orm_function
def delete_review(
    review_id: int, user: User, session: Session = None
) -> Optional[int]:
    review: Review = (
        session.query(Review)
        .filter(Review.id == review_id)
        .options(joinedload(Review.author))
        .first()
    )
    if review and review.author.id == user.id:
        try:
            session.delete(review)
            session.commit()
        except SQLAlchemyError:
            return None
        return review.id
    return None
