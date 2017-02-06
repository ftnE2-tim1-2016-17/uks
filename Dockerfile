FROM python:3.4

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /ticket_system
COPY /ticket_system/requirements.txt ./
RUN pip install -r requirements.txt
COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "makemigrations app"]
CMD ["python", "manage.py", "migrate"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]