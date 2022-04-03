from pydantic import BaseModel


class AuthorizedUser(BaseModel):
    id: int


class RegisterModel(BaseModel):
    login: str
    password: str
