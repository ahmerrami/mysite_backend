#!/bin/bash
# backup_db_daily.sh - Backup quotidien de la base de données (max 30 jours)

# ========================================
# VARIABLES DE CONFIGURATION
# ========================================

# Nom d'utilisateur sur PythonAnywhere
PA_USER="supratourstravel"

# Informations de connexion au serveur de backup distant
SERVER_USER="webmaster"                    # Utilisateur SSH sur le serveur distant
SERVER_HOST="ivyerrami.ddns.net"          # Nom de domaine ou IP du serveur distant
SERVER_PORT="40022"                        # Port SSH personnalisé (au lieu de 22)

# Chemin du fichier de log pour tracer toutes les opérations
LOG_FILE="/home/$PA_USER/backups/backup_db_daily.log"

# Chemin de l'environnement virtuel Python (contient Django et dépendances)
VENV_PATH="/home/$PA_USER/.virtualenvs/myenv"

# ========================================
# DÉBUT DE L'EXÉCUTION
# ========================================

# Ajouter une ligne de séparation dans le log pour lisibilité
echo "=====================================" >> $LOG_FILE

# Enregistrer la date et heure de début du backup dans le log
echo "$(date '+%Y-%m-%d %H:%M:%S') - Début backup DB" >> $LOG_FILE

# ========================================
# ACTIVATION DE L'ENVIRONNEMENT VIRTUEL
# ========================================

# Activer le virtualenv pour avoir accès à Django et toutes les dépendances Python
# Sans cette étape, le script utiliserait le Python système (sans les packages nécessaires)
source $VENV_PATH/bin/activate

# ========================================
# VÉRIFICATION DE L'ACTIVATION
# ========================================

# Vérifier que le virtualenv est bien activé en testant la variable $VIRTUAL_ENV
# Si la variable est vide (-z), c'est que l'activation a échoué
if [ -z "$VIRTUAL_ENV" ]; then
    # Enregistrer l'erreur dans le log
    echo "$(date '+%Y-%m-%d %H:%M:%S') - ❌ Erreur : virtualenv non activé" >> $LOG_FILE
    # Arrêter le script avec un code d'erreur (1)
    exit 1
fi

# ========================================
# EXÉCUTION DU BACKUP
# ========================================

# Se déplacer dans le répertoire du projet Django
cd /home/$PA_USER/mysite

# Exécuter la commande Django de backup de la base de données
# - manage.py : script de gestion Django
# - dbbackup : commande fournie par django-dbbackup
# - --settings : spécifie les settings de production (config SFTP, etc.)
# - >> $LOG_FILE 2>&1 : redirige la sortie standard ET les erreurs vers le log
python manage.py dbbackup --settings=mysite.settings.prod >> $LOG_FILE 2>&1

# ========================================
# VÉRIFICATION DU SUCCÈS DU BACKUP
# ========================================

# Tester le code de retour de la commande précédente
# $? contient le code de retour : 0 = succès, autre = erreur
if [ $? -eq 0 ]; then
    # Le backup a réussi, enregistrer le succès dans le log
    echo "$(date '+%Y-%m-%d %H:%M:%S') - ✅ Backup DB réussi" >> $LOG_FILE

    # ========================================
    # NETTOYAGE DES ANCIENS BACKUPS
    # ========================================

    # Se connecter au serveur distant via SSH et supprimer les fichiers de plus de 30 jours
    # - ssh -p $SERVER_PORT : connexion SSH sur le port 40022
    # - find : recherche de fichiers
    #   - /home/webmaster/backups/pythonanywhere/db/ : dossier à parcourir
    #   - -type f : seulement les fichiers (pas les dossiers)
    #   - -mtime +30 : modifiés il y a plus de 30 jours
    #   - -delete : supprimer les fichiers trouvés
    # - >> $LOG_FILE 2>&1 : rediriger la sortie vers le log
    ssh -p $SERVER_PORT $SERVER_USER@$SERVER_HOST \
        "find /home/webmaster/backups/pythonanywhere/db/ -type f -mtime +30 -delete" \
        >> $LOG_FILE 2>&1

    # Confirmer le nettoyage dans le log
    echo "$(date '+%Y-%m-%d %H:%M:%S') - 🗑️ Anciens backups supprimés (>30 jours)" >> $LOG_FILE
else
    # Le backup a échoué, enregistrer l'erreur dans le log
    echo "$(date '+%Y-%m-%d %H:%M:%S') - ❌ Erreur backup DB" >> $LOG_FILE
    # Arrêter le script avec un code d'erreur
    exit 1
fi

# ========================================
# DÉSACTIVATION DU VIRTUALENV
# ========================================

# Désactiver l'environnement virtuel pour revenir à l'environnement système
# Bonne pratique pour ne pas polluer l'environnement shell
deactivate

# ========================================
# FIN DE L'EXÉCUTION
# ========================================

# Ajouter une ligne de séparation finale dans le log
echo "=====================================" >> $LOG_FILE