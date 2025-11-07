# PowerShell launcher for Space Invaders
# Uso:  ./run.ps1  (si la politica lo bloquea:  Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass)

$venvPy = Join-Path $PSScriptRoot ".venv/Scripts/python.exe"
if (Test-Path $venvPy) {
    & $venvPy main.py
} else {
    & python main.py
}
