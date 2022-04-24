from flask_admin.contrib.sqla import ModelView

from onlyfilms import Session
from onlyfilms.models.orm import Film, Review, Token, User

admin_session = Session()


class UserView(ModelView):
    column_exclude_list = ['password']


views = [
    UserView(User, admin_session),
    ModelView(Film, admin_session),
    ModelView(Token, admin_session),
    ModelView(Review, admin_session),
]
