FROM python:3.12-alpine

WORKDIR /my_shopapp

COPY ./requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .


CMD ["gunicorn", "mysite.wsgi:application", "--bind", "0.0.0.0:8000"]