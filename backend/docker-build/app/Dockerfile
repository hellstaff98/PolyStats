FROM python:3.12.6-bookworm

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN pip install --upgrade pip wheel "poetry==1.8.3"

RUN poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock ./

RUN poetry install

COPY app .

RUN chmod +x prestart.sh
RUN chmod +x run

ENTRYPOINT ["./prestart.sh"]
CMD ["uvicorn", "main:main_app", "--host", "0.0.0.0", "--port", "8000"]