from flask_admin.contrib.sqla import ModelView

from onlyfilms import Session
from onlyfilms.models.orm import User, Film, Token, Review

admin_session = Session()


class UserModel(ModelView):
    column_exclude_list = ['password']


views = [
    UserModel(User, admin_session),
    ModelView(Film, admin_session),
    ModelView(Token, admin_session),
    ModelView(Review, admin_session),
]
