import json
from functools import wraps
from typing import Any, Callable, List, Optional
from http import HTTPStatus

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
def get_film_by_id(film_id: int, session: Session = None) -> Film:
    film = session.query(Film).filter(Film.id == film_id).first()
    return film


@orm_function
def get_films(
    query: Optional[str] = "",
    offset: int = 0,
    limit: int = 10,
    min_rating: float = 0.0,
    session: Session = None,
) -> List[Film]:

    query_filter = Film.title.ilike('%' + query + '%')
    offset_filter = Film.id > offset
    films = (
        session.query(Film)
        .filter(query_filter & offset_filter)
        .limit(limit)
        .all()
    )

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
def get_film_score(film_id: int, session: Session = None) -> Optional[float]:
    score = (
        session.query(Review)
        .filter((Review.score.is_not(None)) & (Review.film_id == film_id))
        .with_entities(sql_func.avg(Review.score))
        .scalar()
    )
    return score if score is None else round(score, 2)


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
def get_film_data(
    film_id: int, user_id: Optional[int] = None, session: Session = None
) -> response_models.FilmInfoModel:
    film: Film = session.query(Film).filter(Film.id == film_id).first()
    reviews: List[Review] = (
        session.query(Review)
        .filter(Review.film_id == film_id)
        .options(joinedload(Review.author))
        .all()
    )

    review_model_items = []
    score_sum = 0
    reviews_with_score = 0
    for review in reviews:
        review_model_items.append(response_models.ReviewModel.from_orm(review))

        if review.score is not None:
            score_sum += review.score
            reviews_with_score += 1

    score = None
    if reviews_with_score > 0:
        score = round(score_sum / reviews_with_score, 1)

    film_model = response_models.FilmModel.from_orm(film)
    return response_models.FilmInfoModel(
        film=film_model, reviews=review_model_items, score=score
    )


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
