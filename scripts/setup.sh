#!/bin/bash
# Script de configuration rapide du projet pour le développement

set -e  # Arrêter si une commande échoue

echo "🚀 Configuration du projet mysite_backend"
echo "=========================================="

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé"
    exit 1
fi

echo "✅ Python trouvé: $(python3 --version)"

# Créer l'environnement virtuel
echo ""
echo "📦 Création de l'environnement virtuel..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Environnement virtuel créé"
else
    echo "✅ Environnement virtuel existe déjà"
fi

# Activer l'environnement virtuel
echo ""
echo "🔄 Activation de l'environnement virtuel..."
source venv/bin/activate

# Mettre à jour pip
echo ""
echo "📥 Mise à jour de pip..."
pip install --upgrade pip setuptools wheel > /dev/null 2>&1

# Installer les dépendances
echo ""
echo "📦 Installation des dépendances..."
pip install -r requirements.txt > /dev/null 2>&1
pip install pytest pytest-django pytest-cov > /dev/null 2>&1
echo "✅ Dépendances installées"

# Copier le fichier .env si absent
echo ""
if [ ! -f ".env" ]; then
    echo "📝 Création du fichier .env..."
    cp .env.example .env
    echo "⚠️  Modifiez le fichier .env avec vos paramètres locaux"
else
    echo "✅ Fichier .env existe déjà"
fi

# Charger les variables d'environnement
export $(cat .env | grep -v '#' | xargs)

# Appliquer les migrations
echo ""
echo "🗄️  Application des migrations..."
python manage.py migrate

# Créer un superutilisateur (optionnel)
echo ""
echo "👤 Voulez-vous créer un superutilisateur? (y/n)"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    python manage.py createsuperuser
fi

# Collecter les fichiers statiques
echo ""
echo "📦 Collecte des fichiers statiques..."
python manage.py collectstatic --no-input > /dev/null 2>&1

echo ""
echo "=========================================="
echo "✅ Configuration terminée!"
echo ""
echo "📌 Prochaines étapes :"
echo "   1. Activer l'environnement: source venv/bin/activate"
echo "   2. Lancer le serveur: python manage.py runserver"
echo "   3. Accéder à http://localhost:8000"
echo "   4. Admin: http://localhost:8000/admin"
echo ""
echo "🧪 Pour lancer les tests:"
echo "   pytest"
echo "=========================================="
