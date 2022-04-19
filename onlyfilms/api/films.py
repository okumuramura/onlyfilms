from http import HTTPStatus
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.exc import SQLAlchemyError

from onlyfilms import Session, logger, manager
from onlyfilms.api import authorized
from onlyfilms.models import response_models
from onlyfilms.models.orm import Film, Review, User
from onlyfilms.models.request_models import ReviewModel

router = APIRouter()


@router.get('/', status_code=HTTPStatus.OK)
def main_handler(
    request: Request,
    query: Optional[str] = Query(None, alias='q'),
    offset: int = 0,
    limit: int = 10,
):

    films = manager.get_films()

    return {'films': films, 'total': len(films), 'offset': 0}


@router.post('/{film_id}/review')
def review_handler(
    film_id: int, review: ReviewModel, user: User = Depends(authorized)
):
    with Session() as session:
        film: Film = session.query(Film).filter(Film.id == film_id).first()

        if film is None:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND, detail='film not found'
            )

        new_review = Review(user, film, review.text)
        if review.score is not None:
            film.rate(review.score)

        session.add(new_review)

        try:
            session.commit()
        except SQLAlchemyError as error:
            session.rollback()
            logger.error(
                'SQLAlchemy error while reviewing film %s: %s', film, error
            )
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR)

    # logger.info(
    #     'User %s with id %d left a review to film with id %d: %s',
    #     user.login,
    #     user.id,
    #     film_id,
    #     review.text,
    # )
    return {'status': 'ok', 'user': user}


@router.post('/{film_id}/review/{review_id}')
def review_info_handler(film_id: int, review_id: int):
    return {'status': 'ok'}


@router.get('/{film_id}/reviews')
def reviews_list_handler(film_id: int, offset: int = 0, limit: int = 10):
    with Session() as session:
        reviews: List[Review] = (
            session.query(Review)
            .filter(Review.film_id == film_id)
            .offset(offset)
            .limit(limit)
            .all()
        )

    return {'reviews': reviews}


@router.get('/{film_id}', response_model=response_models.FilmInfoModel)
def film_info_handler(film_id: int) -> response_models.FilmInfoModel:
    film = manager.get_film_data(film_id)
    return film
