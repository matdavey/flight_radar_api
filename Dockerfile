FROM python:3.13.3-slim-bullseye

RUN addgroup --gid 10001 --system app && \
    adduser --shell /bin/false --disabled-password --uid 10001 --system --gid 10001 app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        netbase \
        tzdata \
        gcc \
        python3-dev \
    && \
    rm -rf /var/lib/apt/lists/* 

WORKDIR /app

COPY requirements.txt ./
RUN pip install -U setuptools && \
    pip install --no-cache-dir -r requirements.txt

COPY . .
RUN echo "${APP_VERSION}" > version.txt

USER app

EXPOSE 8006

CMD ["/app/flightradar-cli", "run"]