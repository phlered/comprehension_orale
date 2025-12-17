#!/bin/bash
# Wrapper pour batch_genmp3.py - utilise automatiquement le bon Python

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="${SCRIPT_DIR}/.venv312/bin/python"

if [ ! -f "$PYTHON" ]; then
    echo "❌ Erreur: Python venv non trouvé à $PYTHON"
    exit 1
fi

exec "$PYTHON" "${SCRIPT_DIR}/batch_genmp3.py" "$@"
