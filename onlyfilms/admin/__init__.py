from flask import Flask
from flask_admin import Admin

from onlyfilms.admin.views import views


def create_admin(app: Flask) -> Admin:

    admin = Admin(app)
    admin.add_views(*views)

    return admin
