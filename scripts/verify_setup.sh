#!/bin/bash
# Script de vérification de la configuration

echo "🔍 Vérification de la configuration du projet"
echo "=============================================="

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Compteurs
PASSED=0
FAILED=0

# Fonction de vérification
check() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅${NC} $1"
        ((PASSED++))
    else
        echo -e "${RED}❌${NC} $1"
        ((FAILED++))
    fi
}

# Vérifications
echo ""
echo "📦 Fichiers de configuration :"

[ -f "manage.py" ]
check "manage.py existe"

[ -f "requirements.txt" ]
check "requirements.txt existe"

[ -f ".env.example" ]
check ".env.example existe"

[ -f ".gitignore" ]
check ".gitignore existe"

[ -f "README.md" ]
check "README.md existe"

[ -f "pytest.ini" ]
check "pytest.ini existe"

[ -f "conftest.py" ]
check "conftest.py existe"

echo ""
echo "📁 Fichiers de guide :"

[ -f "DEPLOYMENT.md" ]
check "DEPLOYMENT.md existe"

[ -f "GITHUB_SETUP.md" ]
check "GITHUB_SETUP.md existe"

[ -f "PYTHONANYWHERE_SETUP.md" ]
check "PYTHONANYWHERE_SETUP.md existe"

[ -f "CONVENTIONS.md" ]
check "CONVENTIONS.md existe"

echo ""
echo "⚙️  Configuration Django :"

[ -f "mysite/settings/base.py" ]
check "base.py existe"

[ -f "mysite/settings/dev.py" ]
check "dev.py existe"

[ -f "mysite/settings/prod.py" ]
check "prod.py existe"

[ -f "mysite/settings/test.py" ]
check "test.py existe"

echo ""
echo "🔄 GitHub Actions :"

[ -f ".github/workflows/tests.yml" ]
check ".github/workflows/tests.yml existe"

echo ""
echo "🛠️  Scripts :"

[ -f "scripts/setup.sh" ]
check "scripts/setup.sh existe"

[ -f "scripts/run.sh" ]
check "scripts/run.sh existe"

[ -f "scripts/test.sh" ]
check "scripts/test.sh existe"

[ -x "scripts/setup.sh" ]
check "scripts/setup.sh est exécutable"

[ -x "scripts/run.sh" ]
check "scripts/run.sh est exécutable"

[ -x "scripts/test.sh" ]
check "scripts/test.sh est exécutable"

echo ""
echo "=============================================="
echo -e "Résultats : ${GREEN}$PASSED passés${NC}, ${RED}$FAILED échoués${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ Toutes les vérifications sont passées!${NC}"
    exit 0
else
    echo -e "${RED}❌ Certaines vérifications ont échoué.${NC}"
    exit 1
fi
