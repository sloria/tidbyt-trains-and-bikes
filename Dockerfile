##### Python base #####
FROM python:3.15.2-slim-trixie@sha256:c4158543ecb725b99e57d129dfd43d761d4c43e4577b5e23326aabb223cf7f4e AS python-base

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

COPY --from=ghcr.io/astral-sh/uv:latest@sha256:af22a52f5eafef3d78e551599d405c02df61919d18028f0cea8eda93bc9986d0 /uv /uvx /bin/

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
COPY pyproject.toml uv.lock ./
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
  LC_ALL=C.UTF-8

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
ENTRYPOINT ["tini", "--"]
CMD ["trains-and-bikes"]
