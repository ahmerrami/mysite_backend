#!/bin/bash
# Script rapide pour lancer le serveur de développement

# Charger les variables d'environnement
if [ -f ".env" ]; then
    export $(cat .env | grep -v '#' | xargs)
fi

# Activer l'environnement virtuel s'il existe
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Vérifier si les migrations sont nécessaires
echo "🔍 Vérification des migrations..."
python manage.py migrate

# Lancer le serveur
echo "🚀 Lancement du serveur Django..."
echo "📍 Accédez à http://localhost:8000"
echo "👤 Admin: http://localhost:8000/admin"
echo "Appuyez sur Ctrl+C pour arrêter le serveur"
echo ""

python manage.py runserver
