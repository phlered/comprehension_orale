#!/bin/bash

# Lancement du serveur batch UI
# Usage: ./batch_server.sh [--port 5000] [--debug]

set -e

# Déterminer le répertoire du script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Vérifier que Flask est installé
if ! .venv312/bin/python -c "import flask" 2>/dev/null; then
    echo "❌ Flask n'est pas installé"
    echo "📦 Installation de Flask..."
    .venv312/bin/pip install flask
fi

# Récupérer les arguments
PORT="${PORT:-5000}"
DEBUG="${DEBUG:-false}"

for arg in "$@"; do
    case $arg in
        --port)
            PORT="$2"
            shift 2
            ;;
        --debug)
            DEBUG="true"
            shift
            ;;
        --help)
            echo "Usage: ./batch_server.sh [options]"
            echo ""
            echo "Options:"
            echo "  --port PORT      Port du serveur (défaut: 5000)"
            echo "  --debug          Mode debug (rechargement automatique)"
            echo "  --help           Afficher cette aide"
            echo ""
            echo "Exemples:"
            echo "  ./batch_server.sh"
            echo "  ./batch_server.sh --port 8080"
            echo "  ./batch_server.sh --port 3000 --debug"
            exit 0
            ;;
    esac
done

# Lancer le serveur
echo "🚀 Démarrage du serveur batch UI sur le port $PORT..."
echo ""
echo "📌 Ouvrez http://localhost:$PORT dans votre navigateur"
echo ""

if [ "$DEBUG" = "true" ]; then
    DEBUG_FLAG="--debug"
else
    DEBUG_FLAG=""
fi

.venv312/bin/python batch_server.py --port "$PORT" $DEBUG_FLAG
