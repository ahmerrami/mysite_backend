# Bonnes pratiques et conventions du projet

## 📋 Table des matières

1. [Structure du code](#structure-du-code)
2. [Conventions de nommage](#conventions-de-nommage)
3. [Écriture des tests](#écriture-des-tests)
4. [Git et versioning](#git-et-versioning)
5. [Sécurité](#sécurité)
6. [Performance](#performance)
7. [Documentation](#documentation)

## 🏗️ Structure du code

### Organisation des fichiers Django

```
app_name/
├── __init__.py
├── admin.py           # Configuration Django Admin
├── apps.py            # Configuration de l'app
├── models.py          # Modèles de données
├── views.py           # Vues (ou dossier views/)
├── serializers.py     # Serializers DRF (si API REST)
├── forms.py           # Formulaires Django
├── urls.py            # URLs de l'app
├── validators.py      # Validateurs personnalisés
├── tests.py           # Tests (ou dossier tests/)
├── signals.py         # Django signals
├── management/
│   └── commands/      # Commandes Django personnalisées
├── migrations/        # Migrations de BD
└── templates/
    └── app_name/      # Templates
```

### Dossiers importants

```
mysite_backend/
├── mysite/           # Project settings
│   ├── settings/
│   │   ├── base.py   # Configuration commune
│   │   ├── dev.py    # Développement
│   │   ├── prod.py   # Production
│   │   └── test.py   # Tests
│   ├── urls.py       # URLs principales
│   └── wsgi.py
├── static/           # Fichiers statiques (CSS, JS, images)
├── media/            # Fichiers uploadés
├── scripts/          # Scripts d'automatisation
├── requirements.txt  # Dépendances Python
├── manage.py
├── pytest.ini        # Configuration pytest
└── README.md
```

## 📛 Conventions de nommage

### Python/Django

| Élément | Convention | Exemple |
|---------|------------|---------|
| **Fichiers** | `snake_case` | `user_models.py`, `api_views.py` |
| **Modules** | `snake_case` | `from myapp.models import MyModel` |
| **Classes** | `PascalCase` | `class UserSerializer` |
| **Fonctions** | `snake_case` | `def get_user_data()` |
| **Variables** | `snake_case` | `user_count = 10` |
| **Constantes** | `UPPER_SNAKE_CASE` | `MAX_USERS = 100` |
| **Modèles** | `PascalCase` | `class MyUser` |
| **Champs privés** | `_snake_case` | `self._internal_value` |

### Django ORM

```python
# ❌ Mauvais
class UserModel(models.Model):
    user_name = models.CharField(max_length=100)
    email_address = models.EmailField()

# ✅ Bon
class User(models.Model):
    username = models.CharField(max_length=100)
    email = models.EmailField()

# ❌ Mauvais
class user_profile(models.Model):
    pass

# ✅ Bon
class UserProfile(models.Model):
    pass
```

### URLs

```python
# ✅ Bon : paths explicites
urlpatterns = [
    path('api/users/', UserListCreateView.as_view(), name='user-list-create'),
    path('api/users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('api/users/<int:pk>/update/', UserUpdateView.as_view(), name='user-update'),
]
```

## 🧪 Écriture des tests

### Structure des tests

```python
# ✅ Bon
import pytest
from django.test import TestCase
from rest_framework.test import APITestCase

class UserModelTests(TestCase):
    """Tests pour le modèle User"""
    
    def setUp(self):
        """Préparation avant chaque test"""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
    
    def test_user_creation(self):
        """Test la création d'un utilisateur"""
        self.assertEqual(User.objects.count(), 1)
    
    def test_user_email_validation(self):
        """Test la validation de l'email"""
        # ...test...

@pytest.mark.django_db
class TestUserAPI:
    """Tests API avec pytest"""
    
    def test_get_users(self, api_client):
        """Test la récupération des utilisateurs"""
        response = api_client.get('/api/users/')
        assert response.status_code == 200
```

### Bonnes pratiques des tests

```python
# ✅ Noms de tests explicites
def test_user_creation_with_valid_email(self):
    pass

# ❌ Noms génériques
def test_user(self):
    pass

# ✅ Tests avec assertions claires
def test_user_email(self):
    user = User.objects.create_user(email='test@example.com')
    self.assertEqual(user.email, 'test@example.com')

# ❌ Tests vagues
def test_user_email(self):
    user = User.objects.create_user(email='test@example.com')
    self.assertTrue(user)

# ✅ Tests indépendants
def test_user_creation(self):
    user = User.objects.create_user(email='test1@example.com')
    # Tester seulement la création

def test_user_update(self):
    user = User.objects.create_user(email='test2@example.com')
    # Tester seulement la mise à jour

# ❌ Tests dépendants
def test_user_workflow(self):
    user = User.objects.create_user(email='test@example.com')
    # ... 10 assertions ...
    # Difficile de localiser les erreurs
```

### Couverture de tests

```bash
# Exécuter avec couverture
pytest --cov=. --cov-report=html

# Minimal : 80% de couverture
# Cible : 90%+

# Voir quelles lignes ne sont pas testées
# Ouvrir htmlcov/index.html dans le navigateur
```

## 📦 Git et versioning

### Commits

```bash
# ✅ Bon format de commit
git commit -m "Feature: add user authentication API"
git commit -m "Fix: user email validation bug"
git commit -m "Docs: update README with setup instructions"
git commit -m "Refactor: simplify user serializer"
git commit -m "Test: add test cases for user creation"

# ❌ Mauvais format
git commit -m "fix stuff"
git commit -m "updates"
git commit -m "WIP"
```

### Branches

```bash
# Convention des noms de branche
feature/user-authentication        # Nouvelle fonctionnalité
fix/user-email-validation         # Correction de bug
refactor/user-model               # Refactorisation
docs/setup-guide                  # Documentation
test/user-api-tests               # Tests

# ❌ À éviter
my-work
update
temp
test123
```

### Tags de version

```bash
# Format : v(MAJOR).(MINOR).(PATCH)
git tag -a v1.0.0 -m "Release version 1.0.0"
git tag -a v1.0.1 -m "Fix: critical security issue"
git tag -a v1.1.0 -m "Feature: new user dashboard"

# Pousser les tags
git push origin v1.0.0
```

### Pull Requests

```markdown
## Description
Description courte et claire de la feature/fix

## Type de changement
- [x] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation

## Testing
- [x] Tests ajoutés
- [x] Tests passent localement
- [x] Couverture vérifiée

## Checklist
- [x] Code suit les conventions du projet
- [x] Documenté et commenté
- [x] Pas de breaking changes
- [x] Migrations créées (si besoin)

Ferme #123
```

## 🔒 Sécurité

### Variables d'environnement

```python
# ✅ Bon : utiliser python-decouple
from decouple import config

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='').split(',')

# ❌ Mauvais : hardcoder les secrets
SECRET_KEY = 'my-super-secret-key'
DB_PASSWORD = 'password123'
```

### Authentification

```python
# ✅ Bon : utiliser les authentificateurs DRF
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    )
}

# ❌ Mauvais : pas de protection
# (Laisser les endpoints publics par défaut)
```

### CORS

```python
# ✅ Bon : être restrictif
CORS_ALLOWED_ORIGINS = [
    'https://yourdomain.com',
    'https://app.yourdomain.com',
]

# ❌ Mauvais : tout autoriser
CORS_ALLOWED_ORIGINS = ['*']
```

### Sensibilité des données

```python
# ✅ Ne pas mettre en log les données sensibles
import logging
logger = logging.getLogger(__name__)
logger.info(f'User {user.id} created')  # ✅

# ❌ Ne pas logger les mots de passe
logger.info(f'Password: {password}')  # ❌
```

## ⚡ Performance

### Requêtes à la base de données

```python
# ❌ N+1 queries
users = User.objects.all()
for user in users:
    print(user.profile.bio)  # 1 query par utilisateur

# ✅ Utiliser select_related
users = User.objects.select_related('profile').all()
for user in users:
    print(user.profile.bio)  # Une seule requête

# ✅ Utiliser prefetch_related pour les ForeignKey multiples
users = User.objects.prefetch_related('groups').all()
```

### Caching

```python
from django.views.decorators.cache import cache_page

# ✅ Cacher les réponses GET
@cache_page(60 * 5)  # 5 minutes
def get_users(request):
    return Response(...)

# ✅ Cacher les requêtes fréquentes
from django.core.cache import cache

def get_user_data(user_id):
    cache_key = f'user_{user_id}'
    data = cache.get(cache_key)
    
    if data is None:
        data = User.objects.get(id=user_id).to_dict()
        cache.set(cache_key, data, 60 * 5)  # 5 minutes
    
    return data
```

## 📚 Documentation

### Docstrings

```python
# ✅ Bon : docstring Google style
def create_user(email: str, password: str) -> User:
    """
    Crée un nouvel utilisateur.
    
    Args:
        email: Adresse email de l'utilisateur
        password: Mot de passe (sera hashé)
    
    Returns:
        L'objet User créé
    
    Raises:
        ValueError: Si l'email existe déjà
    
    Example:
        >>> user = create_user('test@example.com', 'password123')
        >>> user.email
        'test@example.com'
    """
    pass

# ✅ Bon : docstring pour les classes
class UserSerializer(serializers.ModelSerializer):
    """
    Sérializer pour le modèle User.
    
    Valide et transforme les données utilisateur pour l'API REST.
    """
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name']
```

### Comments

```python
# ✅ Expliquer le POURQUOI, pas le QUOI
# L'utilisateur doit être actif pour accéder à ses données
# (Django en a besoin pour is_authenticated)
if user.is_active:
    return user_data

# ❌ Commentaires redondants
# Incrémenter le compteur
counter += 1
```

### Type hints

```python
# ✅ Utiliser les type hints
from typing import Optional, List

def get_users(active_only: bool = True) -> List[User]:
    """Récupère la liste des utilisateurs"""
    pass

def get_user_by_id(user_id: int) -> Optional[User]:
    """Récupère un utilisateur par ID, None si pas trouvé"""
    pass

# ❌ Sans type hints
def get_users(active_only=True):
    pass
```

## ✅ Checklist avant commit

- [ ] Tests passent localement
- [ ] Couverture de code maintenue/améliorée
- [ ] Code suit les conventions du projet
- [ ] Pas de fichiers sensibles (secrets, .env, credentials)
- [ ] Docstrings et comments ajoutés
- [ ] Migrations créées si changement de modèle
- [ ] Pas de debugging statements (print, console.log, etc.)
- [ ] Commit message explicite

---

**Dernière mise à jour** : Mai 2026
