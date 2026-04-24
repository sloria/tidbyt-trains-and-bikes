##### Python base #####
FROM python:3.14.4-slim-trixie@sha256:c11aee3b3cae066f55d1e9318fc812673aa6557073b0db0d792b59491b262e0c AS python-base

RUN apt-get update \
  && apt-get upgrade -y \
  && apt-get install -y --no-install-recommends tini \
  && apt-get autoremove -y \
  && apt-get clean -y \
  && rm -rf /root/.cache \
  && rm -rf /var/apt/lists/* \
  && rm -rf /var/cache/apt/* \
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && mkdir -p /workspace/app

COPY --from=ghcr.io/astral-sh/uv:latest@sha256:240fb85ab0f263ef12f492d8476aa3a2e4e1e333f7d67fbdd923d00a506a516a /uv /uvx /bin/

##### Python build base #####
FROM python-base AS builder

ENV UV_LINK_MODE=copy \
  UV_NO_CACHE=1 \
  UV_COMPILE_BYTECODE=1 \
  UV_SYSTEM_PYTHON=1 \
  PATH="/workspace/app/.venv/bin:/usr/local/bin:$PATH" \
  PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONFAULTHANDLER=1 \
  PYTHONHASHSEED=random \
  LANG=C.UTF-8 \
  LC_ALL=C.UTF-8

# Add build packages

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    git \
    build-essential \
    gcc \
  && apt-get autoremove -y \
  && apt-get clean -y \
  && rm -rf /root/.cache \
  && rm -rf /var/apt/lists/* \
  && rm -rf /var/cache/apt/* \
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false

# Install application

WORKDIR /workspace/app
COPY pyproject.toml uv.lock application.py ./
COPY src/ ./src/

RUN uv venv \
  && uv sync --no-dev --frozen --no-install-project --no-editable \
  && uv export --no-dev --frozen --no-hashes --output-file=requirements.txt \
  && uv sync --no-dev --frozen --no-editable \
  && uv build

##### Run image ######

FROM python-base AS runner

ENV PATH="/workspace/app/.venv/bin:/usr/local/bin:$PATH" \
  UV_LINK_MODE=copy \
  UV_NO_CACHE=1 \
  UV_COMPILE_BYTECODE=1 \
  UV_SYSTEM_PYTHON=1 \
  PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONFAULTHANDLER=1 \
  PYTHONHASHSEED=random \
  LANG=C.UTF-8 \
  LC_ALL=C.UTF-8 \
  LITESTAR_APP="app.api.app:app"

# Need curl for pixlet installation
# Need git for installing my fork of gtfs-realtime-bindings
RUN apt-get update \
  && apt-get install -y --no-install-recommends curl git \
  && apt-get autoremove -y \
  && apt-get clean -y \
  && rm -rf /root/.cache \
  && rm -rf /var/apt/lists/* \
  && rm -rf /var/cache/apt/* \
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false

# Install pixlet
RUN curl -LO https://github.com/tidbyt/pixlet/releases/download/v0.34.0/pixlet_0.34.0_linux_amd64.tar.gz && \
  tar -xvf pixlet_0.34.0_linux_amd64.tar.gz && \
  chmod +x pixlet && \
  mv pixlet /usr/local/bin && \
  rm pixlet_0.34.0_linux_amd64.tar.gz

# Create non-root user
RUN addgroup --system --gid 65532 nonroot \
  && adduser --no-create-home --system --uid 65532 nonroot \
  && chown -R nonroot:nonroot /workspace

COPY --from=builder --chown=65532:65532 /workspace/app/dist /tmp/

WORKDIR /workspace/app

# Install built application

RUN uv pip install --quiet --disable-pip-version-check /tmp/*.whl \
  && rm -Rf /tmp/*

# Run the application
USER nonroot
EXPOSE 8000
ENTRYPOINT ["tini", "--"]
CMD ["litestar", "run", "--port", "8000", "--host", "0.0.0.0"]
