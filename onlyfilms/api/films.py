from http import HTTPStatus
from typing import Optional

from fastapi import APIRouter, Depends, Query, Request, HTTPException
from sqlalchemy.exc import SQLAlchemyError

from onlyfilms import logger, Session
from onlyfilms.api import authorized
from onlyfilms.models.orm import User, Film, Review
from onlyfilms.models.request_models import ReviewModel, RatingModel

router = APIRouter()


@router.get('/', status_code=HTTPStatus.OK)
def main_handler(
    request: Request,
    query: Optional[str] = Query(None, alias='q'),
    offset: int = 0,
):

    with Session() as session:
        films = session.query(Film).all()

    return {'films': films, 'total': len(films), 'offset': 0}


@router.post('/{film_id}/rate')
def rate_handler(
    film_id: int, rating: RatingModel, user: User = Depends(authorized)
):
    with Session() as session:
        film: Film = session.query(Film).filter(Film.id == film_id).first()
        if film is None:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND, detail='Film not found'
            )

        film.rate(rating.score)

        try:
            session.commit()
        except SQLAlchemyError as error:
            logger.error(
                'SQLAlchemy error while rating film %s: %s', film, error
            )
            session.rollback()
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR)

    logger.info(
        'User %s with id %d rate film with id %d: 0.0',
        user.login,
        user.id,
        film_id,
    )
    return {'status': 'ok', 'user': user}


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

    logger.info(
        'User %s with id %d left a review to film with id %d: %s',
        user.login,
        user.id,
        film_id,
        review.text,
    )
    return {'status': 'ok', 'user': user}


@router.post('/{film_id}/review/{review_id}')
def review_info_handler(film_id: int, review_id: int):
    return {'status': 'ok'}


@router.get('/{film_id}/reviews')
def reviews_list_handler(film_id: int, offset: int = 0):
    return {'status': 'ok'}


@router.get('/{film_id}')
def film_info_handler(film_id: int):
    return {'status': 'ok'}
