FROM runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://ollama.com/install.sh | sh

RUN pip install --no-cache-dir \
    runpod \
    requests \
    aiohttp

COPY handler.py /app/handler.py

ENV OLLAMA_HOST=0.0.0.0
ENV OLLAMA_MODELS=/runpod-volume/models

EXPOSE 11434

CMD ["python", "-u", "/app/handler.py"]