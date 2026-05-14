# Configuration PythonAnywhere - Guide complet

## 📌 Vue d'ensemble

Ce guide explique comment déployer votre projet Django sur PythonAnywhere après l'avoir testé sur GitHub.

## 🚀 Prérequis

- ✅ Compte PythonAnywhere (gratuit ou payant)
- ✅ Tous les tests passent sur GitHub
- ✅ Code commité et pushé sur GitHub
- ✅ Variables d'environnement configurées

## 1️⃣ Préparation locale avant déploiement

### Vérifier que tout fonctionne

```bash
# 1. Vérifier que les tests passent
pytest

# 2. Vérifier la sécurité
python manage.py check --deploy

# 3. Vérifier que les migrations sont créées
python manage.py makemigrations --dry-run

# 4. Vérifier que les fichiers statiques sont collectés
python manage.py collectstatic --dry-run --no-input

# 5. Générer une nouvelle clé secrète pour la production
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

### Créer une release

```bash
# Créer une tag de version
git tag -a v1.0.0 -m "Release version 1.0.0"

# Pousser la tag
git push origin v1.0.0

# Vérifier
git tag -l
```

## 2️⃣ Configuration PythonAnywhere (Interface Web)

### Étape 1 : Créer une application web

1. Aller à **Web** dans la barre latérale
2. Cliquer sur **Add a new web app**
3. Sélectionner :
   - Domaine : `yourusername.pythonanywhere.com` (gratuit) ou custom
   - Framework : **Django**
   - Python version : **3.11** ou **3.12**

### Étape 2 : Configurer l'application Django

Après création, aller à **Web** → Sélectionner votre app

#### WSGI configuration file
Cliquer sur le lien `WSGI configuration file` et remplacer le contenu :

```python
"""
WSGI config for mysite project on PythonAnywhere.
"""
import os
import sys

# Ajouter le répertoire du projet au PATH
path = '/home/yourusername/mysite'
if path not in sys.path:
    sys.path.append(path)

# Configuration Django
os.environ['DJANGO_SETTINGS_MODULE'] = 'mysite.settings.prod'

# Importer l'application WSGI
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

#### Virtualenv
1. Créer un virtualenv (voir Section 3)
2. Entrer son chemin : `/home/yourusername/mysite/venv`

#### Static files
Ajouter le mapping des fichiers statiques :
```
/static/  =>  /home/yourusername/mysite/static
/media/   =>  /home/yourusername/mysite/media
```

### Étape 3 : Configurer les variables d'environnement

1. Aller à **Web** → **Environment variables**
2. Ajouter chaque variable depuis votre `.env.production` :

```
DJANGO_ENV=production
SECRET_KEY=your-new-secret-key-from-step-1
SOCIETE=MySite
ALLOWED_HOSTS=yourusername.pythonanywhere.com,yourdomain.com
CORS_ALLOWED_ORIGINS=https://yourusername.pythonanywhere.com,https://yourdomain.com
DB_ENGINE=django.db.backends.mysql
DB_NAME=yourusername$mysite_db
DB_USER=yourusername
DB_PASSWORD=your-mysql-password
DB_HOST=yourusername.mysql.pythonanywhere-services.com
```

## 3️⃣ Configuration SSH (Terminal PythonAnywhere)

### Étape 1 : Ouvrir une console Bash

1. Aller à **Consoles**
2. Cliquer sur **Bash console**

### Étape 2 : Cloner le repository

```bash
# Se placer dans le home
cd ~

# Cloner le repository
git clone https://github.com/yourusername/mysite_backend.git mysite

# Entrer dans le répertoire
cd mysite

# Vérifier la branche (utiliser main si c'est votre principale)
git branch -a
```

### Étape 3 : Créer et configurer le virtualenv

```bash
# Créer le virtualenv
mkvirtualenv --python=/usr/bin/python3.12 mysite_venv

# Il devrait être activé automatiquement, sinon :
workon mysite_venv

# Mettre à jour pip
pip install --upgrade pip

# Installer les dépendances
pip install -r requirements.txt

# Installer gunicorn (optionnel, si vous utilisez gunicorn)
pip install gunicorn
```

### Étape 4 : Configurer la base de données

```bash
# Créer la base de données MySQL (une fois)
# Via l'interface PythonAnywhere Web → MySQL → Create a new database

# Appliquer les migrations
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser
```

### Étape 5 : Collecter les fichiers statiques

```bash
# Collecter tous les fichiers statiques
python manage.py collectstatic --no-input --clear

# Vérifier
ls -la static/
```

### Étape 6 : Tester l'application

```bash
# Test rapide
python manage.py check

# Lancer le serveur test (accès sur http://yourusername.pythonanywhere.com:8000)
python manage.py runserver 0.0.0.0:8000
```

## 4️⃣ Redémarrer l'application web

Après configuration, redémarrer l'application :

1. Aller à **Web**
2. Cliquer le bouton **Reload** (vert)
3. Attendre quelques secondes
4. Visiter `https://yourusername.pythonanywhere.com`

## 5️⃣ Configuration personnalisée du domaine

Si vous avez un domaine custom :

1. Aller à **Web**
2. Entrer le domaine dans le champ **Domains**
3. Vérifier les enregistrements DNS :
   ```
   Type: A
   Name: yourdomain.com (ou subdomain)
   Value: (l'IP fournie par PythonAnywhere)
   ```
4. Attendre 24-48h pour la propagation DNS

## 🔒 Configuration HTTPS/SSL

PythonAnywhere propose SSL gratuit avec Let's Encrypt :

1. Aller à **Web** → **SSL certificate**
2. Cliquer **Auto-renew** si non activé
3. Si pas de certificat :
   - Cliquer **Get a new certificate with Let's Encrypt**
   - Suivre les étapes
4. Vérifier que le protocole est HTTPS

## 📁 Structure des répertoires sur PythonAnywhere

```
/home/yourusername/
├── mysite/                    # Votre projet Django
│   ├── mysite/               # Dossier project
│   │   ├── settings/
│   │   ├── wsgi.py
│   │   └── ...
│   ├── accounts/
│   ├── fournisseurs/
│   ├── manage.py
│   ├── requirements.txt
│   ├── static/               # Fichiers statiques collectés
│   ├── media/                # Fichiers uploadés
│   └── venv/                 # Virtualenv
├── mysite_venv/              # Alternative virtualenv
└── .../                       # Autres fichiers
```

## 🔄 Mettre à jour le code

### Via SSH

```bash
cd ~/mysite

# Activer le virtualenv
workon mysite_venv

# Récupérer les changements
git fetch origin
git pull origin main

# Installer les nouvelles dépendances (si changé)
pip install -r requirements.txt

# Appliquer les migrations
python manage.py migrate

# Collecter les fichiers statiques
python manage.py collectstatic --no-input

# Redémarrer l'application
# Va au Web et clique "Reload"
```

### Avec un script d'automatisation (optionnel)

Créer un fichier `~/deploy.sh` :

```bash
#!/bin/bash
cd ~/mysite
source ../mysite_venv/bin/activate
git pull origin main
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --no-input
echo "✅ Déploiement terminé!"
```

Puis exécuter :
```bash
bash ~/deploy.sh
```

## 📊 Monitoring

### Voir les logs

```bash
# Logs d'erreur web
tail -f /var/log/yourusername.pythonanywhere.com.error.log

# Logs d'accès
tail -f /var/log/yourusername.pythonanywhere.com.access.log
```

### Vérifier les processus

```bash
# Processus en cours
ps aux | grep python

# Espace disque utilisé
du -sh ~/mysite
```

### Vérifier la base de données

```bash
# Connecter à MySQL
mysql -u yourusername
SHOW DATABASES;
USE yourusername$mysite_db;
SHOW TABLES;
```

## 🐛 Troubleshooting

### 502 Bad Gateway

**Cause** : L'application WSGI a un problème

**Solution** :
```bash
# Vérifier les logs
tail /var/log/yourusername.pythonanywhere.com.error.log

# Tester la configuration
python manage.py check

# Redémarrer l'app
# Via Web → Reload
```

### Static files missing (404)

**Cause** : Les fichiers statiques ne sont pas collectés

**Solution** :
```bash
# Collecter les fichiers
python manage.py collectstatic --no-input

# Vérifier le chemin dans Web → Static files
# Doit pointer vers /home/yourusername/mysite/static
```

### Database connection error

**Cause** : Variables d'environnement non configurées

**Solution** :
```bash
# Vérifier les variables
env | grep DB_

# Les configurer dans Web → Environment variables
```

### Package import error

**Cause** : Virtualenv non activé ou dépendances manquantes

**Solution** :
```bash
# Activer le virtualenv
workon mysite_venv

# Réinstaller
pip install -r requirements.txt
```

## 🚨 Backup et Restore

### Sauvegarder la base de données

```bash
# Exporter les données
python manage.py dumpdata > backup.json

# Avec gzip
python manage.py dumpdata | gzip > backup.json.gz
```

### Restaurer la base de données

```bash
# Depuis le backup
python manage.py loaddata backup.json

# Depuis gzip
gunzip < backup.json.gz | python manage.py loaddata
```

## ✅ Checklist final

- [ ] Code poussé sur GitHub
- [ ] Tous les tests passent
- [ ] Application créée sur PythonAnywhere
- [ ] Virtualenv configuré
- [ ] Variables d'environnement ajoutées
- [ ] Base de données MySQL créée
- [ ] Migrations appliquées
- [ ] Fichiers statiques collectés
- [ ] Application redémarrée
- [ ] HTTPS/SSL activé
- [ ] Domaine configuré (si custom)
- [ ] Tests de fumée effectués

## 📞 Support

- [PythonAnywhere Help](https://help.pythonanywhere.com/)
- [Django Deployment Guide](https://docs.djangoproject.com/en/4.2/howto/deployment/)

---

**Dernière mise à jour** : Mai 2026
