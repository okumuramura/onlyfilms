from pydantic import BaseModel


class RegisterModel(BaseModel):
    login: str
    password: str


class ReviewModel(BaseModel):
    text: str
