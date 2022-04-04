from http import HTTPStatus
from typing import Optional

from fastapi import APIRouter, Depends, Query, Request

from onlyfilms import logger
from onlyfilms.api import authorized
from onlyfilms.models.orm import User
from onlyfilms.models.response_models import FilmModel, FilmsListModel

router = APIRouter()


@router.get('/', status_code=HTTPStatus.OK, response_model=FilmsListModel)
def main_handler(
    request: Request,
    query: Optional[str] = Query(None, alias='q'),
    offset: int = 0,
):
    return FilmsListModel(
        films=[FilmModel(id=1, title='Star Wars', rating='9.31')],
        total=1,
        offset=0,
    )


@router.post('/{film_id}/rate')
def rate_handler(
    request: Request, film_id: int, user: User = Depends(authorized)
):
    logger.info(
        'User %s with id %d rate film with id %d: 0.0',
        user.login,
        user.id,
        film_id,
    )
    return {'status': 'ok', 'user': user}


@router.post('/{film_id}/review')
def review_handler(
    request: Request, film_id: int, user: User = Depends(authorized)
):
    logger.info(
        'User %s with id %d left a review to film with id %d: %s',
        user.login,
        user.id,
        film_id,
        '...',
    )
    return {'status': 'ok', 'user': user}


@router.post('/{film_id}/review/{review_id}')
def review_info_handler(request: Request, film_id: int, review_id: int):
    return {'status': 'ok'}


@router.get('/{film_id}/reviews')
def reviews_list_handler(request: Request, film_id: int, offset: int = 0):
    return {'status': 'ok'}


@router.get('/{film_id}')
def film_info_handler(request: Request, film_id: int):
    return {'status': 'ok'}
