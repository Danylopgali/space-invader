# Space Invaders (simple)

## Ejecutar

- Windows PowerShell (recomendado):
  - Si tienes un entorno virtual en `.venv`:
    ```powershell
    .\.venv\Scripts\Activate.ps1
    ```
  - Ejecuta el juego:
    ```powershell
    python main.py
    ```
  - O usa el script:
    ```powershell
    ./run.ps1
    ```

- WSL / Linux / macOS (si tienes `make`):
  ```bash
  make run
  ```

## Estructura

- `main.py`: punto de entrada
- `game.py`: bucle principal del juego (nivel único, HUD, sonido de inicio, colisiones)
- `entities/`: `player.py`, `enemy.py`, `ship.py`, `bullet.py`
- `core/`: `settings.py`, `drawing.py`
- `assets/sounds/start.wav`: se genera automáticamente si no existe
- `images/` o `images/img/`: se buscan imágenes primero aquí

## Notas
- En WSL sin servidor gráfico, la ventana puede no verse. En Windows nativo, usa PowerShell.
- Se reproduce un tono corto al iniciar (si el audio no está disponible, se sigue ejecutando).
