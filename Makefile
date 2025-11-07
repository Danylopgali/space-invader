# Simple Makefile for Space Invaders game
# Usage:
#   make run        -> ejecuta el juego
#   make venv       -> crea entorno virtual .venv si no existe
#   make install    -> instala dependencias (si agregas requirements.txt)
#   make clean      -> elimina __pycache__
#   make help       -> muestra objetivos

# Detectar intérprete Python (prioriza python3 si existe)
PYTHON := $(shell command -v python3 2>/dev/null || command -v python 2>/dev/null || echo python)
VENV_DIR := .venv
REQ := requirements.txt

.PHONY: run venv install clean help

run: ## Ejecuta el juego
	$(PYTHON) main.py

venv: ## Crea entorno virtual .venv
	@if [ ! -d "$(VENV_DIR)" ]; then $(PYTHON) -m venv $(VENV_DIR); echo "[OK] Entorno virtual creado"; else echo "[SKIP] Ya existe $(VENV_DIR)"; fi
	@echo "Para activarlo: source $(VENV_DIR)/bin/activate (WSL)"

install: venv ## Instala dependencias desde requirements.txt si existe
	@if [ -f "$(REQ)" ]; then . $(VENV_DIR)/bin/activate && pip install -r $(REQ); else echo "[WARN] No hay $(REQ), agrega una si la necesitas"; fi

clean: ## Limpia archivos temporales
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || echo "Windows cleanup"
	@echo "Limpieza completa"

help: ## Muestra ayuda
	@grep -E '^[a-zA-Z_-]+:.*?##' Makefile | sed 's/:.*##/\t- /'
