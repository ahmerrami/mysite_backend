# 🚀 Guide de démarrage rapide

## ⚡ En 5 minutes

### 1️⃣ Installer et configurer (première fois)

```bash
bash scripts/setup.sh
```

Ce script va :
- ✅ Créer un environnement virtuel
- ✅ Installer les dépendances
- ✅ Créer le fichier `.env`
- ✅ Appliquer les migrations
- ✅ Créer un superutilisateur

### 2️⃣ Lancer le serveur

```bash
bash scripts/run.sh
```

Accédez à :
- 🌐 Application : http://localhost:8000
- 👤 Admin : http://localhost:8000/admin

### 3️⃣ Lancer les tests

```bash
bash scripts/test.sh
```

## 📚 Documentation complète

| Document | Contenu |
|----------|---------|
| [README.md](README.md) | Guide complet d'installation et fonctionnalités |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Commandes Django et guide de déploiement |
| [GITHUB_SETUP.md](GITHUB_SETUP.md) | Configuration GitHub pour CI/CD |
| [PYTHONANYWHERE_SETUP.md](PYTHONANYWHERE_SETUP.md) | Déploiement sur PythonAnywhere |
| [CONVENTIONS.md](CONVENTIONS.md) | Bonnes pratiques et conventions de code |

## 🔄 Flux de travail typique

### Développement local

```bash
# 1. Créer une branche
git checkout -b feature/ma-feature

# 2. Faire des changements
# ... modifiez les fichiers ...

# 3. Tester localement
bash scripts/test.sh --coverage

# 4. Valider la configuration
python manage.py check --deploy

# 5. Commit et push
git add .
git commit -m "Feature: ajout de la nouvelle feature"
git push origin feature/ma-feature
```

### Pull Request sur GitHub

```bash
# Créer une PR sur GitHub
# → Tous les tests s'exécutent automatiquement
# → Attendre que tout passe ✅
# → Merger après review
```

### Déploiement

```bash
# Sur PythonAnywhere
# → Voir PYTHONANYWHERE_SETUP.md pour les étapes détaillées
```

## 🧪 Tests

### Lancer tous les tests

```bash
bash scripts/test.sh
```

### Lancer les tests d'une application

```bash
bash scripts/test.sh accounts/
```

### Lancer les tests avec couverture

```bash
bash scripts/test.sh --coverage
# Voir le rapport : open htmlcov/index.html
```

## 🔐 Variables d'environnement

Copier `.env.example` vers `.env` et adapter :

```env
DJANGO_ENV=development
SECRET_KEY=your-secret-key
SOCIETE=YourCompany
DB_NAME=mysite_db
DB_USER=mysite_user
DB_PASSWORD=your_password
DB_HOST=localhost
```

## 📂 Structure du projet

```
mysite_backend/
├── accounts/              # Gestion des utilisateurs
├── fournisseurs/          # Gestion des fournisseurs
├── clients/               # Gestion des clients
├── aos/                   # Application AOS
├── omra/                  # Application Omra
├── stages/                # Gestion des stages
├── operationsDiverses/    # Opérations diverses
├── mysite/                # Configuration Django
├── static/                # Fichiers statiques
├── media/                 # Fichiers uploadés
├── scripts/               # Scripts d'automatisation
├── .github/workflows/     # GitHub Actions
├── README.md              # Documentation principale
├── DEPLOYMENT.md          # Guide de déploiement
├── GITHUB_SETUP.md        # Configuration GitHub
├── PYTHONANYWHERE_SETUP.md # Configuration PythonAnywhere
└── CONVENTIONS.md         # Conventions de code
```

## 🆘 Aide rapide

### Je veux...

| Action | Commande |
|--------|----------|
| **Lancer le serveur** | `bash scripts/run.sh` |
| **Lancer les tests** | `bash scripts/test.sh` |
| **Lancer avec couverture** | `bash scripts/test.sh --coverage` |
| **Créer une migration** | `python manage.py makemigrations` |
| **Appliquer les migrations** | `python manage.py migrate` |
| **Créer un superutilisateur** | `python manage.py createsuperuser` |
| **Voir la couverture** | `bash scripts/test.sh --coverage && open htmlcov/index.html` |
| **Accéder à la shell Django** | `python manage.py shell` |
| **Exporter les données** | `python manage.py dumpdata > backup.json` |
| **Vérifier la configuration** | `python manage.py check` |
| **Vérifier la sécurité** | `python manage.py check --deploy` |

## 📝 Notes

- **Environnement virtuel** : Le script `setup.sh` le crée automatiquement dans `venv/`
- **Base de données** : Par défaut en développement, vous avez besoin de MySQL
- **Fichiers statiques** : Collectés avec `python manage.py collectstatic`
- **Tests** : Utilisent une BD SQLite en mémoire (rapide et isolée)

## ⚠️ Troubleshooting courant

### `python: command not found`
```bash
# Utiliser python3 à la place
python3 manage.py runserver
```

### `ModuleNotFoundError`
```bash
# Activer l'environnement virtuel
source venv/bin/activate
```

### `Permission denied` pour les scripts
```bash
# Rendre exécutable
chmod +x scripts/*.sh
```

### Erreur de base de données
```bash
# S'assurer que MySQL est actif
mysql -u root -p -e "SHOW DATABASES;"
```

## 🔗 Liens utiles

- [Django Documentation](https://docs.djangoproject.com/en/4.2/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Pytest Documentation](https://docs.pytest.org/)
- [GitHub Actions](https://docs.github.com/en/actions)
- [PythonAnywhere](https://www.pythonanywhere.com/)

## ✅ Checklist initial

- [ ] Cloner le repository
- [ ] Lancer `bash scripts/setup.sh`
- [ ] Éditer le `.env` avec vos paramètres
- [ ] Lancer `bash scripts/run.sh`
- [ ] Accéder à http://localhost:8000
- [ ] Lancer les tests avec `bash scripts/test.sh`

---

**Besoin d'aide ?** Voir les guides complets dans :
- [README.md](README.md) - Guide complet
- [DEPLOYMENT.md](DEPLOYMENT.md) - Commandes détaillées
- [GITHUB_SETUP.md](GITHUB_SETUP.md) - Configuration GitHub
