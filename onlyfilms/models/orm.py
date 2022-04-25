from __future__ import annotations

import datetime
from typing import List, Optional
from uuid import uuid4

import bcrypt
from sqlalchemy import (
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from onlyfilms import Base


class User(Base):
    __tablename__ = 'users'

    id: int = Column(Integer, primary_key=True)
    login: str = Column(String(25), nullable=False, unique=True)
    password: bytes = Column(String(128), nullable=False)
    register_date: datetime.datetime = Column(Date, nullable=False)

    tokens: List[Token] = relationship('Token', back_populates='user')
    reviews: List[Review] = relationship('Review', back_populates='author')

    def __init__(self, login: str, password: str) -> None:
        self.login = login
        self.password = bcrypt.hashpw(
            password.encode('utf-8'), bcrypt.gensalt(10)
        )
        self.register_date = datetime.datetime.now()

    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), self.password)

    def __repr__(self) -> str:
        return f'<User {self.login}>'


class Token(Base):
    __tablename__ = 'tokens'
    EXPIRE = datetime.timedelta(hours=12)

    id: int = Column(Integer, primary_key=True)
    user_id: int = Column(Integer, ForeignKey('users.id'))
    created: datetime.datetime = Column(DateTime, nullable=False)
    token: str = Column(String(128), unique=True)

    user: User = relationship('User', back_populates='tokens')

    def __init__(self, user: User) -> None:
        self.user = user
        self.token = str(uuid4())
        self.created = datetime.datetime.now()

    def is_expired(self) -> bool:
        delta = datetime.datetime.now() - self.created
        return delta >= self.EXPIRE

    def __repr__(self) -> str:
        return f'<Token {self.user}, {self.token}>'


class Review(Base):
    __tablename__ = 'reviews'

    id: int = Column(Integer, primary_key=True)
    author_id: int = Column(Integer, ForeignKey('users.id'))
    film_id: int = Column(Integer, ForeignKey('films.id'))
    created: datetime.datetime = Column(DateTime, nullable=False)
    text: Optional[str] = Column(Text(2000), nullable=True, default=None)
    score: Optional[int] = Column(Integer, nullable=True, default=None)

    author: User = relationship('User', back_populates='reviews')
    film: Film = relationship('Film', back_populates='reviews')

    __table_args__ = (
        UniqueConstraint('author_id', 'film_id', name='_user_review_unique'),
    )

    def __init__(
        self, author: User, film: Film, text: str, score: Optional[int] = None
    ) -> None:
        self.film = film
        self.author = author
        self.text = text
        self.created = datetime.datetime.now()
        self.score = score

    def __repr__(self) -> str:
        return (
            f'<Review {self.text[:30] if self.text else None}..., {self.score}>'
        )


class Film(Base):
    __tablename__ = 'films'

    id: int = Column(Integer, primary_key=True)
    title: str = Column(String(120), nullable=False)
    director: Optional[str] = Column(String(50), nullable=True, default=None)
    description: Optional[str] = Column(Text(2000), nullable=True, default=None)
    cover: Optional[str] = Column(String(500), nullable=True, default=None)

    reviews: List[Review] = relationship('Review', back_populates='film')

    def __init__(
        self,
        title: str,
        director: Optional[str] = None,
        cover: Optional[str] = None,
    ) -> None:
        self.title = title
        self.director = director
        self.cover = cover

    def __repr__(self) -> str:
        return f'<Film {self.title}>'
