FROM python:3.13-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    default-libmysqlclient-dev \
    pkg-config \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --shell /bin/bash django \
    && mkdir -p /app/staticfiles /app/media \
    && chown -R django:django /app

USER django

WORKDIR /app

COPY --chown=django:django requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=django:django . .

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PATH=/home/django/.local/bin:$PATH

EXPOSE 8000

CMD ["gunicorn", "config.asgi:application", "--bind", ":8000", "--workers", "2"]