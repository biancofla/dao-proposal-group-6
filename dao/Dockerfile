FROM python:3

ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY poetry.lock pyproject.toml /app/

RUN pip3 install poetry
RUN poetry install --no-root

COPY . .

ENV DJANGO_SETTINGS_MODULE "dao.settings"
ENV DJANGO_SECRET_KEY "django-insecure-u_t@0p#g^1p^jj020ek#!vquln=6p#bi6j6+7@n+g@#hz0c$da"

RUN poetry run python manage.py collectstatic --noinput

CMD poetry run daphne -b 0.0.0.0 -p 8080 dao.asgi:application