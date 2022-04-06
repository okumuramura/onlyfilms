import uvicorn
from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware
from typer import Typer

from onlyfilms import Base, engine, logger
from onlyfilms.api import api
from onlyfilms.view import app as interface_app

args = Typer()


def create_app() -> FastAPI:
    app = FastAPI()
    app.include_router(api.router)
    app.mount('/onlyfilms/', WSGIMiddleware(interface_app.app))
    return app


@args.command(name='init')
def init_db() -> None:
    Base.metadata.create_all(engine)
    logger.info('Database is successfully initialized')


@args.command()
def start() -> None:
    app = create_app()
    uvicorn.run(app)


if __name__ == '__main__':
    args()
