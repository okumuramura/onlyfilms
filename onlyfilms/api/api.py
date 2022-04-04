from http import HTTPStatus

from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import IntegrityError

from onlyfilms import Session, logger
from onlyfilms.api import films
from onlyfilms.models.orm import Token, User
from onlyfilms.models.request_models import RegisterModel

router = APIRouter(prefix='/api')

router.include_router(films.router, prefix='/films')


@router.post('/register', status_code=HTTPStatus.ACCEPTED)
def register_handler(user_model: RegisterModel):
    new_user = User(user_model.login, user_model.password)

    with Session() as session:
        session.add(new_user)

        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            logger.warning('Can not add new user %s', repr(new_user))

            return HTTPException(status_code=HTTPStatus.NOT_ACCEPTABLE)


@router.post('/login', status_code=HTTPStatus.ACCEPTED)
def login_handler(user_model: RegisterModel):

    with Session() as session:
        user: User = (
            session.query(User).filter(User.login == user_model.login).first()
        )

        if user is None or not user.check_password(user_model.password):
            logger.warning('Wrong user or password for user %s', repr(user))
            return HTTPException(status_code=HTTPStatus.NOT_ACCEPTABLE)

        new_token = Token(user)

        session.add(new_token)
        session.commit()

        token = new_token.token

    return {'token': token}
