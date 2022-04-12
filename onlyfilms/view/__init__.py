from typing import Callable, Any
from functools import wraps

from flask import request

from onlyfilms import Session
from onlyfilms.models.orm import Token


def authorized(func: Callable[..., Any]):  # type: ignore
    @wraps(func)
    def wrapper(*args, **kwargs):  # type: ignore
        token = request.headers.get('Authorization', None)
        if not token:
            token = request.cookies.get('token', None)
        user = None

        with Session() as session:
            real_token: Token = (
                session.query(Token).filter(Token.token == token).first()
            )

            if real_token:
                user = real_token.user

        return func(*args, user=user, **kwargs)

    return wrapper
