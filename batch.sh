#!/bin/bash
# Wrapper pour batch_genmp3.py - utilise automatiquement le bon Python
# Usage:
# ./batch.sh -f prompts/prompt.md -l nl,eng -n A1 
#     ./batch.sh -f prompts/prompt.md -l nl,eng -n A1 --longueur 150
#     ./batch.sh --prompts prompts/prompts_hollandais.md --langues nl --niveau B1 --dry-run
#     ./batch.sh -f prompts/prompt.md -l eng,esp,all -n A2 -g homme
# """

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="${SCRIPT_DIR}/.venv312/bin/python"

if [ ! -f "$PYTHON" ]; then
    echo "❌ Erreur: Python venv non trouvé à $PYTHON"
    exit 1
fi

exec "$PYTHON" "${SCRIPT_DIR}/batch_genmp3.py" "$@"
