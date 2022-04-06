from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import uuid4

import bcrypt
from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from onlyfilms import Base


class User(Base):
    __tablename__ = 'users'

    id: int = Column(Integer, primary_key=True)
    login: str = Column(String(20), nullable=False, unique=True)
    password: bytes = Column(String(128), nullable=False)
    register_date: datetime = Column(Date, nullable=False)

    tokens: List[Token] = relationship('Token', back_populates='user')
    reviews: List[Review] = relationship('Review', back_populates='author')

    def __init__(self, login: str, password: str) -> None:
        self.login = login
        self.password = bcrypt.hashpw(
            password.encode('utf-8'), bcrypt.gensalt(10)
        )
        self.register_date = datetime.now().date()

    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), self.password)

    def __repr__(self) -> str:
        return f'User_{self.id}<{self.login}, {self.password}>'


class Token(Base):
    __tablename__ = 'tokens'

    id: int = Column(Integer, primary_key=True)
    user_id: int = Column(Integer, ForeignKey('users.id'))
    created: datetime = Column(DateTime, nullable=False)
    token: str = Column(String(128), unique=True)

    user: User = relationship('User', back_populates='tokens')

    def __init__(self, user: User) -> None:
        self.user = user
        self.token = str(uuid4())
        self.created = datetime.now()

    def __repr__(self) -> str:
        return f'Token_{self.id}<{self.user_id}>'


class Review(Base):
    __tablename__ = 'reviews'

    id: int = Column(Integer, primary_key=True)
    author_id: int = Column(Integer, ForeignKey('users.id'))
    film_id: int = Column(Integer, ForeignKey('films.id'))
    created: datetime = Column(DateTime, nullable=False)
    text: str = Column(Text(2000), nullable=False)

    author: User = relationship('User', back_populates='reviews')
    film: Film = relationship('Film', back_populates='reviews')

    def __init__(self, author: User, film: Film, text: str) -> None:
        self.film = film
        self.author = author
        self.text = text

    def __repr__(self) -> str:
        return f'Review_{self.id}<{self.author_id}, {self.text[:30]}...>'


class Film(Base):
    __tablename__ = 'films'

    id: int = Column(Integer, primary_key=True)
    title: str = Column(String(120), nullable=False)
    director: str = Column(String(50), nullable=True, default=None)
    description: str = Column(Text(2000), nullable=True, default=None)
    score: str = Column(String(4), nullable=True, default=None)
    evaluators: int = Column(Integer, nullable=False, default=0)
    cover: str = Column(String(256), nullable=True, default=None)

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
        return f'Film_{self.id}<{self.title}, {self.director}, {self.cover}>'
