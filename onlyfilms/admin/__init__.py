from flask import Flask
from flask_admin import Admin


def create_admin(app: Flask) -> Admin:
    from onlyfilms.admin.views import views

    admin = Admin(app)
    admin.add_views(*views)

    return admin
