#!/bin/bash
# Générer 10 documents en italien A1

source .venv312/bin/activate

echo "🚀 Génération de 10 documents en italien (A1, 150 mots, vitesse 0.7)"
echo "=================================================================="

declare -a prompts=("L'alimentazione" "La famiglia" "Viaggiare in Italia" "Dove si trova il campeggio" "Gli animali domestici" "I giorni della settimana" "In albergo" "I colori" "Comprare i vestiti" "Presentarsi")
declare -a genders=("femme" "homme" "femme" "homme" "femme" "homme" "femme" "homme" "femme" "homme")

for i in "${!prompts[@]}"; do
  idx=$((i + 1))
  prompt="${prompts[$i]}"
  gender="${genders[$i]}"
  
  echo "$idx️⃣  $prompt ($gender)..."
  python genmp3.py -l it -p "$prompt" --longueur 150 --niveau A1 -g "$gender" --vitesse 0.7 > /dev/null 2>&1
  
  if [ $? -eq 0 ]; then
    echo "✅ Fait"
  else
    echo "⚠️  Tentative suivante..."
    sleep 5
    python genmp3.py -l it -p "$prompt" --longueur 150 --niveau A1 -g "$gender" --vitesse 0.7 > /dev/null 2>&1
    if [ $? -eq 0 ]; then
      echo "✅ Fait (retry)"
    else
      echo "❌ Erreur"
    fi
  fi
  
  # Attendre entre les générations
  sleep 10
done

echo ""
echo "=================================================================="
echo "✨ Batch complété!"
