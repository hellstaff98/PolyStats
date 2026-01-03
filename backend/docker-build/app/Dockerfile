FROM python:3.12.6-bookworm

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app

WORKDIR /app

RUN pip install --upgrade pip wheel "poetry==1.8.3"
RUN poetry config virtualenvs.create false

# Копируем конфиги из корня проекта
COPY pyproject.toml poetry.lock* ./
RUN poetry install --no-interaction --no-ansi

# Копируем всё содержимое папки app в /app контейнера
# (Это автоматически скопирует и папку tests, если она внутри app)
COPY app/ .

# Исправляем права для скриптов, если они есть
RUN chmod +x prestart.sh run || true

ENTRYPOINT ["./prestart.sh"]
CMD ["uvicorn", "main:main_app", "--host", "0.0.0.0", "--port", "8000"]