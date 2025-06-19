FROM python:3.12-slim

WORKDIR /app

# Dépendances système
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Installer les packages Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le code
COPY . .

# Collecter les fichiers statiques (Django)
RUN python manage.py collectstatic --noinput

# Exposer le port (utile pour docker run ou docker-compose)
EXPOSE 8000

# Définir le chemin de recherche Python
ENV PYTHONPATH=/app

# Lancer Gunicorn
CMD ["gunicorn", "pokedex_project.wsgi:application", "--bind", "0.0.0.0:8000"]
