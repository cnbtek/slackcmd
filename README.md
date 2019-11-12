1. use `gunicorn` to run the application on prod
1. install using `pip install gunicorn`
1. run using `gunicorn --bind 0.0.0.0:5000 wsgi:app`
1. for adding a new yard add it to `config.py`

