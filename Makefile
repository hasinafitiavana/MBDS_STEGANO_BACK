# Création d'un environnement virtuel
env:
	python3 -m venv .venv

install-dev:
	.venv/bin/pip install -r requirements/dev.txt


start:
	.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000