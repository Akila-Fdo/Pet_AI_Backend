FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       git ffmpeg libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Install CPU-only PyTorch wheels explicitly to avoid CUDA downloads.
RUN pip install --no-cache-dir \
    --index-url https://download.pytorch.org/whl/cpu \
    torch==2.3.1+cpu torchvision==0.18.1+cpu

COPY requirements.txt /app/requirements.txt
RUN grep -vE '^(torch|torchvision)($|[<=>~!])' /app/requirements.txt > /tmp/requirements.no-torch.txt \
    && pip install --no-cache-dir -r /tmp/requirements.no-torch.txt \
    && rm /tmp/requirements.no-torch.txt

COPY . /app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
