FROM python:2.7.10
ADD requirements.txt /

RUN pip  install -r requirements.txt

ENV APP_DIR /app
ENV APP_NAME discovery_service
ENV PORT 5004

ADD src $APP_DIR

EXPOSE $PORT

WORKDIR $APP_DIR

CMD gunicorn $APP_NAME:app --bind 0.0.0.0:$PORT