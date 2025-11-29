
Write-Host ">>> Removing old venv (if exists)..."
if (Test-Path "venv") {
    Remove-Item -Recurse -Force "venv"
    Write-Host ">>> Old venv removed."
} else {
    Write-Host ">>> No previous venv found."
}

Write-Host ">>> Creating new virtual environment..."
python -m venv venv

Write-Host ">>> Activating virtual environment..."
# Standard activation for PowerShell
.\venv\Scripts\Activate.ps1

Write-Host ">>> Upgrading pip..."
python -m pip install --upgrade pip

Write-Host ">>> Installing FastAPI / Uvicorn / Pydantic (Python 3.12 compatible)..."
pip install "pydantic>=1.10.12" "fastapi>=0.110.0" "uvicorn[standard]>=0.24.0"

Write-Host ">>> Verifying installation..."
python -c "import sys, pydantic, fastapi, uvicorn; \
print('Python:', sys.version); \
print('pydantic:', pydantic.__version__); \
print('fastapi:', fastapi.__version__); \
print('uvicorn:', uvicorn.__version__)"

Write-Host "`n>>> Starting FastAPI server..."
uvicorn app:app --reload --host 0.0.0.0 --port 8000
