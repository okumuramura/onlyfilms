from flask import Flask, render_template

from onlyfilms import manager, logger
from onlyfilms.models.orm import User
from onlyfilms.view import authorized
from onlyfilms.admin import create_admin


app = Flask(__name__, static_url_path='/static')
create_admin(app)


@app.get('/')
@authorized
def index_page(user: User):
    films = manager.get_films()

    return render_template('index.html', films=films, authorized=user is not None, user=user)


@app.get('/film/<int:film_id>')
@authorized
def film_page(film_id: int, user: User):
    film = manager.get_film_by_id(film_id)
    reviews = manager.get_reviews(film_id, 5)
    logger.info('Info page of film: %s', film)

    return render_template('filmpage.html', authorized=user is not None, user=user, film=film, reviews=reviews)
