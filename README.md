# Onlyfilms

Film evaluation and review service. Contains api, web application and admin panel.  
Uses:
- FastApi (API)
- Flask (web)
- sqlalchemy (ORM).

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

## Examples

`http://127.0.0.1:8000/api/films?q=ar&limit=5`
```json
{
    "films": [
        {
            "id": 4,
            "title": "Scareface",
            "director": "Brian De Palma",
            "description": "In 1980 Miami, a determined Cuban immigrant takes over a drug cartel and succumbs to greed.",
            "cover": "https://cdn.shopify.com/s/files/1/0057/3728/3618/products/6903bbd6751911b93b452e593864d724_d115656c-fe9b-42dd-85fd-3e86e283822c_500x749.jpg?v=1573585334",
            "score": null,
            "evaluators": 0
        },
        {
            "id": 6,
            "title": "Arcane",
            "director": "Ash Brannon",
            "description": "Set in utopian Piltover and the oppressed underground of Zaun, the story follows the origins of two iconic League champions-and the power that will tear them apart.",
            "cover": "https://cdn.shopify.com/s/files/1/0057/3728/3618/products/54409_480x.progressive.jpg?v=1642690615",
            "score": 9.5,
            "evaluators": 2
        }
    ],
    "total": 2,
    "offset": 0
}
```
---
`http://127.0.0.1:8000/api/films/6/reviews?limit=1`
```json
{
    "reviews": [
        {
            "id": 1,
            "film_id": 6,
            "created": "2022-04-15T10:44:55.241815",
            "text": "good film!",
            "score": 9,
            "author": {
                "id": 2,
                "login": "okumuramura"
            }
        }
    ],
    "total": 2,
    "offset": 0
}
```