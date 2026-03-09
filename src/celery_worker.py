from main import celery_init_app
from src.cli import app

# Initialiser l'application Flask avec la configuration appropriée
# (app est déjà créé par src.app)
celery = celery_init_app(app)
