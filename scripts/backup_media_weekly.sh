#!/bin/bash

################################################################################
# Script: backup_media_weekly.sh
# Description: Backup hebdomadaire des fichiers media de PythonAnywhere vers 
#              le serveur local avec rsync et rotation des versions.
#              Conserve les 10 dernières versions (10 semaines = ~2.5 mois).
# 
# Auteur: Ahmed Errami
# Date: 9 décembre 2025
# Version: 1.0
#
# Installation sur PythonAnywhere:
#   1. Copier ce script dans /home/supratourstravel/backup_media_weekly.sh
#   2. Rendre exécutable: chmod +x /home/supratourstravel/backup_media_weekly.sh
#   3. Ajouter dans "Tasks" de PythonAnywhere:
#      - Command: /bin/bash /home/supratourstravel/backup_media_weekly.sh
#      - Frequency: Daily à 02:00 UTC
#      - Le script s'exécutera SEULEMENT le dimanche (configurable via BACKUP_DAY)
#
# Prérequis:
#   - Authentification SSH par clé configurée (sans mot de passe)
#   - Clé privée: /home/supratourstravel/.ssh/id_ed25519
#   - Serveur: ivyerrami.ddns.net:40022 (user: webmaster)
#   - Espace disque suffisant sur le serveur local
#
# Fonctionnement:
#   - Utilise rsync pour backup incrémental (efficace, rapide)
#   - Crée un snapshot daté à chaque exécution
#   - Conserve les 10 dernières versions
#   - Supprime automatiquement les anciens backups
#   - Logs détaillés de chaque opération
#
# Avantages de rsync vs django-dbbackup mediabackup:
#   - Pas de création de fichier temporaire local (évite saturation)
#   - Transfert incrémental (seulement les fichiers modifiés)
#   - Préservation des permissions et timestamps
#   - Beaucoup plus rapide pour les gros volumes
#
# Structure des backups sur le serveur:
#   /home/webmaster/backups/pythonanywhere/media/
#     ├── 20251209_020000/  (backup du 9 déc 2025 02:00)
#     ├── 20251216_020000/  (backup du 16 déc 2025 02:00)
#     └── ...
################################################################################

# Configuration des variables
PA_USER="supratourstravel"
SERVER_USER="webmaster"
SERVER_HOST="ivyerrami.ddns.net"
SERVER_PORT="40022"
SSH_KEY="/home/${PA_USER}/.ssh/id_ed25519"

# Chemins
SOURCE_DIR="/home/${PA_USER}/mysite/media"
DEST_BASE_DIR="/home/${SERVER_USER}/backups/pythonanywhere/media"
LOG_FILE="/home/${PA_USER}/backups/backup_media_weekly.log"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DEST_DIR="${DEST_BASE_DIR}/${TIMESTAMP}"

# Nombre de versions à conserver (4 semaines ≈ 1 mois)
KEEP_VERSIONS=4

# Jour de la semaine pour le backup (0=dimanche, 1=lundi, ..., 6=samedi)
BACKUP_DAY=0  # Dimanche par défaut

################################################################################
# Fonction: log_message
# Description: Enregistre un message avec timestamp dans le fichier de log
# Arguments:
#   $1 - Message à enregistrer
################################################################################
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

################################################################################
# Fonction: check_day_of_week
# Description: Vérifie si nous sommes le bon jour de la semaine pour le backup
# Retourne: 0 si c'est le bon jour, 1 sinon
################################################################################
check_day_of_week() {
    CURRENT_DAY=$(date +%w)  # 0=dimanche, 1=lundi, ..., 6=samedi
    
    if [ "$CURRENT_DAY" -ne "$BACKUP_DAY" ]; then
        log_message "Aujourd'hui n'est pas le jour de backup (jour actuel: $CURRENT_DAY, jour configuré: $BACKUP_DAY)"
        log_message "Backup hebdomadaire prévu pour: $(date -d "next sunday" +%A) (jour $BACKUP_DAY)"
        log_message "Script terminé sans exécution du backup"
        return 1
    fi
    
    log_message "✓ Aujourd'hui est le jour de backup hebdomadaire (jour $BACKUP_DAY)"
    return 0
}

################################################################################
# Fonction: check_prerequisites
# Description: Vérifie que tous les prérequis sont remplis avant de continuer
# Vérifie:
#   - Présence de la clé SSH
#   - Existence du dossier source (media)
#   - Connexion SSH au serveur
################################################################################
check_prerequisites() {
    log_message "=========================================="
    log_message "Début du backup media hebdomadaire"
    log_message "=========================================="
    
    # Vérifier la présence de la clé SSH
    if [ ! -f "$SSH_KEY" ]; then
        log_message "ERREUR: Clé SSH non trouvée: $SSH_KEY"
        exit 1
    fi
    
    # Vérifier l'existence du dossier source
    if [ ! -d "$SOURCE_DIR" ]; then
        log_message "ERREUR: Dossier source non trouvé: $SOURCE_DIR"
        exit 1
    fi
    
    # Tester la connexion SSH
    log_message "Test de connexion SSH au serveur..."
    if ! ssh -p "$SERVER_PORT" -i "$SSH_KEY" -o ConnectTimeout=10 -o StrictHostKeyChecking=no \
         "${SERVER_USER}@${SERVER_HOST}" "echo 'OK'" > /dev/null 2>&1; then
        log_message "ERREUR: Impossible de se connecter au serveur SSH"
        log_message "Vérifiez: ssh -p ${SERVER_PORT} ${SERVER_USER}@${SERVER_HOST}"
        exit 1
    fi
    log_message "✓ Connexion SSH réussie"
}

################################################################################
# Fonction: create_remote_directory
# Description: Crée le répertoire de destination sur le serveur distant
################################################################################
create_remote_directory() {
    log_message "Création du répertoire de destination: $DEST_DIR"
    
    if ssh -p "$SERVER_PORT" -i "$SSH_KEY" "${SERVER_USER}@${SERVER_HOST}" \
       "mkdir -p '$DEST_DIR'" 2>> "$LOG_FILE"; then
        log_message "✓ Répertoire créé avec succès"
    else
        log_message "ERREUR: Impossible de créer le répertoire distant"
        exit 1
    fi
}

################################################################################
# Fonction: perform_backup
# Description: Effectue le backup des fichiers media avec rsync
# Options rsync:
#   -a : mode archive (préserve permissions, timestamps, liens symboliques)
#   -v : mode verbeux
#   -z : compression pendant le transfert
#   -h : tailles lisibles
#   --progress : affiche la progression
#   --stats : statistiques de transfert
#   -e : spécifie la commande SSH avec port et clé
################################################################################
perform_backup() {
    log_message "Démarrage du backup rsync..."
    log_message "Source: $SOURCE_DIR"
    log_message "Destination: ${SERVER_USER}@${SERVER_HOST}:${DEST_DIR}"
    
    # Calculer la taille des données source
    SOURCE_SIZE=$(du -sh "$SOURCE_DIR" 2>/dev/null | cut -f1)
    log_message "Taille des données à sauvegarder: $SOURCE_SIZE"
    
    # Exécuter rsync avec logging
    if rsync -avzh --progress --stats \
       -e "ssh -p ${SERVER_PORT} -i ${SSH_KEY} -o StrictHostKeyChecking=no" \
       "$SOURCE_DIR/" "${SERVER_USER}@${SERVER_HOST}:${DEST_DIR}/" \
       2>&1 | tee -a "$LOG_FILE"; then
        log_message "✓ Backup rsync terminé avec succès"
        return 0
    else
        log_message "ERREUR: Échec du backup rsync"
        return 1
    fi
}

################################################################################
# Fonction: cleanup_old_backups
# Description: Supprime les backups les plus anciens, conserve les N derniers
# Arguments:
#   Utilise la variable globale KEEP_VERSIONS
# Méthode:
#   - Liste tous les backups triés par date
#   - Compte le nombre total
#   - Supprime les plus anciens si > KEEP_VERSIONS
################################################################################
cleanup_old_backups() {
    log_message "Nettoyage des anciens backups (conservation des ${KEEP_VERSIONS} derniers)..."
    
    # Compter et supprimer les anciens backups via SSH
    ssh -p "$SERVER_PORT" -i "$SSH_KEY" "${SERVER_USER}@${SERVER_HOST}" bash << EOF 2>> "$LOG_FILE"
        cd "${DEST_BASE_DIR}" || exit 1
        
        # Lister tous les backups triés par date (du plus ancien au plus récent)
        BACKUPS=\$(ls -1dt */ 2>/dev/null | tac)
        BACKUP_COUNT=\$(echo "\$BACKUPS" | wc -l)
        
        echo "Nombre total de backups: \$BACKUP_COUNT"
        
        if [ \$BACKUP_COUNT -gt ${KEEP_VERSIONS} ]; then
            TO_DELETE=\$((BACKUP_COUNT - ${KEEP_VERSIONS}))
            echo "Suppression de \$TO_DELETE ancien(s) backup(s)..."
            
            echo "\$BACKUPS" | head -n \$TO_DELETE | while read -r backup; do
                if [ -n "\$backup" ]; then
                    echo "Suppression: \$backup"
                    rm -rf "\$backup"
                fi
            done
            
            echo "✓ Nettoyage terminé"
        else
            echo "Aucun nettoyage nécessaire (\$BACKUP_COUNT backups <= ${KEEP_VERSIONS})"
        fi
EOF
    
    log_message "✓ Nettoyage terminé"
}

################################################################################
# Fonction: display_summary
# Description: Affiche un résumé du backup (taille, nombre de fichiers, etc.)
################################################################################
display_summary() {
    log_message "=========================================="
    log_message "Résumé du backup"
    log_message "=========================================="
    
    # Récupérer des statistiques du serveur distant
    ssh -p "$SERVER_PORT" -i "$SSH_KEY" "${SERVER_USER}@${SERVER_HOST}" bash << EOF | tee -a "$LOG_FILE"
        echo "Dossier de backup: ${DEST_DIR}"
        echo "Taille du backup: \$(du -sh '${DEST_DIR}' 2>/dev/null | cut -f1)"
        echo "Nombre de fichiers: \$(find '${DEST_DIR}' -type f 2>/dev/null | wc -l)"
        echo ""
        echo "Backups disponibles:"
        ls -lht '${DEST_BASE_DIR}' 2>/dev/null | head -n $((KEEP_VERSIONS + 1))
EOF
    
    log_message "=========================================="
    log_message "Backup media hebdomadaire terminé avec succès"
    log_message "=========================================="
}

################################################################################
# Fonction principale
################################################################################
main() {
    # Créer le dossier de log si nécessaire
    mkdir -p "$(dirname "$LOG_FILE")"
    
    log_message "=========================================="
    log_message "Démarrage du script backup_media_weekly.sh"
    log_message "=========================================="
    
    # Vérifier si c'est le bon jour de la semaine
    if ! check_day_of_week; then
        # Pas le bon jour, sortir silencieusement (code 0 = succès)
        exit 0
    fi
    
    # Exécuter les étapes du backup
    check_prerequisites
    create_remote_directory
    
    if perform_backup; then
        cleanup_old_backups
        display_summary
        exit 0
    else
        log_message "ERREUR: Le backup a échoué"
        exit 1
    fi
}

# Exécuter le script
main
