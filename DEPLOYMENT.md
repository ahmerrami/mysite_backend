# Guide de déploiement et commandes utiles

## 🚀 Démarrage rapide

### Installation locale (première fois)
```bash
bash scripts/setup.sh
```

### Lancer le serveur de développement
```bash
bash scripts/run.sh
```

### Exécuter les tests
```bash
bash scripts/test.sh                    # Tests simples
bash scripts/test.sh --coverage         # Avec rapport de couverture
bash scripts/test.sh --verbose          # Mode verbeux
bash scripts/test.sh accounts/          # Tests d'une app spécifique
```

## 📋 Commandes Django courantes

### Migrations
```bash
# Créer une migration après modification des modèles
python manage.py makemigrations

# Voir l'état des migrations
python manage.py showmigrations

# Appliquer les migrations
python manage.py migrate

# Appliquer les migrations d'une app spécifique
python manage.py migrate accounts

# Annuler les migrations d'une app
python manage.py migrate accounts zero
```

### Gestion des données
```bash
# Créer un superutilisateur
python manage.py createsuperuser

# Charger des données initiales
python manage.py loaddata initial_data

# Exporter les données
python manage.py dumpdata > data.json

# Importer les données
python manage.py loaddata data.json
```

### Fichiers statiques
```bash
# Collecter les fichiers statiques
python manage.py collectstatic --no-input

# Vérifier les fichiers statiques
python manage.py collectstatic --dry-run
```

### Vérifications et debugging
```bash
# Vérifier la configuration Django
python manage.py check

# Vérifier la sécurité
python manage.py check --deploy

# Afficher les URLs disponibles
python manage.py show_urls

# Lancer la shell Django interactive
python manage.py shell
```

## 🔒 Sécurité avant déploiement

### Checklist de sécurité
```bash
# 1. Vérifier les problèmes de sécurité
python manage.py check --deploy

# 2. Générer une nouvelle clé secrète
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

# 3. Mettre à jour la clé dans .env ou les variables d'environnement
SECRET_KEY=your-new-secret-key

# 4. S'assurer que DEBUG=False en production
DJANGO_ENV=production

# 5. Vérifier que les paramètres HTTPS sont activés
# Dans mysite/settings/prod.py, vérifier:
# - SECURE_SSL_REDIRECT = True
# - SESSION_COOKIE_SECURE = True
# - CSRF_COOKIE_SECURE = True
```

## 📦 Gestion des dépendances

### Mettre à jour les dépendances
```bash
# Afficher les dépendances outdated
pip list --outdated

# Mettre à jour une dépendance spécifique
pip install --upgrade Django

# Sauvegarder les versions actuelles
pip freeze > requirements.txt

# Installer depuis requirements.txt
pip install -r requirements.txt
```

## 🐛 Debugging

### Logs Django
```bash
# Activer les logs en développement
# Dans mysite/settings/dev.py, définir:
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}

# Puis lancer le serveur avec logs
python manage.py runserver --verbosity=3
```

### Shell Django pour tester
```bash
python manage.py shell

# Puis dans la shell:
from accounts.models import MyUser
users = MyUser.objects.all()
for user in users:
    print(user.email)
```

## 🚀 Déploiement PythonAnywhere

### Préparation
```bash
# 1. S'assurer que tous les tests passent
pytest

# 2. Créer une tag de version
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0

# 3. Vérifier la configuration de production
python manage.py check --deploy
```

### Sur PythonAnywhere
```bash
# 1. SSH vers le serveur
ssh -i ~/.ssh/id_rsa username@yourdomain.com

# 2. Aller au répertoire du projet
cd /home/username/mysite

# 3. Activer l'environnement virtuel
source venv/bin/activate

# 4. Mettre à jour le code
git pull origin master

# 5. Installer les dépendances
pip install -r requirements.txt

# 6. Appliquer les migrations
python manage.py migrate

# 7. Collecter les fichiers statiques
python manage.py collectstatic --no-input

# 8. Redémarrer l'application web
# Via l'interface web PythonAnywhere ou via le fichier WSGI
touch /var/www/username_pythonanywhere_com_wsgi.py
```

## 📊 Monitoring

### Vérifier l'état de l'application
```bash
# Via les logs
tail -f /var/log/apache2/access.log
tail -f /var/log/apache2/error.log

# Via la base de données
python manage.py shell
from django.contrib.auth import get_user_model
User = get_user_model()
print(f"Total users: {User.objects.count()}")
```

## 🔄 CI/CD avec GitHub Actions

Les tests s'exécutent automatiquement sur:
- Push sur `master`, `main`, ou `develop`
- Création de pull request

Pour vérifier l'état des tests sur GitHub:
1. Aller à **Actions** dans le repository
2. Sélectionner **Django Tests**
3. Voir le dernier workflow run

## 💡 Tips & Tricks

### Créer un dump de la base locale
```bash
python manage.py dumpdata > backup.json
```

### Restaurer depuis un dump
```bash
python manage.py loaddata backup.json
```

### Réinitialiser les migrations (⚠️ développement uniquement)
```bash
# Supprimer les migrations récentes
rm fournisseurs/migrations/000X_*.py

# Créer une nouvelle migration
python manage.py makemigrations

# Appliquer
python manage.py migrate
```

### Vider la cache (si utilisée)
```bash
python manage.py clear_cache
```

---

**Dernière mise à jour** : Mai 2026
