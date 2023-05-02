FROM python:3.10 AS builder

WORKDIR /app
ENV POETRY_CREATE_VIRTUALENVS false

RUN ["pip3", "install", "--user", "poetry"]
COPY ./pyproject.toml /app/pyproject.toml
COPY ./k8slokilogs /app/k8slokilogs

RUN ["poetry", "install"]

CMD ["poetry", "run", "app"]
