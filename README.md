# Mysite Backend

Plateforme de gestion pour suppratourstravel.

## 📋 Table des matières

- [Installation locale](#installation-locale)
- [Configuration](#configuration)
- [Tests](#tests)
- [Déploiement](#déploiement)
- [CI/CD avec GitHub](#cicd-avec-github)

## 🚀 Installation locale

### Prérequis

- Python 3.11+
- MySQL 8.0+
- pip et virtualenv

### Étapes d'installation

1. **Cloner le repository**

```bash
git clone https://github.com/yourusername/mysite_backend.git
cd mysite_backend
```

2. **Créer et activer un environnement virtuel**

```bash
python3 -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

3. **Installer les dépendances**

```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install pytest pytest-django pytest-cov  # Pour les tests
```

4. **Configurer les variables d'environnement**

```bash
cp .env.example .env
```

Ensuite, éditer le fichier `.env` avec vos configurations locales :

```env
DJANGO_ENV=development
SECRET_KEY=your-secret-key
SOCIETE=MyCompany
DB_NAME=mysite_db
DB_USER=mysite_user
DB_PASSWORD=your_password
DB_HOST=localhost
```

5. **Créer la base de données**

```bash
# Créer la base MySQL
mysql -u root -p -e "CREATE DATABASE mysite_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
mysql -u root -p -e "CREATE USER 'mysite_user'@'localhost' IDENTIFIED BY 'your_password';"
mysql -u root -p -e "GRANT ALL PRIVILEGES ON mysite_db.* TO 'mysite_user'@'localhost';"
```

6. **Appliquer les migrations**

```bash
python manage.py migrate
```

7. **Créer un superutilisateur**

```bash
python manage.py createsuperuser
```

8. **Charger les données initiales (optionnel)**

```bash
python manage.py loaddata initial_data
```

9. **Lancer le serveur de développement**

```bash
python manage.py runserver
```

Le serveur sera accessible à `http://localhost:8000`

## ⚙️ Configuration

### Variables d'environnement

Voir [.env.example](.env.example) pour la liste complète des variables disponibles.

### Settings Django

Le projet utilise des configurations différentes selon l'environnement :

- **`mysite/settings/base.py`** - Configuration de base commune
- **`mysite/settings/dev.py`** - Configuration pour développement
- **`mysite/settings/prod.py`** - Configuration pour production
- **`mysite/settings/test.py`** - Configuration pour les tests

L'environnement est sélectionné via la variable `DJANGO_ENV` :

```bash
DJANGO_ENV=development  # Utilise dev.py
DJANGO_ENV=production   # Utilise prod.py
DJANGO_ENV=test         # Utilise test.py
```

## 🧪 Tests

### Lancer tous les tests

```bash
# Avec pytest (recommandé)
pytest

# Avec coverage
pytest --cov=. --cov-report=html
```

### Lancer des tests spécifiques

```bash
# Tests d'une application
pytest accounts/

# Tests d'un fichier
pytest accounts/tests.py

# Tests avec un pattern
pytest -k "test_user"
```

### Tests avec Django test runner (optionnel)

```bash
python manage.py test accounts
```

### Générer un rapport de couverture

```bash
pytest --cov=. --cov-report=html --cov-report=term-missing
# Le rapport est généré dans htmlcov/index.html
```

## 📦 Dépendances principales

- **Django 4.2.16** - Framework web
- **djangorestframework 3.15.2** - API REST
- **mysqlclient 2.2.4** - Connecteur MySQL
- **django-cors-headers 4.6.0** - Gestion CORS
- **django-import-export 4.3.5** - Import/export de données
- **gunicorn 23.0.0** - Serveur WSGI
- **python-decouple 3.8** - Gestion variables d'environnement

## 🔄 CI/CD avec GitHub

### Workflow de test automatique

Un workflow GitHub Actions est configuré pour :

- ✅ Exécuter les tests sur chaque push et pull request
- ✅ Vérifier la couverture de code
- ✅ Valider les migrations Django
- ✅ Exécuter `django check`
- ✅ Recueillir les fichiers statiques

**Fichier de configuration** : [.github/workflows/tests.yml](.github/workflows/tests.yml)

### Branch Protection Rules (recommandé)

Sur GitHub, configurez les règles de protection de branche pour `master` :

1. Aller à **Settings** → **Branches**
2. Ajouter une règle de protection pour `master`
3. Activer :
   - ✅ Require a pull request before merging
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging
   - ✅ Require code reviews before merging (recommandé : 1 review)

### Déclencher manuellement les tests

Les tests se déclenchent automatiquement sur :
- Push sur `master`, `main`, ou `develop`
- Création de pull request

Pour déclencher manuellement :

1. Aller à **Actions** dans GitHub
2. Sélectionner **Django Tests**
3. Cliquer sur **Run workflow**

## 🚀 Déploiement

### Préparation avant déploiement

1. **Vérifier que tous les tests passent**

```bash
pytest
```

2. **Vérifier la configuration de sécurité**

```bash
python manage.py check --deploy
```

3. **Créer une version**

```bash
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

### Déploiement sur PythonAnywhere

#### Prérequis PythonAnywhere
- Compte PythonAnywhere
- Accès SSH configuré

#### Étapes de déploiement

1. **Sur votre machine locale, préparer la release**

```bash
# Mettre à jour les versions
git add .
git commit -m "Prepare release v1.0.0"
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin master
git push origin v1.0.0
```

2. **Sur PythonAnywhere, cloner/mettre à jour le code**

```bash
cd /home/yourusername/mysite
git pull origin master
```

3. **Activer l'environnement virtuel et installer les dépendances**

```bash
source venv/bin/activate
pip install -r requirements.txt
```

4. **Appliquer les migrations**

```bash
python manage.py migrate
```

5. **Collecter les fichiers statiques**

```bash
python manage.py collectstatic --no-input
```

6. **Redémarrer l'application web**

```bash
# Via l'interface web de PythonAnywhere ou :
touch /var/www/yourusername_pythonanywhere_com_wsgi.py
```

## 📋 Checklist de déploiement

- [ ] Tous les tests passent (`pytest`)
- [ ] Les vérifications de sécurité passent (`python manage.py check --deploy`)
- [ ] Les variables d'environnement sont configurées sur PythonAnywhere
- [ ] La base de données est sauvegardée
- [ ] Les migrations sont appliquées
- [ ] Les fichiers statiques sont collectés
- [ ] Le serveur web est redémarré
- [ ] Les tests de fumée sont effectués

## 🐛 Dépannage

### Erreur de connexion à la base de données

```bash
# Vérifier les paramètres dans .env
cat .env | grep DB_

# Vérifier que MySQL est actif
mysql -u root -p -e "SHOW DATABASES;"
```

### Erreurs de migrations

```bash
# Voir l'état des migrations
python manage.py showmigrations

# Réinitialiser les migrations (développement uniquement)
python manage.py migrate --fake accounts zero
```

### Fichiers statiques manquants

```bash
python manage.py collectstatic --clear --no-input
```

## 📚 Documentation supplémentaire

- [Django Documentation](https://docs.djangoproject.com/en/4.2/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [PythonAnywhere Docs](https://help.pythonanywhere.com/)
- [GitHub Actions](https://docs.github.com/en/actions)

## 📞 Support

Pour des questions ou problèmes, veuillez créer une **issue** sur GitHub.

## 📄 Licence

Propriétaire - SupraTours Travel

---

**Dernière mise à jour** : Mai 2026
