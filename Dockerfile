FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DATA_DIR=/data

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Обычный пользователь вместо root + папка для базы и логов
RUN useradd --create-home botuser && mkdir /data && chown botuser /data

COPY --chown=botuser main.py config.py vk_client.py scheduler.py storage.py \
     diagnose.py listen.py messages.json ./

USER botuser

CMD ["python", "main.py"]
