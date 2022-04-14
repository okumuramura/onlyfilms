from http import HTTPStatus

from flask import (
    Flask,
    render_template,
    request,
    make_response,
    redirect,
    url_for,
    abort,
)

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

    return render_template(
        'index.html', films=films, authorized=user is not None, user=user
    )


@app.get('/film/<int:film_id>')
@authorized
def film_page(film_id: int, user: User):
    film = manager.get_film_by_id(film_id=film_id)
    if film is None:
        return abort(HTTPStatus.NOT_FOUND)

    reviews = manager.get_reviews(film_id, 5)
    logger.info('Info page of film: %s', film)

    return render_template(
        'filmpage.html',
        authorized=user is not None,
        user=user,
        film=film,
        reviews=reviews,
    )


@app.post('/film/<int:film_id>/review')
@authorized
def film_review(film_id: int, user: User):
    text = request.form.get('text')
    if manager.create_review(film_id, user, text):
        logger.info('review for film %d with text %s created', film_id, text)
    else:
        logger.info('review creation filed')
    return redirect(url_for('.film_page', film_id=film_id))


@app.route('/register', methods=['GET', 'POST'])
def register_handler():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        login = request.form.get('login')
        password = request.form.get('password')

        logger.info('registration request with login: %s', login)
        if login and password:
            if manager.regster_user(login, password):
                token = manager.login_user(login, password)

                logger.info('new user registered: %s', login)
                logger.info('new token created: %s', token)

                response = make_response(redirect(url_for('.index_page'), 302))
                response.set_cookie('token', token)

                return response

        logger.info('registration failed: <User %s>', login)
        return 'wrong data'


@app.route('/login', methods=['GET', 'POST'])
def login_handler():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        login = request.form.get('login')
        password = request.form.get('password')

        if login and password:
            token = manager.login_user(login, password)
            response = make_response(redirect(url_for('.index_page'), 302))
            response.set_cookie('token', token)

            return response
    logger.info('sign in failed: <User %s>', login)
    return 'wrong data'


@app.route('/logout', methods=['GET', 'POST'])
def logout_handler():
    response = make_response(redirect(url_for('.index_page'), 302))
    response.set_cookie('token', '', expires=0)
    return response


@app.errorhandler(HTTPStatus.NOT_FOUND)
def not_found_error(_: Exception):
    return render_template('404.html'), HTTPStatus.NOT_FOUND
