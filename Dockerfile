FROM python:3.7-slim

RUN useradd -ms /bin/bash messenger

WORKDIR /home/messenger

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn

COPY app app
COPY migrations migrations
COPY messenger.py config.py boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP messenger.py
ENV SECRET_KEY 'fake_secret_key_for_github'
ENV DATABASE_URL postgresql://user:password@postgres:5432/messenger

RUN chown -R messenger:messenger ./
USER messenger

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
