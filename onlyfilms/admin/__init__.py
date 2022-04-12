from flask_admin import Admin
from flask import Flask


def create_admin(app: Flask) -> Admin:
    from onlyfilms.admin.views import views

    admin = Admin(app)
    admin.add_views(*views)

    return admin
