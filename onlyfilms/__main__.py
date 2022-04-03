from typer import Typer
from fastapi import FastAPI
import uvicorn

from onlyfilms import Base, engine
from onlyfilms.api import api

args = Typer()


def create_app() -> FastAPI:
    app = FastAPI()
    app.include_router(api.router)

    return app


@args.command(name='init')
def init_db() -> None:
    Base.metadata.create_all(engine)


@args.command()
def start() -> None:
    app = create_app()
    uvicorn.run(app)


if __name__ == '__main__':
    args()
