FROM python:3.10 AS builder

WORKDIR /app
ENV POETRY_CREATE_VIRTUALENVS false

RUN ["pip3", "install", "--user", "poetry"]
COPY ./pyproject.toml /app/pyproject.toml
COPY ./poetry.lock /app/poetry.lock
COPY ./k8slokilogs /app/k8slokilogs

RUN ["python3", "-m", "poetry", "install", "--only", "main"]

CMD ["python3", "-m", "poetry", "run", "app"]
