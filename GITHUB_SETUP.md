# Configuration GitHub - Guide complet

## 📌 Vue d'ensemble

Ce guide explique comment configurer votre projet Django sur GitHub pour :
- ✅ Exécuter les tests automatiquement
- ✅ Vérifier la couverture de code
- ✅ Valider les migrations
- ✅ Bloquer les merges si les tests échouent
- ✅ Déployer sur PythonAnywhere (optionnel)

## 🔧 Configuration initiale de GitHub

### 1. Créer un repository GitHub

Si vous n'avez pas encore créé le repository :

```bash
# Initialiser Git (si pas fait)
git init

# Ajouter la remote
git remote add origin https://github.com/yourusername/mysite_backend.git

# Créer la branche principale
git branch -M main

# Ajouter et commit les fichiers
git add .
git commit -m "Initial commit: Django project setup with CI/CD"

# Pousser vers GitHub
git push -u origin main
```

### 2. Ajouter les secrets GitHub (variables d'environnement)

Les tests utilisent les secrets suivants. Pour les ajouter :

1. Aller à **Settings** → **Secrets and variables** → **Actions**
2. Cliquer sur **New repository secret**
3. Ajouter chaque secret :

#### Secrets à ajouter :

| Nom | Valeur | Description |
|-----|--------|-------------|
| `SECRET_KEY` | (générer avec `python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'`) | Clé secrète Django |
| `DB_NAME` | `test_db` | Nom de la BD pour les tests |
| `DB_USER` | `test_user` | Utilisateur BD pour les tests |
| `DB_PASSWORD` | `test_password` | Mot de passe BD pour les tests |
| `DB_HOST` | `127.0.0.1` | Host BD pour les tests |

**Note** : Pour les tests, une BD SQLite en mémoire est utilisée, donc ces secrets ne sont pas strictement nécessaires. Ils sont là pour la documentation.

### 3. Configurer les règles de protection de branche

1. Aller à **Settings** → **Branches**
2. Cliquer sur **Add rule** sous **Branch protection rules**
3. Entrer `main` (ou `master`) comme pattern
4. Activer :
   - ✅ **Require a pull request before merging**
   - ✅ **Require status checks to pass before merging**
   - ✅ **Require branches to be up to date before merging**
   - ✅ **Require code reviews before merging** (recommandé)
   - 📊 Sélectionner **Django Tests** comme status check requis

## 🚀 Flux de travail avec GitHub

### Développement local

```bash
# 1. Créer une branche pour votre feature
git checkout -b feature/my-new-feature

# 2. Faire vos modifications
# ... modifiez les fichiers ...

# 3. Lancer les tests localement
bash scripts/test.sh

# 4. Commit et push
git add .
git commit -m "Add new feature"
git push origin feature/my-new-feature
```

### Créer une Pull Request

1. Aller à votre repository sur GitHub
2. Cliquer sur **Compare & pull request**
3. Remplir la description :
   ```markdown
   ## Description
   Description courte de la feature
   
   ## Type de changement
   - [ ] Bug fix
   - [x] New feature
   - [ ] Breaking change
   - [ ] Documentation
   
   ## Tests
   - [x] Tests ajoutés/modifiés
   - [x] Tests passent localement
   - [x] Couverture de code vérifiée
   
   Ferme #123
   ```

4. Attendre que les tests GitHub Actions passent ✅

### Merging

Une fois que tous les checks passent :
1. Demander une review (si configuré)
2. Approuver les changements
3. Cliquer sur **Merge pull request**
4. Supprimer la branche

## 📊 Monitoring des tests

### Afficher le statut des tests

1. Aller à l'onglet **Actions** du repository
2. Voir la liste des workflows
3. Cliquer sur un workflow pour voir les détails

### Exemples de statuts

- ✅ **All checks passed** - Tous les tests passent
- ❌ **Some checks failed** - Des tests ont échoué
- ⏳ **Checks in progress** - Tests en cours

### Voir les résultats détaillés

1. Cliquer sur le workflow run
2. Voir les étapes : **Test**, **Coverage**, **Check**, etc.
3. Cliquer sur une étape pour voir les logs

## 🔍 Interpréter les résultats des tests

### ✅ Tous les tests passent

```
✅ Run tests with coverage
✅ Upload coverage to Codecov
✅ Run Django checks
✅ Collect static files
```

### ❌ Les tests échouent

Vérifier les logs pour identifier le problème :

```
FAILED accounts/tests.py::TestUserAPI::test_user_create - AssertionError
```

Actions à prendre :
1. Reproduire localement : `pytest accounts/tests.py::TestUserAPI::test_user_create`
2. Corriger le code ou le test
3. Pousser les changements

### ⚠️ Problèmes courants

#### Import Error
```
ImportError: No module named 'myapp'
```
**Solution** : S'assurer que l'app est dans `INSTALLED_APPS` dans settings/base.py

#### Database Error
```
django.db.utils.OperationalError: no such table
```
**Solution** : Les migrations s'appliquent automatiquement avec `--run-syncdb`

#### Coverage Report Missing
```
FileNotFoundError: coverage.xml
```
**Solution** : Vérifier que `pytest-cov` est installé

## 🔐 Secrets pour le déploiement (optionnel)

Si vous souhaitez déployer automatiquement sur PythonAnywhere, ajouter ces secrets :

| Nom | Valeur |
|-----|--------|
| `PYTHONANYWHERE_USERNAME` | Votre username PythonAnywhere |
| `PYTHONANYWHERE_TOKEN` | Votre API token PythonAnywhere |
| `PYTHONANYWHERE_PASSWORD` | Votre mot de passe PythonAnywhere |

## 📈 Rapports de couverture

Les rapports de couverture sont :
1. Générés à chaque test
2. Uploadés à Codecov (optionnel)
3. Affichés dans GitHub

Pour voir localement :
```bash
bash scripts/test.sh --coverage
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

## 🤝 Collaborer en équipe

### Configuration pour plusieurs développeurs

1. **Clone** du repository par chaque développeur
2. Chacun crée sa **branche feature**
3. Code review via **pull request**
4. **Merge** après validation des tests

### Bonnes pratiques

- 📝 Commits explicites : `git commit -m "Fix: user authentication bug"`
- 🔀 Rebase avant merge : `git rebase main`
- ✅ Tests avant push : `pytest`
- 📊 Garder la couverture > 80%

## 🚨 Troubleshooting

### Les tests ne se lancent pas

**Problème** : Workflow n'apparaît pas dans Actions

**Solution** :
```bash
# Vérifier le workflow YAML
cat .github/workflows/tests.yml

# Vérifier la syntaxe YAML
# Utiliser https://www.yamllint.com/
```

### Tests passent localement mais échouent sur GitHub

**Causes possibles** :
- Différence de version Python
- Variables d'environnement manquantes
- Dépendances système manquantes

**Solution** :
```bash
# Vérifier la version Python sur GitHub
# (Défini dans le workflow)

# Tester avec la même version localement
python3.12 -m venv venv-test
source venv-test/bin/activate
pip install -r requirements.txt
pytest
```

## 📚 Ressources utiles

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Django Testing Guide](https://docs.djangoproject.com/en/4.2/topics/testing/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Codecov Documentation](https://docs.codecov.io/)

## ✅ Checklist final

- [ ] Repository créé sur GitHub
- [ ] Fichier .github/workflows/tests.yml commité
- [ ] Secrets GitHub configurés (optionnel)
- [ ] Branch protection rules activées
- [ ] Premier commit poussé
- [ ] Workflow "Django Tests" visible dans Actions
- [ ] Tests passent sur GitHub ✅

---

**Dernière mise à jour** : Mai 2026
