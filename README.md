# Onlyfilms

Film evaluation and review service. Contains api, web application and admin panel. Uses FastApi (API), Flask (web), sqlalchemy (ORM).

## Installation
```bash
python -m pip install poetry
poetry install
```

## Launch
```
poetry shell
python -m onlyfilms start
# or
make up
```

## Docker
Onlyfilms has docker image.
```bash
docker build -t onlyfilms .
docker run -dp 8000:8000 onlyfilms
```

## Documentation
You can view available requests at `http://127.0.0.1:8000/docs`.

## Services
API: `http://127.0.0.1:8000/api`  
Web app: `http://127.0.0.1:8000/onlyfilms`  
Admin: `http://127.0.0.1:8000/onlyfilms/admin`