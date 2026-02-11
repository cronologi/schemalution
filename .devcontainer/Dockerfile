FROM mcr.microsoft.com/devcontainers/python:3.10

# System dependencies for dev tooling, Graphviz rendering, and optional Spark usage.
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    git \
    make \
    default-jre-headless \
    graphviz \
    libfreetype6 \
    libpng16-16 \
    fonts-dejavu-core \
    fonts-lato \
    fonts-noto-core \
  && rm -rf /var/lib/apt/lists/*

# Python tooling
RUN python -m pip install --no-cache-dir -U pip uv

# Headless matplotlib rendering.
ENV MPLBACKEND=Agg
