@echo off
REM Run Space Invaders on Windows without make
setlocal

REM Prefer virtualenv if active, else fall back to system python
where python >nul 2>&1
if errorlevel 1 (
  echo Python no encontrado en PATH.
  exit /b 1
)

python main.py
