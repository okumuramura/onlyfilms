from http import HTTPStatus

from fastapi import APIRouter, HTTPException

from onlyfilms import logger, manager
from onlyfilms.api import films
from onlyfilms.models.request_models import RegisterModel

router = APIRouter(prefix='/api')

router.include_router(films.router, prefix='/films')


@router.post('/register', status_code=HTTPStatus.ACCEPTED)
def register_handler(user_model: RegisterModel):
    if not manager.regster_user(user_model.login, user_model.password):
        logger.warning('Can not add new user %s', user_model.login)
        raise HTTPException(status_code=HTTPStatus.NOT_ACCEPTABLE)

    logger.info('User with login %s registered succsessfully', user_model.login)
    return HTTPStatus.CREATED


@router.post('/login', status_code=HTTPStatus.ACCEPTED)
def login_handler(user_model: RegisterModel):

    token = manager.login_user(user_model.login, user_model.password)

    if not token:
        logger.warning('Wrong user or password for user %s', user_model.login)
        raise HTTPException(status_code=HTTPStatus.NOT_ACCEPTABLE)

    logger.info(
        'User with login %s logged in successfully, token: %s',
        user_model.login,
        token,
    )

    return {'token': token}
