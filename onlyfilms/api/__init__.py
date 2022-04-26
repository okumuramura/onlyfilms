from http import HTTPStatus
from typing import Optional

from fastapi import Header, HTTPException

from onlyfilms import Session
from onlyfilms.models.orm import Token, User


def authorized(authorization: Optional[str] = Header(None)) -> User:
    if not authorization:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Authorization requied'
        )

    with Session() as session:
        token: Token = (
            session.query(Token).filter(Token.token == authorization).first()
        )

        if token is None:
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN, detail='Authorization faild'
            )

        user = token.user

    return user
