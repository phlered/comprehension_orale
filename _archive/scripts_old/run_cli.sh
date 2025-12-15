#!/bin/bash
# Script de démarrage pour app.py CLI
# Vérifie l'environnement Python et lance le script

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Chemin du venv
VENV_BIN=".venv312/bin/python"
PYTHON_CMD="$VENV_BIN"

# Vérifier que le venv existe
if [ ! -f "$PYTHON_CMD" ]; then
    echo "❌ Environnement Python non trouvé"
    echo "Veuillez d'abord configurer l'environnement avec:"
    echo "  python3 -m venv .venv312"
    echo "  .venv312/bin/pip install openai edge-tts python-dotenv"
    exit 1
fi

# Vérifier que .env existe
if [ ! -f ".env" ]; then
    echo "⚠️  Fichier .env non trouvé"
    echo "Créez un fichier .env avec:"
    echo "  OPENAI_API_KEY=sk-..."
    exit 1
fi

# Lancer l'application
"$PYTHON_CMD" app.py "$@"
