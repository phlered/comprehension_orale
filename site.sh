#!/bin/bash

# Script utilitaire pour gérer le site web de langues
# Usage: ./site.sh [command]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="$SCRIPT_DIR/.venv312/bin/python"
SITE_DIR="$SCRIPT_DIR/site_langues"

# Couleurs pour les messages
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Fonction d'aide
show_help() {
    echo -e "${BLUE}📚 Gestionnaire du site web de langues${NC}"
    echo ""
    echo "Usage: ./site.sh [command]"
    echo ""
    echo "Commandes disponibles:"
    echo "  ${GREEN}build${NC}        - Générer/régénérer le site à partir de docs/"
    echo "  ${GREEN}serve${NC}        - Lancer un serveur local sur http://localhost:8000"
    echo "  ${GREEN}open${NC}         - Ouvrir le site dans le navigateur par défaut"
    echo "  ${GREEN}stats${NC}        - Afficher les statistiques des ressources"
    echo "  ${GREEN}clean${NC}        - Nettoyer les fichiers temporaires"
    echo "  ${GREEN}deploy${NC}       - Préparer le déploiement (build + vérifications)"
    echo "  ${GREEN}help${NC}         - Afficher cette aide"
    echo ""
    echo "Exemples:"
    echo "  ./site.sh build          # Générer le site"
    echo "  ./site.sh serve          # Tester localement"
    echo "  ./site.sh deploy         # Préparer pour GitHub Pages"
}

# Générer le site
build_site() {
    echo -e "${BLUE}🔨 Génération du site web...${NC}"
    "$PYTHON" "$SCRIPT_DIR/build_site.py"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Site généré avec succès !${NC}"
        echo -e "📂 Répertoire: ${SITE_DIR}"
    else
        echo -e "${RED}❌ Erreur lors de la génération${NC}"
        exit 1
    fi
}

# Lancer un serveur local
serve_site() {
    echo -e "${BLUE}🌐 Lancement du serveur local...${NC}"
    echo -e "📍 URL: ${GREEN}http://localhost:8000${NC}"
    echo -e "⌨️  Arrêter avec ${YELLOW}Ctrl+C${NC}"
    echo ""
    
    cd "$SITE_DIR"
    "$PYTHON" -m http.server 8000
}

# Ouvrir dans le navigateur
open_site() {
    if command -v open &> /dev/null; then
        # macOS
        open "http://localhost:8000"
    elif command -v xdg-open &> /dev/null; then
        # Linux
        xdg-open "http://localhost:8000"
    elif command -v start &> /dev/null; then
        # Windows
        start "http://localhost:8000"
    else
        echo -e "${YELLOW}⚠️  Impossible d'ouvrir automatiquement le navigateur${NC}"
        echo -e "   Ouvrez manuellement: ${GREEN}http://localhost:8000${NC}"
    fi
    
    echo -e "${GREEN}✅ Ouverture du navigateur...${NC}"
}

# Afficher les statistiques
show_stats() {
    echo -e "${BLUE}📊 Statistiques des ressources${NC}"
    echo ""
    
    if [ ! -f "$SITE_DIR/metadata.json" ]; then
        echo -e "${RED}❌ Fichier metadata.json introuvable${NC}"
        echo "   Exécutez d'abord: ./site.sh build"
        exit 1
    fi
    
    # Utiliser jq si disponible, sinon grep
    if command -v jq &> /dev/null; then
        echo -e "${GREEN}Total:${NC}"
        jq -r '.total_resources' "$SITE_DIR/metadata.json" | xargs echo "  Ressources:"
        
        echo -e "\n${GREEN}Par langue:${NC}"
        jq -r '.resources | group_by(.langue) | map({langue: .[0].langue, count: length}) | .[] | "  \(.langue): \(.count) ressources"' "$SITE_DIR/metadata.json"
        
        echo -e "\n${GREEN}Par niveau:${NC}"
        jq -r '.resources | group_by(.niveau) | map({niveau: .[0].niveau, count: length}) | .[] | "  \(.niveau): \(.count) ressources"' "$SITE_DIR/metadata.json"
    else
        echo -e "${YELLOW}ℹ️  Installer jq pour des statistiques détaillées${NC}"
        echo ""
        grep -o '"total_resources": [0-9]*' "$SITE_DIR/metadata.json" | cut -d: -f2 | xargs echo "Total:"
    fi
    
    echo ""
    echo -e "Taille des ressources:"
    du -sh "$SITE_DIR/resources" 2>/dev/null || echo "  N/A"
}

# Nettoyer
clean_site() {
    echo -e "${BLUE}🧹 Nettoyage...${NC}"
    
    # Supprimer les fichiers Python compilés
    find "$SCRIPT_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
    find "$SCRIPT_DIR" -name "*.pyc" -delete 2>/dev/null
    find "$SCRIPT_DIR" -name "*.pyo" -delete 2>/dev/null
    
    # Supprimer .DS_Store
    find "$SCRIPT_DIR" -name ".DS_Store" -delete 2>/dev/null
    
    echo -e "${GREEN}✅ Nettoyage terminé${NC}"
}

# Préparer le déploiement
deploy_site() {
    echo -e "${BLUE}🚀 Préparation du déploiement...${NC}"
    echo ""
    
    # 1. Nettoyer
    echo -e "${YELLOW}1/4${NC} Nettoyage..."
    clean_site
    
    # 2. Générer le site
    echo -e "${YELLOW}2/4${NC} Génération du site..."
    build_site
    
    # 3. Vérifications
    echo -e "${YELLOW}3/4${NC} Vérifications..."
    
    # Vérifier que les fichiers essentiels existent
    files_to_check=(
        "$SITE_DIR/index.html"
        "$SITE_DIR/search.html"
        "$SITE_DIR/player.html"
        "$SITE_DIR/metadata.json"
        "$SITE_DIR/README.md"
    )
    
    all_ok=true
    for file in "${files_to_check[@]}"; do
        if [ -f "$file" ]; then
            echo -e "   ${GREEN}✓${NC} $(basename "$file")"
        else
            echo -e "   ${RED}✗${NC} $(basename "$file") manquant"
            all_ok=false
        fi
    done
    
    # Vérifier que resources existe et contient des fichiers
    if [ -d "$SITE_DIR/resources" ] && [ "$(ls -A "$SITE_DIR/resources")" ]; then
        resource_count=$(find "$SITE_DIR/resources" -name "audio.mp3" | wc -l)
        echo -e "   ${GREEN}✓${NC} $resource_count fichiers audio"
    else
        echo -e "   ${RED}✗${NC} Aucune ressource trouvée"
        all_ok=false
    fi
    
    # 4. Résumé
    echo ""
    echo -e "${YELLOW}4/4${NC} Résumé"
    
    if [ "$all_ok" = true ]; then
        echo -e "${GREEN}✅ Le site est prêt pour le déploiement !${NC}"
        echo ""
        echo "Prochaines étapes:"
        echo "  1. Commiter les changements:"
        echo "     ${BLUE}git add site_langues/${NC}"
        echo "     ${BLUE}git commit -m \"Mise à jour du site\"${NC}"
        echo ""
        echo "  2. Pousser vers GitHub:"
        echo "     ${BLUE}git push origin main${NC}"
        echo ""
        echo "  3. Attendre le déploiement GitHub Pages (1-2 min)"
        echo ""
        echo "📖 Pour plus de détails, voir: DEPLOIEMENT_GITHUB_PAGES.md"
    else
        echo -e "${RED}❌ Des problèmes ont été détectés${NC}"
        echo "   Vérifiez les erreurs ci-dessus"
        exit 1
    fi
}

# Main
case "${1:-help}" in
    build)
        build_site
        ;;
    serve)
        serve_site
        ;;
    open)
        open_site
        ;;
    stats)
        show_stats
        ;;
    clean)
        clean_site
        ;;
    deploy)
        deploy_site
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}❌ Commande inconnue: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac
