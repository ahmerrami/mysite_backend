#!/bin/bash

# === CONFIGURATION ===
PROJECT_DIR=~/mysite
BACKUP_DIR=~/backups
LOG_FILE=$BACKUP_DIR/backup.log
DATE=$(date +"%Y-%m-%d %H:%M:%S")
PYTHON=~/.virtualenvs/myenv/bin/python

# Vérifier si on est samedi (6 = samedi)
if [ $(date +%u) -ne 6 ]; then
    exit 0
fi

# Créer le dossier de sauvegarde s'il n'existe pas
mkdir -p $BACKUP_DIR
cd $PROJECT_DIR# Vérifier si on est samedi (6 = samedi)
if [ $(date +%u) -ne 6 ]; then
    echo "[$DATE] Backup non exécuté (seulement le samedi)" >> $LOG_FILE
    exit 0
fi

# === Début log ===
echo "[$DATE] --- Début du backup ---" >> $LOG_FILE

# Sauvegarde de la base Django en JSON
JSON_FILE=$BACKUP_DIR/db_$(date +"%Y%m%d_%H%M%S").json
if $PYTHON manage.py dumpdata --settings=mysite.settings.prod --natural-primary --natural-foreign --indent 2 > $JSON_FILE; then
    echo "[$DATE] Base exportée : $JSON_FILE" >> $LOG_FILE
else
    echo "[$DATE] ❌ ERREUR lors de l’export JSON" >> $LOG_FILE
fi

# Sauvegarde du dossier media
MEDIA_FILE=$BACKUP_DIR/media_$(date +"%Y%m%d_%H%M%S").tar.gz
if tar -czf $MEDIA_FILE media/; then
    echo "[$DATE] Media sauvegardé : $MEDIA_FILE" >> $LOG_FILE
else
    echo "[$DATE] ❌ ERREUR lors de la sauvegarde media" >> $LOG_FILE
fi

# Nettoyage des vieux backups
ls -1t $BACKUP_DIR/db_*.json | tail -n +4 | xargs -r rm -- && \
echo "[$DATE] Nettoyage : conservé 3 derniers JSON" >> $LOG_FILE

ls -1t $BACKUP_DIR/media_*.tar.gz | tail -n +2 | xargs -r rm -- && \
echo "[$DATE] Nettoyage : conservé 1 seul media" >> $LOG_FILE

# === Fin log ===
echo "[$DATE] --- Fin du backup ---" >> $LOG_FILE
echo "" >> $LOG_FILE