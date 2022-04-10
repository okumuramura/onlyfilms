from flask_admin.contrib.sqla import ModelView

from onlyfilms.models.orm import User, Film, Token, Review
from onlyfilms.admin import admin_session


class UserModel(ModelView):
    column_exclude_list = ['password']


views = [
    UserModel(User, admin_session),
    ModelView(Film, admin_session),
    ModelView(Token, admin_session),
    ModelView(Review, admin_session)
]
