#!/bin/bash
# Script pour exécuter les tests

# Charger les variables d'environnement
if [ -f ".env" ]; then
    export $(cat .env | grep -v '#' | xargs)
fi

# Activer l'environnement virtuel s'il existe
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Options par défaut
COVERAGE=false
VERBOSE=false
SPECIFIC_TEST=""

# Parser les arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --coverage|-c)
            COVERAGE=true
            shift
            ;;
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        *)
            SPECIFIC_TEST="$1"
            shift
            ;;
    esac
done

# Construire la commande pytest
CMD="pytest"

if [ -n "$SPECIFIC_TEST" ]; then
    CMD="$CMD $SPECIFIC_TEST"
fi

if [ "$COVERAGE" = true ]; then
    CMD="$CMD --cov=. --cov-report=html --cov-report=term-missing"
fi

if [ "$VERBOSE" = true ]; then
    CMD="$CMD -vv"
else
    CMD="$CMD -v"
fi

echo "🧪 Exécution des tests..."
echo "Commande: $CMD"
echo ""

$CMD

if [ "$COVERAGE" = true ]; then
    echo ""
    echo "📊 Rapport de couverture généré dans htmlcov/index.html"
fi
