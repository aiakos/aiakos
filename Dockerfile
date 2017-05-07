FROM python:3.6

WORKDIR /app
ENV PYTHONPATH /app
ENV DJANGO_SETTINGS_MODULE aiakos.settings

ADD requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

ADD . /app

RUN DJANGO_SECRET_KEY=x AIAKOS_HOSTNAME=x python -m aiakos collectstatic --noinput
CMD ["gunicorn", "-k", "gevent", "-b", "[::]:80", "aiakos.wsgi"]
EXPOSE 80
