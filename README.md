# Django Pokédex (Générations 1 à 6)

Ce projet est une application Django permettant de consulter une base de données enrichie des Pokémon des générations 1 à 6, à partir des données de la [PokéAPI](https://pokeapi.co/). Il repose sur une architecture Docker modulaire (Django, MySQL, phpMyAdmin, Nginx) et un modèle de données relationnel normalisé.

---

## 🧠 Fonctionnalités principales

- Intégration des Pokémon des générations 1 à 6
- Données extraites de la PokéAPI : noms, tailles, poids, types, capacités, statistiques de base, sprites, cris, descriptions
- Structuration relationnelle :
  - Types avec couleurs personnalisées
  - Table d'efficacité des types (multiplicateurs de dégâts)
  - Capacités avec gestion de la visibilité (cachées ou non)
  - Statistiques de base par Pokémon
  - Multiples descriptions textuelles
- Modèles Django reflétant cette structure
- Interface d'administration Django activable

---

## 🐳 Stack technique

- **Django** (Python 3.12)
- **MySQL 8.3**
- **phpMyAdmin** (accès simplifié à la base)
- **Gunicorn** (serveur WSGI)
- **Nginx** (serveur proxy pour Django)
- **Docker & Docker Compose**

---

## 📁 Structure du projet

- `pokedex_project/` : Application Django
- `models.py` : Définition des modèles relationnels (Pokémon, Types, Capacités, etc.)
- `Dockerfile` : Image personnalisée Django + Gunicorn
- `docker-compose.yml` : Orchestration des services
- `nginx.conf` : Configuration du serveur Nginx
- `requirements.txt` : Dépendances Python
- `wait-for-it.sh` : Script de synchronisation avec MySQL

---

## 🚀 Lancer le projet

### 1. Cloner le projet

```bash
git clone https://github.com/votre-utilisateur/django-pokedex.git
cd django-pokedex
```

### 2. Construire et démarrer les conteneurs

```bash
docker-compose up --build
```

### 3. Accéder aux services

- Interface Pokédex (via Nginx) : http://localhost:8072
- phpMyAdmin : http://localhost:8087  
  - **Utilisateur** : `root`  
  - **Mot de passe** : `passroot`  
  - **Hôte** : `mysql`

---

## ⚙️ Variables de configuration (extraites)

- Base de données :  
  - `MYSQL_DATABASE=pokedex`  
  - `MYSQL_USER=dexuser`  
  - `MYSQL_PASSWORD=passkedex`
- Django :  
  - `DJANGO_SETTINGS_MODULE=pokedex_project.settings`

---

## 🧩 Modèles principaux

### `Pokemon`
- Nom, taille, poids, base experience, sprite, cri
- Relations : `PokemonAbility`, `PokemonType`, `BaseStats`, `PokemonDescription`

### `Ability` & `PokemonAbility`
- Capacité avec gestion de visibilité (cachée ou non)
- Slot de priorité

### `Type` & `PokemonType`
- Types avec couleurs personnalisées
- Gestion du slot de priorité

### `BaseStats`
- Statistiques : HP, ATK, DEF, SP.ATK, SP.DEF, Vitesse

### `TypeEfficacy`
- Multiplicateurs de dégâts entre types (ex : Feu → Plante = x2)

### `PokemonDescription`
- Descriptions multiples et surnoms facultatifs

---

## 🧪 Exemple de script de peuplement

L’import des données depuis la PokéAPI n’est pas inclus ici, mais vous pouvez utiliser `requests` et l’API RESTful de PokéAPI pour peupler les tables via un script de gestion Django (`manage.py`).

---

## 🛠 Commandes utiles (via docker-compose)

```bash
# Accéder au shell Django
docker-compose exec django python manage.py shell

# Exécuter des migrations
docker-compose exec django python manage.py migrate

# Créer un superutilisateur
docker-compose exec django python manage.py createsuperuser

# Collecter les fichiers statiques
docker-compose exec django python manage.py collectstatic --noinput
```

---

## 🔐 Accès admin (optionnel)

Activez l'interface Django Admin dans `settings.py` si vous souhaitez gérer les modèles manuellement :
```python
INSTALLED_APPS += ["django.contrib.admin"]
```
Ensuite, exécutez `createsuperuser` pour accéder à `http://localhost:8072/admin`.

---

## 🧹 Nettoyage

```bash
docker-compose down -v
```

Cela supprime les conteneurs **et les volumes** (`mysql-data`, `cache-volume`, `log-volume`).

---

## 📦 Volumes Docker utilisés

- `mysql-data` : persistance des données MySQL
- `cache-volume` : cache local de données API
- `log-volume` : logs d'extraction ou d'import

---

## ✨ Contributions

Améliorations bienvenues ! Ce projet est conçu pour être étendu avec de nouvelles générations, des mécaniques avancées (formes, talents, évolution, localisation, etc.), ou une interface frontend dédiée.

---

## 📜 Licence

Ce projet est open-source et peut être utilisé librement.
