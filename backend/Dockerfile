FROM python:3.12-slim-bullseye

RUN pip install poetry

RUN mkdir /app
WORKDIR /app

COPY pyproject.toml /app

RUN poetry install --no-root

COPY . /app

RUN poetry install

CMD ["poetry", "run", "fastapi", "dev", "--host", "0.0.0.0", "main.py"]
