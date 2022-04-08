from flask import Flask, render_template

from onlyfilms import manager, logger


app = Flask(__name__, static_url_path='/static')


@app.get('/')
def index_page():
    films = manager.get_films()

    return render_template('index.html', films=films)


@app.get('/film/<int:film_id>')
def film_page(film_id: int):
    film = manager.get_film_by_id(film_id)
    reviews = manager.get_reviews(film_id, 5)
    logger.info('Info page of film: %s', film)

    return render_template('filmpage.html', film=film, reviews=reviews)
