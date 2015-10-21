FROM python:2.7.10
ADD requirements.txt /

RUN pip  install -r requirements.txt

ENV APP_DIR /app
ENV APP_NAME runserver
ENV PORT 5001

ADD src $APP_DIR/

EXPOSE $PORT

WORKDIR $APP_DIR

CMD gunicorn $APP_NAME:app --bind 0.0.0.0:$PORT