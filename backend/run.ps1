# Start TrendWatch Python API using the project venv (not conda).
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not (Test-Path ".\venv\Scripts\python.exe")) {
    Write-Host "Creating venv..."
    python -m venv venv
}

Write-Host "Installing dependencies..."
.\venv\Scripts\pip install -r requirements.txt --quiet

Write-Host "Checking spaCy model..."
.\venv\Scripts\python -c "import spacy; spacy.load('en_core_web_sm'); print('en_core_web_sm OK')"

Write-Host "Starting uvicorn (reload excludes venv to avoid model install races)..."
.\venv\Scripts\uvicorn main:app --reload --reload-exclude "venv" --host 127.0.0.1 --port 8000
