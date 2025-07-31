FROM python:3.11-slim


WORKDIR /apps



COPY requirements/ requirements/

RUN python3 -m venv .venv

RUN .venv/bin/pip install --upgrade pip
RUN .venv/bin/pip install --no-cache-dir -r requirements/dev.txt --index-url https://pypi.org/simple
COPY models/ models/

copy .env .env


COPY app/ app/

CMD [".venv/bin/uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]