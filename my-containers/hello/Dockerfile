FROM python:3.8-slim-buster

# create non privileged user
ARG APP_USER=appuser
RUN useradd --create-home ${APP_USER}

# use root for privileged operations, switch user later
USER root

# install apt packages
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# upgrade pip to latest version
RUN pip install --upgrade pip

# install poetry package manager
ENV POETRY_VIRTUALENVS_CREATE=false \
    POETRY_HOME=/poetry \
    POETRY_VERSION=1.1.13
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="${POETRY_HOME}/bin:${PATH}"
RUN poetry --version

# switch workdir
WORKDIR /home/${APP_USER}/app
# copy config files
COPY pyproject.toml poetry.lock ./
# install only dependencies
RUN poetry install --no-dev --no-root

# copy source code and install root package
COPY src src
RUN poetry install --no-dev

# switch to non privileged user before running app
USER ${APP_USER}

# expose port
EXPOSE 9000
# run app
ENTRYPOINT ["uvicorn", "hello.main:app"]
CMD ["--host", "0.0.0.0", "--port", "9000"]
