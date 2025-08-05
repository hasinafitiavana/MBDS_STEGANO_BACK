@echo off

if "%1"=="env" (
    python -m venv .venv
)

if "%1"=="install-dev" (
    .venv\Scripts\pip install -r requirements\dev.txt
)

if "%1"=="start" (
    .venv\Scripts\uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
)
