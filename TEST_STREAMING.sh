#!/bin/bash
# Test script for progressive streaming in batch_server

echo "🚀 Démarrage du test de streaming progressif"
echo ""
echo "Assurez-vous que batch_server.py est en cours d'exécution:"
echo "  python batch_server.py"
echo ""
echo "Puis visitez: http://localhost:5000"
echo ""
echo "Voici un exemple de prompts pour tester le streaming :"
echo ""
cat << 'EOF'
1. Réserver une chambre d'hôtel
2. Commander au restaurant
3. Acheter des vêtements
4. Demander l'heure
5. Passer une commande en ligne
EOF
echo ""
echo "Copie ce texte dans la section 'Entrez vos prompts' et appuie sur 'Créer'"
echo "Vous verrez maintenant les outputs s'afficher progressivement au lieu"
echo "d'attendre plusieurs minutes pour voir tous les résultats à la fin."
