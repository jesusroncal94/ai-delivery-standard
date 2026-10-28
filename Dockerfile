FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/* \
    && git config --system --add safe.directory '*' \
    && git config --system user.name "ai-delivery-standard" \
    && git config --system user.email "ai-delivery-standard@localhost"

WORKDIR /opt/ads
COPY checker/ checker/
RUN pip install --no-cache-dir "copier==9.4.1" "pytest==8.3.3" ./checker

WORKDIR /work
ENTRYPOINT ["ads"]
