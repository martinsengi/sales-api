FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    curl \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

RUN pip install pipenv

COPY Pipfile Pipfile.lock /app/
RUN pipenv install --dev --system --deploy

COPY . /app/

ENTRYPOINT ["/app/entrypoint.sh"]
