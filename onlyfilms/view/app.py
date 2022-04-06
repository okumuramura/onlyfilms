from flask import Flask, render_template

from onlyfilms import manager


app = Flask(__name__, static_url_path='/static')


@app.get('/')
def index_page():
    films = manager.get_films()

    return render_template(
        'index.html',
        films=films
    )


@app.get('/film/{film_id}')
def film_page():
    return 'film page'
