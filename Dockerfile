FROM python:3.9-slim as builder

ARG user=app_user
ARG group=${user}
ARG uid=1010
ARG gid=1010

ARG APP_DIR=/app

# install app
ENV POETRY_HOME="/.poetry" \
    POETRY_CACHE_DIR=/tmp/poetry_cache \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN apt-get -y -q update && \
    apt-get -y -q install --no-install-recommends curl && \
    curl -sSL https://install.python-poetry.org | python - --version 1.3.2

ENV PATH="${POETRY_HOME}/bin:${PATH}"
ENV PATH="${APP_DIR}/.venv/bin:${PATH}"

WORKDIR $APP_DIR
COPY pyproject.toml poetry.lock ./
RUN find . | grep -E "(__pycache__|\.pyc$)" | xargs rm -rf
RUN poetry install --with app --without dev --no-root --no-interaction && rm -rf $POETRY_CACHE_DIR

FROM python:3.9-slim as runtime

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH" \
    PROJECT_ID="playground-351113"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

COPY src src

ENV PORT 80

ENTRYPOINT [ "python", "-m", "streamlit", "run", "src/app.py", "--server.port=80", "--server.address=0.0.0.0", "--theme.primaryColor=#135aaf"]