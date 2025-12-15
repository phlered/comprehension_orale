#!/bin/bash

# Script de lancement de l'application de compréhension orale
# Ce script installe les dépendances et lance l'application

echo "🎧 Générateur de Compréhension Orale - Allemand"
echo "================================================"
echo ""

# Vérifier si les dépendances sont installées
if ! python3 -c "import anthropic" 2>/dev/null; then
    echo "📦 Installation des dépendances..."
    pip3 install --user anthropic edge-tts python-dotenv
    echo ""
fi

# Vérifier si le fichier .env existe
if [ ! -f .env ]; then
    echo "⚠️  Le fichier .env n'existe pas encore."
    echo "📝 Pour utiliser l'IA, créez un fichier .env avec votre clé API :"
    echo "   ANTHROPIC_API_KEY=votre_clé_ici"
    echo ""
    echo "   Ou copiez .env.example : cp .env.example .env"
    echo ""
fi

# Lancer l'application
echo "🚀 Lancement de l'application..."
python3 app_comprehension_orale.py
