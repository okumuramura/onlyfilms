from http import HTTPStatus
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from onlyfilms import logger, manager
from onlyfilms.api import authorized
from onlyfilms.models import response_models
from onlyfilms.models.orm import User
from onlyfilms.models.request_models import ReviewModel

router = APIRouter()


@router.get(
    '/', response_model=response_models.Films, status_code=HTTPStatus.OK
)
def main_handler(
    query: Optional[str] = Query('', alias='q', max_length=200),
    offset: int = Query(0, ge=0),
    limit: int = Query(10, le=50),
):

    films = manager.get_films(query, offset, limit)
    films_models = []
    for film, score, evaluators in films:
        model = response_models.FilmModel.from_orm(film)
        model.score = score
        model.evaluators = evaluators
        films_models.append(model)
    return response_models.Films(
        films=films_models, total=len(films), offset=offset
    )


@router.post('/{film_id}/review', status_code=HTTPStatus.CREATED)
def review_handler(
    film_id: int, review: ReviewModel, user: User = Depends(authorized)
):
    status = manager.post_review(film_id, user, review.text, review.score)

    if status == HTTPStatus.CREATED:
        raise HTTPException(status_code=status)

    logger.info(
        'User %s with id %d left a review to film with id %d: %s',
        user.login,
        user.id,
        film_id,
        review.text,
    )


@router.get(
    '/{film_id}/reviews/{review_id}',
    response_model=response_models.ReviewModel,
    status_code=HTTPStatus.OK,
)
def review_info_handler(film_id: int, review_id: int):
    review = manager.get_review_by_id(review_id, film_id)
    if review is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND)
    return review


@router.get(
    '/{film_id}/reviews',
    response_model=response_models.Reviews,
    status_code=HTTPStatus.OK,
)
def reviews_list_handler(film_id: int, offset: int = 0, limit: int = 10):
    reviews = manager.get_reviews(film_id, limit, offset)

    reviews_models = [response_models.ReviewModel.from_orm(x) for x in reviews]

    return response_models.Reviews(
        movie='?', reviews=reviews_models, total=len(reviews), offset=offset
    )


@router.get(
    '/{film_id}',
    response_model=response_models.FilmModel,
    status_code=HTTPStatus.OK,
)
def film_info_handler(film_id: int) -> response_models.FilmModel:
    film, score, evaluators = manager.get_film_by_id(film_id)
    model = response_models.FilmModel.from_orm(film)
    model.score = round(score, 1)
    model.evaluators = evaluators
    return model


@router.delete('/{film_id}/reviews/{review_id}', status_code=HTTPStatus.OK)
def delete_review_handler(review_id: int, user: User = Depends(authorized)):
    deleted = manager.delete_review(review_id, user)
    if not deleted:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN)

    logger.info('deleted review: %d', deleted)
