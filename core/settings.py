import os

# Base paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

# Assets
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")
ASSETS_IMG_DIR = os.path.join(ASSETS_DIR, "images")

# Defaults
WIDTH = 800
HEIGHT = 600
FPS = 60
