FROM python:3.8-slim

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    PIPENV_HIDE_EMOJIS=true \
    PIPENV_COLORBLIND=true \
    PIPENV_NOSPIN=true \
    PIPENV_DOTENV_LOCATION=.env

RUN apt-get update && apt-get install -y curl python3-dev build-essential && rm -rf /var/lib/apt/lists/*
WORKDIR /code
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY . .

CMD ["uvicorn","main:app","--host","0.0.0.0","--port","5000","--root-path","/smartTimetable"]

