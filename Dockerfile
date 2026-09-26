FROM python:3.13-slim
RUN apt-get update && apt-get install -y --no-install-recommends curl poppler-utils build-essential && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.lock.txt ./
RUN python -m venv /app/.venv && /app/.venv/bin/pip install --no-cache-dir --require-hashes -r requirements.lock.txt
COPY pyproject.toml ./
COPY src ./src
RUN /app/.venv/bin/pip install --no-deps .
COPY config ./config
COPY dbt ./dbt
RUN mkdir -p data reports && chown 1000:1000 /app/data /app/reports
USER 1000:1000
ENV PATH="/app/.venv/bin:$PATH"
ENTRYPOINT ["trayectorias", "run", "--root", "/app"]
