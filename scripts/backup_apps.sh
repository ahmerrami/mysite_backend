#!/bin/bash

# === CONFIGURATION GÉNÉRALE ===
PROJECT_DIR=~/mysite
BACKUP_DIR=~/backups
LOG_FILE=$BACKUP_DIR/backup_apps.log
DATE=$(date +"%Y-%m-%d %H:%M:%S")
PYTHON=~/.virtualenvs/myenv/bin/python

mkdir -p $BACKUP_DIR/fournisseurs
mkdir -p $BACKUP_DIR/stages
cd $PROJECT_DIR

echo "[$DATE] --- Début du backup ---" >> $LOG_FILE

# Jour de la semaine (1=lundi ... 7=dimanche)
DAY=$(date +%u)

# === Backup fournisseurs (tous les jours sauf dimanche) ===
if [ "$DAY" -ne 2 ]; then
    JSON_FILE=$BACKUP_DIR/fournisseurs/db_$(date +"%Y%m%d_%H%M%S").json
    MEDIA_FILE=$BACKUP_DIR/fournisseurs/media_$(date +"%Y%m%d_%H%M%S").tar.gz

    if $PYTHON manage.py dumpdata fournisseurs --settings=mysite.settings.prod --indent 2 > $JSON_FILE; then
        echo "[$DATE] ✅ Fournisseurs JSON exporté : $JSON_FILE" >> $LOG_FILE
    else
        echo "[$DATE] ❌ ERREUR export JSON fournisseurs" >> $LOG_FILE
    fi

    if tar -czf $MEDIA_FILE media/fournisseurs/; then
        echo "[$DATE] ✅ Fournisseurs media sauvegardé : $MEDIA_FILE" >> $LOG_FILE
    else
        echo "[$DATE] ❌ ERREUR media fournisseurs" >> $LOG_FILE
    fi

    # Nettoyage : garder 3 JSON et 2 media
    ls -1t $BACKUP_DIR/fournisseurs/db_*.json | tail -n +4 | xargs -r rm --
    ls -1t $BACKUP_DIR/fournisseurs/media_*.tar.gz | tail -n +3 | xargs -r rm --
fi

# === Backup stages (uniquement dimanche) ===
if [ "$DAY" -eq 2 ]; then
    JSON_FILE=$BACKUP_DIR/stages/db_$(date +"%Y%m%d_%H%M%S").json
    MEDIA_FILE=$BACKUP_DIR/stages/media_$(date +"%Y%m%d_%H%M%S").tar.gz

    if $PYTHON manage.py dumpdata stages --settings=mysite.settings.prod --indent 2 > $JSON_FILE; then
        echo "[$DATE] ✅ Stages JSON exporté : $JSON_FILE" >> $LOG_FILE
    else
        echo "[$DATE] ❌ ERREUR export JSON stages" >> $LOG_FILE
    fi

    if tar -czf $MEDIA_FILE media/stages/; then
        echo "[$DATE] ✅ Stages media sauvegardé : $MEDIA_FILE" >> $LOG_FILE
    else
        echo "[$DATE] ❌ ERREUR media stages" >> $LOG_FILE
    fi

    # Nettoyage : garder 2 JSON et 2 media
    ls -1t $BACKUP_DIR/stages/db_*.json | tail -n +3 | xargs -r rm --
    ls -1t $BACKUP_DIR/stages/media_*.tar.gz | tail -n +3 | xargs -r rm --
fi

echo "[$DATE] --- Fin du backup ---" >> $LOG_FILE
echo "" >> $LOG_FILE
