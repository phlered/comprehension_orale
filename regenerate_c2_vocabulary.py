#!/usr/bin/env python3
"""
Script pour régénérer le vocabulaire des docs C2 qui n'en ont pas assez (< 35 mots).
Utilise GPT-4o pour extraire 35 mots de vocabulaire du texte existant.
"""

import os
import re
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class VocabularyGenerator:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
    def extract_text_from_markdown(self, text_md_content):
        """Extrait le texte principal (sans frontmatter ni vocabulaire existant)"""
        # Supprimer le frontmatter YAML
        if text_md_content.startswith('---'):
            parts = text_md_content.split('---', 2)
            if len(parts) >= 3:
                text_md_content = parts[2]
        
        # Trouver la section "Texte" ou "Text" ou "Texto", etc.
        # Extraire jusqu'à la section Vocabulaire
        match = re.search(r'##\s+(?:Texte|Text|Texto|Testo|Tekst|텍스트)(.*?)(?:##\s+(?:Vocabulaire|Vocabulary|Vocabulario|Vocabolario|Woordenschat|어휘)|$)', 
                         text_md_content, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return text_md_content
    
    def get_language_from_frontmatter(self, text_md_content):
        """Extrait la langue depuis le frontmatter"""
        match = re.search(r'langue:\s*(.+)', text_md_content)
        if match:
            return match.group(1).strip()
        return "Français"  # Default
    
    def get_prompt_from_frontmatter(self, text_md_content):
        """Extrait le prompt depuis le frontmatter"""
        match = re.search(r'prompt:\s*(.+)', text_md_content)
        if match:
            return match.group(1).strip()
        return ""
    
    def generate_vocabulary(self, langue_display, text, prompt):
        """Génère 35 mots de vocabulaire via GPT-4o"""
        
        # Map langue display → langue_code pour déterminer format
        langue_map = {
            'Français': 'fr',
            'Anglais (UK)': 'eng',
            'Anglais (US)': 'us',
            'Allemand': 'all',
            'Espagnol (Espagne)': 'esp',
            'Espagnol (Amérique du Sud)': 'hisp',
            'Néerlandais': 'nl',
            'Coréen': 'cor',
            'Italien': 'it'
        }
        langue_code = langue_map.get(langue_display, 'fr')
        
        # Déterminer la description et format selon la langue
        lang_descriptions = {
            'fr': ('en français', 'article mot_français | traduction_néerlandaise', 
                   'la maison | huis\nle chat | kat'),
            'all': ('en allemand', 'article mot_allemand | traduction_française',
                   'der Frau | la femme'),
            'eng': ('en anglais', 'mot_anglais | traduction_française',
                   'to see | voir\nhouse | maison'),
            'us': ('en anglais américain', 'mot_anglais | traduction_française',
                  'to see | voir\nhouse | maison'),
            'esp': ('en espagnol d\'Espagne', 'article mot_espagnol | traduction_française',
                   'la casa | la maison'),
            'hisp': ('en espagnol sud-américain', 'article mot_espagnol | traduction_française',
                    'la casa | la maison'),
            'nl': ('en néerlandais', 'article mot_néerlandais | traduction_française',
                  'de hond | le chien'),
            'cor': ('en coréen', 'mot_coréen → romanisation (traduction_française)',
                   '김치 → kimchi (chou fermenté épicé)'),
            'it': ('en italien', 'article mot_italien | traduction_française',
                  'la casa | la maison')
        }
        
        lang_desc, format_str, example_str = lang_descriptions.get(langue_code, lang_descriptions['fr'])
        
        vocab_prompt = f"""Analyse ce texte {lang_desc} et extrais les 35 mots les plus importants et utiles pour un apprenant.

Pour chaque mot :
- Choisis des mots clés représentatifs du contenu sur le thème "{prompt}"
- Privilégie les noms, verbes et adjectifs importants
"""
        
        # Consignes spécifiques par langue
        if langue_code == "all":
            vocab_prompt += "- Pour les noms allemands, INDIQUE TOUJOURS l'article défini (der/die/das) devant le mot\n"
            vocab_prompt += "Format strict (un mot par ligne) :\narticle mot_allemand | traduction_française\n\nExemple:\nder Frau | la femme\n"
        elif langue_code in ["eng", "us"]:
            vocab_prompt += "- Pour les verbes anglais, indique 'to' avant le verbe\n"
            vocab_prompt += "- NE PAS mettre d'article devant les noms anglais\n"
            vocab_prompt += "Format strict (un mot par ligne) :\nmot_anglais | traduction_française\n\nExemple:\nto see | voir\nhouse | maison\n"
        elif langue_code in ["esp", "hisp"]:
            vocab_prompt += "- Pour les noms espagnols, INDIQUE TOUJOURS l'article défini (el/la/los/las) devant le mot\n"
            vocab_prompt += "Format strict (un mot par ligne) :\narticle mot_espagnol | traduction_française\n\nExemple:\nla casa | la maison\nel perro | le chien\n"
        elif langue_code == "nl":
            vocab_prompt += "- Pour les noms néerlandais, INDIQUE TOUJOURS l'article défini (de/het) devant le mot\n"
            vocab_prompt += "Format strict (un mot par ligne) :\narticle mot_néerlandais | traduction_française\n\nExemple:\nde hond | le chien\nhet huis | la maison\n"
        elif langue_code == "fr":
            vocab_prompt += "- Pour les noms français, INDIQUE TOUJOURS l'article défini (le/la/les) devant le mot\n"
            vocab_prompt += "- La TRADUCTION doit être en NÉERLANDAIS (pas en français)\n"
            vocab_prompt += "Format strict (un mot par ligne) :\narticle mot_français | traduction_néerlandaise\n\nExemples:\nla maison | huis\nle chat | kat\n"
        elif langue_code == "cor":
            vocab_prompt += "- Pour chaque mot coréen, donne d'abord la romanisation (phonétique), puis la traduction en français\n"
            vocab_prompt += "Format strict (un mot par ligne) :\nmot_coréen → romanisation (traduction_française)\n\nExemple:\n김치 → kimchi (chou fermenté épicé)\n불고기 → bulgogi (viande marinée grillée)\n"
        elif langue_code == "it":
            vocab_prompt += "- Pour les noms italiens, INDIQUE TOUJOURS l'article défini (il/la/lo/gli/le) devant le mot\n"
            vocab_prompt += "Format strict (un mot par ligne) :\narticle mot_italien | traduction_française\n\nExemple:\nla casa | la maison\nil gatto | le chat\n"
        else:
            vocab_prompt += "- Pour les noms, INDIQUE l'article défini devant le mot si la langue l'utilise\n"
            vocab_prompt += "Format strict (un mot par ligne) :\nmot_langue | traduction_française\n\nExemple:\nword | traduction\n"

        vocab_prompt += f"\nTEXTE :\n{text}\n\nDonne uniquement la liste des 35 mots au format demandé, sans numérotation, sans commentaire."
        
        print(f"  📚 Génération de 35 mots de vocabulaire via GPT-4o...")
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": vocab_prompt}],
            max_tokens=1024
        )
        
        vocabulary = []
        for line in response.choices[0].message.content.strip().split('\n'):
            separator = '→' if '→' in line else '|'
            if separator in line:
                parts = line.split(separator)
                if len(parts) >= 2:
                    word = parts[0].strip().strip('*').strip('-').strip()
                    translation = parts[1].strip().strip('*').strip('-').strip()
                    if word and translation:
                        vocabulary.append((word, translation))
        
        return vocabulary
    
    def update_text_md(self, text_md_path):
        """Met à jour le fichier text.md avec le nouveau vocabulaire"""
        with open(text_md_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extraire informations
        langue = self.get_language_from_frontmatter(content)
        prompt = self.get_prompt_from_frontmatter(content)
        text = self.extract_text_from_markdown(content)
        
        print(f"  📖 Langue: {langue}")
        print(f"  📝 Prompt: {prompt}")
        
        # Générer vocabulaire
        vocabulary = self.generate_vocabulary(langue, text, prompt)
        
        # Reconstituer le contenu sans la vieille section vocabulaire
        # Supprimer la vieille section vocabulaire
        content = re.sub(
            r'##\s+(?:Vocabulaire|Vocabulary|Vocabulario|Vocabolario|Woordenschat|어휘).*',
            '',
            content,
            flags=re.DOTALL | re.IGNORECASE
        ).rstrip()
        
        # Ajouter la nouvelle section vocabulaire
        content += "\n\n## Vocabulaire\n\n" if langue == "Français" else "\n\n## Vocabulary\n\n"
        if langue == "Allemand":
            content += "\n\n## Wortschatz\n\n"
        elif langue in ["Anglais (UK)", "Anglais (US)"]:
            content += "\n\n## Vocabulary\n\n"
        elif langue in ["Espagnol (Espagne)", "Espagnol (Amérique du Sud)"]:
            content += "\n\n## Vocabulario\n\n"
        elif langue == "Néerlandais":
            content += "\n\n## Woordenschat\n\n"
        elif langue == "Coréen":
            content += "\n\n## 어휘\n\n"
        elif langue == "Italien":
            content += "\n\n## Vocabolario\n\n"
        
        for word, translation in vocabulary:
            content += f"- **{word}** → {translation}\n"
        
        # Sauvegarder
        with open(text_md_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"  ✅ {len(vocabulary)} mots de vocabulaire générés et sauvegardés")
        return len(vocabulary)

def main():
    gen = VocabularyGenerator()
    
    # Trouver les docs C2 avec moins de 35 mots de vocabulaire
    docs_to_fix = []
    for root, dirs, files in os.walk('docs'):
        if 'text.md' in files:
            text_path = os.path.join(root, 'text.md')
            with open(text_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'niveau: C2' in content:
                    vocab_count = len(re.findall(r'^- \*\*.+?\*\*', content, re.MULTILINE))
                    if vocab_count < 35:
                        folder_name = os.path.basename(root)
                        docs_to_fix.append((text_path, folder_name, vocab_count))
    
    if not docs_to_fix:
        print("✅ Tous les docs C2 ont 35 mots de vocabulaire ou plus.")
        return
    
    print(f"\n🔧 {len(docs_to_fix)} doc(s) C2 à réparer:\n")
    
    for text_path, folder_name, current_vocab in docs_to_fix:
        print(f"📁 {folder_name}")
        print(f"  Vocabulaire actuel: {current_vocab}/35")
        
        vocab_count = gen.update_text_md(text_path)
        
        if vocab_count >= 35:
            print(f"  ✅ RÉPARÉ: {vocab_count} mots générés\n")
        else:
            print(f"  ⚠️  ATTENTION: Seulement {vocab_count} mots générés (attendu 35)\n")

if __name__ == "__main__":
    main()
