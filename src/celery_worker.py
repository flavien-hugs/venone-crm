from src.venone import venone_app
from src.__init__ import celery_init_app

# Initialiser l'application Flask avec la configuration appropriée
# (venone_app est déjà créé par src.venone)
celery = celery_init_app(venone_app)
