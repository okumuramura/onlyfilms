import secrets
from http import HTTPStatus
from typing import Any, Tuple

from flask import (
    Flask,
    Response,
    abort,
    make_response,
    redirect,
    render_template,
    request,
    url_for,
)

from onlyfilms import logger, manager
from onlyfilms.admin import create_admin
from onlyfilms.models import response_models
from onlyfilms.models.orm import User
from onlyfilms.view import authorized

app = Flask(__name__, static_url_path='/static')
app.config['SECRET_KEY'] = secrets.token_hex(16)

create_admin(app)


@app.get('/')
@authorized
def index_page(user: User) -> str:
    query = request.args.get('query', '')
    logger.info('Query: %s', query)
    films, _ = manager.get_films(query=query)
    film_models = []
    for film, score, evaluators in films:
        model = response_models.FilmModel.from_orm(film)
        model.score = score
        model.evaluators = evaluators
        film_models.append(model)

    return render_template(
        'index.html',
        films=film_models,
        authorized=user is not None,
        user=user,
        search_holder=(query if query else 'Search'),
    )


@app.get('/film/<int:film_id>')
@authorized
def film_page(film_id: int, user: User) -> str:
    film, score, evaluators = manager.get_film_by_id(film_id=film_id)
    if film is None:
        return abort(HTTPStatus.NOT_FOUND)

    reviews, _ = manager.get_reviews(film_id, 5)
    film_model = response_models.FilmModel.from_orm(film)
    film_model.score = score if score else 0.0
    film_model.evaluators = evaluators
    logger.info('Info page of film: %s', film)

    return render_template(
        'filmpage.html',
        authorized=user is not None,
        user=user,
        film=film_model,
        reviews=reviews,
    )


@app.post('/film/<int:film_id>/review')
@authorized
def film_review(film_id: int, user: User) -> Any:
    text = request.form.get('text')
    if manager.post_review(film_id, user, text)[0] == HTTPStatus.CREATED:
        logger.info('review for film %d with text %s created', film_id, text)
    else:
        logger.info('review creation filed')
    return redirect(url_for('.film_page', film_id=film_id))


@app.route('/register', methods=['GET', 'POST'])
def register_handler() -> Any:
    if request.method == 'GET':
        return render_template('register.html')

    login = request.form.get('login')
    password = request.form.get('password')

    logger.info('registration request with login: %s', login)
    if login and password:
        if manager.regster_user(login, password):
            token = manager.login_user(login, password)

            logger.info('new user registered: %s', login)
            logger.info('new token created: %s', token)

            response = make_response(
                redirect(url_for('.index_page'), HTTPStatus.FOUND)
            )
            response.set_cookie('token', token)

            return response

    logger.info('registration failed: <User %s>', login)
    return 'wrong data'


@app.route('/login', methods=['GET', 'POST'])
def login_handler() -> Any:
    if request.method == 'GET':
        return render_template('login.html')

    login = request.form.get('login')
    password = request.form.get('password')

    if login and password:
        token = manager.login_user(login, password)
        if not token:
            logger.info('sign in failed: <User %s>', login)
            return abort(HTTPStatus.CONFLICT)
        response = make_response(
            redirect(url_for('.index_page'), HTTPStatus.FOUND)
        )
        response.set_cookie('token', token)

        return response
    logger.info('sign in failed: <User %s>', login)
    return abort(HTTPStatus.CONFLICT)


@app.route('/logout', methods=['GET', 'POST'])
def logout_handler() -> Response:
    response = make_response(redirect(url_for('.index_page'), HTTPStatus.FOUND))
    response.set_cookie('token', '', expires=0)
    return response


@app.errorhandler(HTTPStatus.NOT_FOUND)
def not_found_error(_: Exception) -> Tuple[str, int]:
    return render_template('404.html'), HTTPStatus.NOT_FOUND
