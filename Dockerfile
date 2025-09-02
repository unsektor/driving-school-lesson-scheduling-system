FROM python:3.9 AS web-app

RUN apt update && apt-get install -y uwsgi uwsgi-plugin-python3
COPY requirements.lock .
RUN python3 -m pip install -r requirements.lock

ENTRYPOINT ["uwsgi", "--ini", "/usr/local/etc/uwsgi/app.ini"]
