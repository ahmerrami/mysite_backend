# Système de Backup Automatisé - PythonAnywhere → Serveur Local

## Vue d'ensemble

Ce système permet de sauvegarder automatiquement la base de données et les fichiers media depuis PythonAnywhere vers un serveur local avec rotation automatique des versions.

## Architecture

```
PythonAnywhere                          Serveur Local (ivyerrami.ddns.net:40022)
┌─────────────────────────┐            ┌──────────────────────────────────────┐
│ Django Application      │   SSH/SFTP │ /home/webmaster/backups/             │
│ - Database (MySQL)      │───────────>│   pythonanywhere/                    │
│ - Media files           │            │     ├── db/                          │
│                         │            │     │   ├── backup-default-*.sql     │
│ Scripts:                │            │     │   └── (30 jours de rétention)  │
│ - backup_db_daily.sh    │            │     └── media/                       │
│ - backup_media_weekly.sh│            │         ├── 20251209_020000/         │
│                         │            │         └── (10 versions)            │
└─────────────────────────┘            └──────────────────────────────────────┘
```

## Fichiers du Système

### 1. Scripts de Backup

#### `scripts/backup_db_daily.sh` (114 lignes)
- **Fonction** : Backup quotidien de la base de données MySQL
- **Méthode** : `django-dbbackup` via SFTP
- **Rétention** : 30 jours
- **Format** : `.sql` (compatible avec mysql cli et phpMyAdmin)
- **Planification** : Quotidienne (recommandé: 00:00 UTC)

#### `scripts/backup_media_weekly.sh` (248 lignes)
- **Fonction** : Backup hebdomadaire des fichiers media
- **Méthode** : `rsync` incrémental
- **Rétention** : 10 versions (≈ 2.5 mois)
- **Planification** : Hebdomadaire (recommandé: dimanche 02:00 UTC)

### 2. Configuration Django

#### `mysite/settings/prod.py`
```python
STORAGES = {
    "dbbackup": {
        "BACKEND": "storages.backends.sftpstorage.SFTPStorage",
        "OPTIONS": {
            "host": "ivyerrami.ddns.net:40022",
            "params": {
                "username": "webmaster",
                "key_filename": "/home/supratourstravel/.ssh/id_ed25519",
            },
            "root_path": "/home/webmaster/backups/pythonanywhere/db",
        },
    },
}
```

#### `mysite/settings/base.py`
- `'dbbackup'` ajouté dans `INSTALLED_APPS`

## Prérequis

### 1. Authentification SSH (✅ Configuré)
```bash
# Sur PythonAnywhere
~/.ssh/id_ed25519         # Clé privée
~/.ssh/id_ed25519.pub     # Clé publique

# Sur serveur local (ivyerrami.ddns.net)
~/.ssh/authorized_keys    # Contient la clé publique PythonAnywhere
```

### 2. Dépendances Python
Voir `requirements.txt` optimisé (16 packages essentiels):
- `django-dbbackup==5.0.1`
- `django-storages[sftp]==1.14.6`
- `mysqlclient==2.2.4`

### 3. Structure des Dossiers

#### Sur PythonAnywhere
```
/home/supratourstravel/
├── mysite_pythonanywhere/          # Application Django
│   └── media/                       # Fichiers à sauvegarder
├── backups/                         # Logs locaux
│   ├── backup_db_daily.log
│   └── backup_media_weekly.log
├── backup_db_daily.sh               # Script DB
└── backup_media_weekly.sh           # Script media
```

#### Sur Serveur Local
```
/home/webmaster/backups/pythonanywhere/
├── db/                              # Backups database
│   ├── backup-default-20251209-164015.sql
│   ├── backup-default-20251208-000002.sql
│   └── ... (30 derniers jours)
└── media/                           # Backups media
    ├── 20251209_020000/
    ├── 20251202_020000/
    └── ... (10 dernières versions)
```

## Installation sur PythonAnywhere

### Étape 1: Copier les Scripts
```bash
# Depuis votre repository local
scp -P 40022 scripts/backup_db_daily.sh supratourstravel@ssh.pythonanywhere.com:~/
scp -P 40022 scripts/backup_media_weekly.sh supratourstravel@ssh.pythonanywhere.com:~/
```

### Étape 2: Rendre Exécutables
```bash
# Sur PythonAnywhere
chmod +x ~/backup_db_daily.sh
chmod +x ~/backup_media_weekly.sh
```

### Étape 3: Tester les Scripts
```bash
# Test backup DB
./backup_db_daily.sh
cat ~/backups/backup_db_daily.log

# Test backup media
./backup_media_weekly.sh
cat ~/backups/backup_media_weekly.log
```

### Étape 4: Configurer les Tâches Planifiées

#### Dashboard PythonAnywhere → Tasks

**Backup Database (Quotidien)**
- **Command**: `/bin/bash /home/supratourstravel/backup_db_daily.sh`
- **Hour**: `00` (minuit UTC)
- **Minute**: `00`

**Backup Media (Hebdomadaire - Dimanche uniquement)**
- **Command**: `/bin/bash /home/supratourstravel/backup_media_weekly.sh`
- **Hour**: `02` (2h du matin UTC)
- **Minute**: `00`

> **Note**: PythonAnywhere Free tier permet seulement 1 tâche planifiée quotidienne.
> Pour les deux tâches, un compte payant est nécessaire, ou combiner les deux dans un script.

## Restauration des Backups

### Restauration Database

#### Méthode 1: Django dbbackup
```bash
# Sur PythonAnywhere
cd ~/mysite_pythonanywhere
source ~/.virtualenvs/myenv/bin/activate
python manage.py dbrestore --settings=mysite.settings.prod
```

#### Méthode 2: MySQL direct
```bash
# Depuis le serveur local
mysql -h supratourstravel.mysql.pythonanywhere-services.com \
      -u supratourstravel \
      -p mysite_pythonanywhere < backup-default-20251209-164015.sql
```

### Restauration Media

#### Méthode 1: rsync complet
```bash
# Du serveur local vers PythonAnywhere
rsync -avzh --progress \
      -e "ssh -p 22" \
      /home/webmaster/backups/pythonanywhere/media/20251209_020000/ \
      supratourstravel@ssh.pythonanywhere.com:~/mysite_pythonanywhere/media/
```

#### Méthode 2: Fichier spécifique
```bash
# Via scp
scp /home/webmaster/backups/pythonanywhere/media/20251209_020000/factures/facture_123.pdf \
    supratourstravel@ssh.pythonanywhere.com:~/mysite_pythonanywhere/media/factures/
```

## Monitoring et Logs

### Vérifier les Logs
```bash
# Sur PythonAnywhere
tail -f ~/backups/backup_db_daily.log
tail -f ~/backups/backup_media_weekly.log
```

### Vérifier les Backups sur le Serveur
```bash
# Depuis le serveur local
ls -lht /home/webmaster/backups/pythonanywhere/db/ | head -20
ls -lht /home/webmaster/backups/pythonanywhere/media/ | head -20
```

### Statistiques
```bash
# Taille totale des backups DB (30 derniers jours)
du -sh /home/webmaster/backups/pythonanywhere/db/

# Taille totale des backups media (10 versions)
du -sh /home/webmaster/backups/pythonanywhere/media/

# Nombre de fichiers dans le dernier backup media
find /home/webmaster/backups/pythonanywhere/media/$(ls -t /home/webmaster/backups/pythonanywhere/media/ | head -1) -type f | wc -l
```

## Politique de Rétention

| Type | Fréquence | Rétention | Espace Estimé* |
|------|-----------|-----------|----------------|
| **Database** | Quotidienne | 30 jours | ~300 MB (10 MB × 30) |
| **Media** | Hebdomadaire | 10 versions | ~10 GB (1 GB × 10) |

*Estimations basées sur la taille moyenne actuelle. Ajuster selon vos besoins.

## Sécurité

### ✅ Authentification
- SSH par clé (ed25519) sans mot de passe
- Pas de credentials en clair dans les scripts
- Utilisation de `StrictHostKeyChecking=no` (seulement pour automatisation)

### ✅ Permissions
```bash
# Sur PythonAnywhere
chmod 600 ~/.ssh/id_ed25519        # Clé privée
chmod 644 ~/.ssh/id_ed25519.pub    # Clé publique
chmod 700 ~/.ssh                    # Dossier .ssh

# Sur serveur local
chmod 600 ~/.ssh/authorized_keys    # Clés autorisées
chmod 700 ~/.ssh                     # Dossier .ssh
```

### ✅ Accès Restreint
- Serveur local derrière NAT avec port forwarding (40022)
- Seule la clé SSH de PythonAnywhere est autorisée

## Dépannage

### Erreur: "Permission denied (publickey)"
```bash
# Vérifier la clé SSH
ssh -p 40022 -i ~/.ssh/id_ed25519 webmaster@ivyerrami.ddns.net "echo OK"

# Vérifier authorized_keys sur le serveur
cat ~/.ssh/authorized_keys
```

### Erreur: "No space left on device"
```bash
# Nettoyer manuellement les anciens backups
ssh -p 40022 webmaster@ivyerrami.ddns.net
cd /home/webmaster/backups/pythonanywhere/db
find . -type f -mtime +30 -delete  # Supprimer > 30 jours
```

### Erreur: "Connection refused"
```bash
# Vérifier le serveur local est accessible
ping ivyerrami.ddns.net
nc -zv ivyerrami.ddns.net 40022
```

### Backup trop lent (rsync media)
```bash
# Utiliser compression (déjà activée avec -z)
# Exclure certains types de fichiers (si nécessaire)
rsync -avzh --progress --exclude='*.tmp' --exclude='cache/*' ...
```

## Optimisations Futures

1. **Compression différentielle** : Utiliser `rsync --link-dest` pour hardlinks entre versions
2. **Notification email** : Ajouter envoi d'email en cas d'échec
3. **Monitoring externe** : Intégrer avec un service comme UptimeRobot
4. **Backup incrémental DB** : Utiliser `mysqldump --single-transaction` avec binlogs
5. **Chiffrement** : Ajouter GPG encryption pour les backups sensibles

## Historique

- **2025-12-09** : Création des scripts backup_db_daily.sh et backup_media_weekly.sh
- **2025-12-09** : Configuration SFTP dans settings/prod.py
- **2025-12-09** : Optimisation requirements.txt (77 → 16 packages)
- **2025-12-08** : Configuration authentification SSH par clé

## Auteur

Ahmed Errami (ahmederrami@gmail.com)

## Licence

Projet interne - Tous droits réservés
