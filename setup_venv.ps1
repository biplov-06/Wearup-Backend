# PowerShell script to create a venv and install requirements
# Run from the Backend folder in PowerShell

$VENV_DIR = "$PWD\venv"
if (-Not (Test-Path $VENV_DIR)) {
    python -m venv $VENV_DIR
}

# Activate venv
& "$VENV_DIR\Scripts\Activate.ps1"

# Upgrade pip and install requirements
python -m pip install --upgrade pip
pip install -r "$PWD\requirements.txt"

Write-Output "Virtualenv created and requirements installed. Activate with: .\venv\Scripts\Activate.ps1"