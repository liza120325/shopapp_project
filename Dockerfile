FROM python:3.12

WORKDIR /my_shopapp


RUN pip install 'poetry==2.4.1'
RUN poetry config virtualenvs.create false --local
COPY pyproject.toml poetry.lock README.md .

RUN poetry install --no-interaction --no-ansi --no-root --no-directory

COPY . .

CMD ["gunicorn", "mysite.wsgi:application", "--bind", "0.0.0.0:8000"]