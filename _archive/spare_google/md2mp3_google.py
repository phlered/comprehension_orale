#!/usr/bin/env python3
"""
Script pour convertir des fichiers Markdown en MP3 avec Google Cloud Text-to-Speech.
Alternative à Azure TTS pour comparaison de qualité audio.

Usage:
    python md2mp3_google.py texte.md -l fr
    python md2mp3_google.py texte.md -l all --voix femme
    python md2mp3_google.py dialogue.md -l fr --voix homme (pour forcer)
"""

import argparse
import os
import re
import random
from pathlib import Path
from dotenv import load_dotenv
import json

try:
    from google.cloud import texttospeech
    HAS_GOOGLE = True
except ImportError:
    HAS_GOOGLE = False
    print("⚠️  Google Cloud Text-to-Speech SDK non installé. Installez avec: pip install google-cloud-texttospeech")

load_dotenv()


class GoogleVoiceConfig:
    """Configuration des voix Google Cloud pour chaque langue"""
    
    # Mapping complet des voix Google Cloud Text-to-Speech
    # Format: "langue": {"female": [...], "male": [...]}
    VOICES = {
        "fr": {
            "female": [
                "fr-FR-Neural2-A",  # Mathilda
                "fr-FR-Neural2-B",  # Chloé
                "fr-FR-Neural2-C",  # Émilie
                "fr-FR-Neural2-D",  # Olivia
                "fr-FR-Neural2-E",  # Léa
                "fr-FR-Wavenet-A",  # Standard alternative
                "fr-FR-Wavenet-B",
                "fr-FR-Wavenet-C",
                "fr-FR-Wavenet-D",
            ],
            "male": [
                "fr-FR-Neural2-F",  # Laurent
                "fr-FR-Neural2-G",  # Marc
                "fr-FR-Wavenet-E",  # Standard alternative
                "fr-FR-Wavenet-F",
                "fr-FR-Wavenet-G",
            ]
        },
        "all": {  # Allemand
            "female": [
                "de-DE-Neural2-A",  # Ziva
                "de-DE-Neural2-B",  # Hannah
                "de-DE-Neural2-C",  # Katrin
                "de-DE-Neural2-D",  # Connie
                "de-DE-Neural2-E",  # Rosalie
                "de-DE-Wavenet-A",
                "de-DE-Wavenet-B",
                "de-DE-Wavenet-C",
                "de-DE-Wavenet-D",
            ],
            "male": [
                "de-DE-Neural2-F",  # Boris
                "de-DE-Neural2-G",  # Marcus
                "de-DE-Wavenet-E",
                "de-DE-Wavenet-F",
                "de-DE-Wavenet-G",
            ]
        },
        "eng": {  # Anglais GB
            "female": [
                "en-GB-Neural2-A",  # Amy
                "en-GB-Neural2-B",  # Emma
                "en-GB-Neural2-C",  # Olivia
                "en-GB-Neural2-D",  # Ella
                "en-GB-Neural2-E",  # Lily
                "en-GB-Neural2-F",  # Charlotte
                "en-GB-Wavenet-A",
                "en-GB-Wavenet-B",
                "en-GB-Wavenet-C",
                "en-GB-Wavenet-D",
            ],
            "male": [
                "en-GB-Neural2-G",  # George
                "en-GB-Neural2-H",  # Thomas
                "en-GB-Neural2-I",  # James
                "en-GB-Wavenet-E",
                "en-GB-Wavenet-F",
                "en-GB-Wavenet-G",
                "en-GB-Wavenet-H",
            ]
        },
        "us": {  # Anglais US
            "female": [
                "en-US-Neural2-A",  # Aria
                "en-US-Neural2-C",  # Jessie
                "en-US-Neural2-E",  # Sasha
                "en-US-Neural2-F",  # Grace
                "en-US-Neural2-G",  # Zoey
                "en-US-Neural2-H",  # Ivy
                "en-US-Neural2-I",  # Jacqueline
                "en-US-Neural2-J",  # Joanna
                "en-US-Wavenet-A",
                "en-US-Wavenet-B",
                "en-US-Wavenet-C",
            ],
            "male": [
                "en-US-Neural2-B",  # Ethan
                "en-US-Neural2-D",  # Liam
                "en-US-Neural2-K",  # Kendra
                "en-US-Neural2-L",  # Lucia
                "en-US-Wavenet-D",
                "en-US-Wavenet-E",
                "en-US-Wavenet-F",
            ]
        },
        "esp": {  # Espagnol Espagne
            "female": [
                "es-ES-Neural2-A",  # Lucía
                "es-ES-Neural2-B",  # Carmen
                "es-ES-Neural2-C",  # Elsa
                "es-ES-Wavenet-A",
                "es-ES-Wavenet-B",
                "es-ES-Wavenet-C",
            ],
            "male": [
                "es-ES-Neural2-D",  # Jaime
                "es-ES-Neural2-E",  # Mateo
                "es-ES-Wavenet-D",
                "es-ES-Wavenet-E",
            ]
        },
        "hisp": {  # Espagnol Amérique Latine (Mexique)
            "female": [
                "es-MX-Neural2-A",  # Lupita
                "es-MX-Neural2-B",  # Sofía
                "es-MX-Wavenet-A",
                "es-MX-Wavenet-B",
            ],
            "male": [
                "es-MX-Neural2-C",  # Pablo
                "es-MX-Neural2-D",  # Javier
                "es-MX-Wavenet-C",
                "es-MX-Wavenet-D",
            ]
        },
        "nl": {  # Néerlandais
            "female": [
                "nl-NL-Neural2-A",  # Femke
                "nl-NL-Neural2-B",  # Josefina
                "nl-NL-Wavenet-A",
                "nl-NL-Wavenet-B",
            ],
            "male": [
                "nl-NL-Neural2-C",  # Joep
                "nl-NL-Neural2-D",  # Jeroen
                "nl-NL-Wavenet-C",
                "nl-NL-Wavenet-D",
            ]
        },
        "it": {  # Italien
            "female": [
                "it-IT-Neural2-A",  # Stella
                "it-IT-Neural2-B",  # Adriana
                "it-IT-Wavenet-A",
                "it-IT-Wavenet-B",
            ],
            "male": [
                "it-IT-Neural2-C",  # Diego
                "it-IT-Neural2-D",  # Giorgio
                "it-IT-Wavenet-C",
                "it-IT-Wavenet-D",
            ]
        },
        "co": {  # Coréen
            "female": [
                "ko-KR-Neural2-A",  # Hyesung
                "ko-KR-Neural2-B",  # Seoyeon
                "ko-KR-Wavenet-A",
                "ko-KR-Wavenet-B",
            ],
            "male": [
                "ko-KR-Neural2-C",  # Jungkook
                "ko-KR-Wavenet-C",
                "ko-KR-Wavenet-D",
            ]
        },
    }
    
    # Mapping des langues pour les codes SSML
    LANGUAGE_CODES = {
        "fr": "fr-FR",
        "all": "de-DE",
        "eng": "en-GB",
        "us": "en-US",
        "esp": "es-ES",
        "hisp": "es-MX",
        "nl": "nl-NL",
        "it": "it-IT",
        "co": "ko-KR",
    }

    @staticmethod
    def get_voice(langue, gender=None, voice_name=None):
        """Retourne une voix aléatoire basée sur la langue et le genre"""
        if voice_name:
            return voice_name
        
        if gender and gender in ["female", "male"]:
            voices = GoogleVoiceConfig.VOICES.get(langue, {}).get(gender, [])
            if voices:
                return random.choice(voices)
        
        # Si pas de genre spécifié, prendre une voix aléatoire quelconque
        all_voices = []
        for genders in GoogleVoiceConfig.VOICES.get(langue, {}).values():
            all_voices.extend(genders)
        return random.choice(all_voices) if all_voices else "en-US-Neural2-A"


class MarkdownCleaner:
    """Nettoie le Markdown avant synthèse vocale"""
    
    @staticmethod
    def clean_for_tts(text):
        """Supprime les éléments non-phonétiques du Markdown"""
        # Supprimer les équations LaTeX
        text = re.sub(r'\$[^\$]+\$', '', text)
        text = re.sub(r'\$\$[^\$]+\$\$', '', text)
        
        # Supprimer les titres Markdown (garder le contenu)
        text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
        
        # Supprimer la mise en gras/italique
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
        text = re.sub(r'\*([^*]+)\*', r'\1', text)
        text = re.sub(r'__([^_]+)__', r'\1', text)
        text = re.sub(r'_([^_]+)_', r'\1', text)
        
        # Supprimer les listes (garder le contenu)
        text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)
        
        # Supprimer les blocs de code
        text = re.sub(r'```[^`]*```', '', text, flags=re.DOTALL)
        text = re.sub(r'`[^`]+`', '', text)
        
        # Supprimer les images
        text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'\1', text)
        
        # Supprimer les liens HTML
        text = re.sub(r'<[^>]+>', '', text)
        
        # Normaliser les espaces
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text
    
    @staticmethod
    def detect_dialogue(text):
        """Détecte si le texte est un dialogue (retourne True/False)"""
        # Chercher des patterns de dialogue
        patterns = [
            r'^[""]',  # Commence par des guillemets
            r'^\s*-\s+',  # Tiret en début de ligne
            r':\s+["""]',  # Deux points suivi de guillemets
        ]
        
        lines = text.strip().split('\n')
        dialogue_lines = 0
        
        for line in lines:
            for pattern in patterns:
                if re.search(pattern, line):
                    dialogue_lines += 1
                    break
        
        # Si au moins 30% des lignes semblent être du dialogue
        return len(lines) > 0 and dialogue_lines / len(lines) > 0.3


class GoogleTTSGenerator:
    """Génère l'audio avec Google Cloud Text-to-Speech"""

    def __init__(self, langue="fr", gender=None, voice_name=None, speed=0.8, pitch=-2.0, ssml_extended=False):
        if not HAS_GOOGLE:
            raise RuntimeError("Google Cloud Text-to-Speech SDK non installé")
        
        self.langue = langue
        
        # Convertir gender de français vers anglais (femme → female, homme → male)
        if gender == "femme":
            self.gender = "female"
        elif gender == "homme":
            self.gender = "male"
        else:
            self.gender = gender
        
        self.voice_name = voice_name
        self.speed = max(0.25, min(4.0, speed))  # Google accepte 0.25 à 4.0
        self.pitch = max(-20.0, min(20.0, pitch))
        self.ssml_extended = ssml_extended
        
        # Initialiser le client Google Cloud
        try:
            self.client = texttospeech.TextToSpeechClient()
        except Exception as e:
            raise ValueError(f"Erreur d'authentification Google Cloud: {e}\n"
                           "Assurez-vous que GOOGLE_APPLICATION_CREDENTIALS est défini")

    def _select_voice(self, language_code, voice, gender):
        """Valide la voix et force un timbre du genre demandé si la voix est absente ou du mauvais genre."""
        try:
            response = self.client.list_voices(language_code=language_code)
            voices = response.voices or []
        except Exception:
            return voice

        # Map disponible pour lookup rapide
        voice_map = {v.name: v for v in voices}

        # Liste préférée selon la config (par genre)
        preferred = []
        if gender == "male":
            preferred = GoogleVoiceConfig.VOICES.get(self.langue, {}).get("male", [])
        elif gender == "female":
            preferred = GoogleVoiceConfig.VOICES.get(self.langue, {}).get("female", [])

        target = voice_map.get(voice)

        # Si la voix demandée n'existe pas ou n'est pas du bon genre, essayer la liste préférée
        def is_gender(v, g):
            if g == "male":
                return v.ssml_gender == texttospeech.SsmlVoiceGender.MALE
            if g == "female":
                return v.ssml_gender == texttospeech.SsmlVoiceGender.FEMALE
            return True

        if not target or not is_gender(target, gender):
            for name in preferred:
                v = voice_map.get(name)
                if v and is_gender(v, gender):
                    if not target:
                        print(f"ℹ️ Voix {voice} introuvable, utilisation: {v.name}")
                    else:
                        print(f"ℹ️ Voix {voice} non conforme au genre, utilisation: {v.name}")
                    target = v
                    break

        # Dernier recours: prendre une voix du genre voulu parmi Neural/Wavenet
        if not target or not is_gender(target, gender):
            for v in voices:
                if is_gender(v, gender) and ("Neural" in v.name or "Wavenet" in v.name):
                    print(f"ℹ️ Voix {voice} non trouvée, fallback: {v.name}")
                    target = v
                    break

        # Si toujours rien, garder la voix initiale
        if not target:
            return voice

        return target.name if target else voice
    
    def generate_audio_from_text(self, text, output_file, voice=None):
        """Génère un fichier MP3 à partir du texte"""
        
        if voice is None:
            voice = GoogleVoiceConfig.get_voice(self.langue, self.gender, self.voice_name)
        
        # Nettoyer le texte
        clean_text = MarkdownCleaner.clean_for_tts(text)
        
        if not clean_text:
            return False, "❌ Texte vide après nettoyage"
        
        try:
            # Si le texte est très long (>3000 chars), le diviser en chunks
            if len(clean_text) > 3000:
                return self._generate_audio_chunked(clean_text, output_file, voice)
            else:
                return self._synthesize_to_file(clean_text, output_file, voice)
        
        except Exception as e:
            return False, f"❌ Erreur TTS: {str(e)}"

    def _synthesize_to_file(self, text, output_file, voice):
        """Synthétise le texte en fichier MP3 (sans chunking)
        Ajoute des pauses SSML pour réduire l'effet robotique.

        Modes:
        - ssml_extended=False: SSML simple (pauses, éventuelle vitesse globale).
        - ssml_extended=True: variations légères par phrase; si la langue est en-US
          et que le texte est court (< 2500 chars), on applique un SSML plus riche
          avec emphases modérées et micro-variations de pitch/rate.
        """
        import html

        try:
            # Récupérer la langue
            language_code = GoogleVoiceConfig.LANGUAGE_CODES.get(self.langue, "fr-FR")
            voice = self._select_voice(language_code, voice, self.gender)

            raw = text.replace("\r", "\n")
            raw = raw.replace("\n\n", " <break time=\"650ms\"/> ")
            raw = raw.replace("\n", " ")

            escaped = html.escape(raw, quote=False)
            escaped = re.sub(r"\s+", " ", escaped).strip()

            sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", escaped) if s.strip()]

            # Mode étendu “riche” réservé à en-US sur textes courts, sinon étendu normal
            rich = self.ssml_extended and self.langue == "us" and len(escaped) < 2500 and sentences

            if rich:
                base_pct = self.speed * 100.0
                def clamp_pct(v):
                    return max(70.0, min(115.0, v))
                variants = [
                    {"pitch": "+1st", "rate": clamp_pct(base_pct * 1.03)},
                    {"pitch": "0st", "rate": clamp_pct(base_pct)},
                    {"pitch": "-1st", "rate": clamp_pct(base_pct * 0.97)},
                ]
                keywords = ["climate", "energy", "public", "transport", "water", "heat", "carbon", "food"]
                segs = []
                for i, s in enumerate(sentences):
                    v = variants[i % len(variants)]
                    # emphase modérée sur 1 mot-clé si présent
                    for kw in keywords:
                        pattern = re.compile(rf"\b{kw}\b", re.IGNORECASE)
                        if pattern.search(s):
                            s = pattern.sub(lambda m: f"<emphasis level=\"moderate\">{m.group(0)}</emphasis>", s)
                            break
                    segs.append(
                        f"<s><prosody pitch=\"{v['pitch']}\" rate=\"{v['rate']:.0f}%\">{s}</prosody></s>"
                    )
                joined = " <break time=\"260ms\"/> ".join(segs)
            elif self.ssml_extended and sentences:
                base_pct = self.speed * 100.0
                def clamp_pct(v):
                    return max(70.0, min(120.0, v))
                variants = [
                    {"pitch": "+1st", "rate": clamp_pct(base_pct * 1.04)},
                    {"pitch": "-1st", "rate": clamp_pct(base_pct * 0.96)},
                    {"pitch": "0st", "rate": clamp_pct(base_pct)},
                ]
                segs = []
                for i, s in enumerate(sentences):
                    v = variants[i % len(variants)]
                    segs.append(
                        f"<s><prosody pitch=\"{v['pitch']}\" rate=\"{v['rate']:.0f}%\">{s}</prosody></s>"
                    )
                joined = " <break time=\"280ms\"/> ".join(segs)
            else:
                if sentences:
                    joined = " <break time=\"300ms\"/> ".join(sentences)
                else:
                    joined = escaped

            rate_pct = f"{self.speed * 100:.0f}%"
            rate_attr = "" if self.ssml_extended else (f' rate="{rate_pct}"' if abs(self.speed - 1.0) > 1e-3 else "")

            ssml = (
                f"<speak>"
                f"<voice name=\"{voice}\">"
                f"<prosody{rate_attr}>{joined}</prosody>"
                f"</voice>"
                f"</speak>"
            )

            synthesis_input = texttospeech.SynthesisInput(ssml=ssml)

            # Configurer la voix
            voice_params = texttospeech.VoiceSelectionParams(
                language_code=language_code,
                name=voice
            )
            
            # Configurer l'audio (avec profil d'effets pour meilleur rendu)
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                pitch=self.pitch,
                speaking_rate=self.speed,
                effects_profile_id=["large-home-entertainment-class-device"]
            )
            
            # Générer l'audio
            response = self.client.synthesize_speech(
                input=synthesis_input,
                voice=voice_params,
                audio_config=audio_config,
                timeout=30.0
            )
            
            # Écrire le fichier MP3
            with open(output_file, "wb") as out:
                out.write(response.audio_content)
            
            return True, f"✅ Audio généré: {voice_params.name}"
        
        except Exception as e:
            # Fallback: si SSML invalide, tenter phrase par phrase avec silences
            if "Invalid SSML" in str(e):
                ok, msg = self._synthesize_sentencewise(text, output_file, voice_params.name)
                if ok:
                    return True, msg
                # Sinon, dernier recours: texte brut d'un coup
                try:
                    text_clean = text.replace("\r", " ").replace("\n", " ")
                    text_clean = re.sub(r"\s+", " ", text_clean).strip()
                    synthesis_input = texttospeech.SynthesisInput(text=text_clean)
                    response = self.client.synthesize_speech(
                        input=synthesis_input,
                        voice=voice_params,
                        audio_config=audio_config,
                        timeout=30.0
                    )
                    with open(output_file, "wb") as out:
                        out.write(response.audio_content)
                    return True, f"✅ Audio généré (fallback texte): {voice_params.name}"
                except Exception as e2:
                    return False, f"❌ Erreur TTS (fallback texte): {str(e2)}"
            return False, f"❌ Erreur TTS: {str(e)}"

    def _synthesize_sentencewise(self, text, output_file, voice_name):
        """Synthèse phrase par phrase avec insertion de silences pour améliorer la prosodie."""
        try:
            import tempfile
            from pydub import AudioSegment
            import io

            language_code = GoogleVoiceConfig.LANGUAGE_CODES.get(self.langue, "fr-FR")
            voice_params = texttospeech.VoiceSelectionParams(language_code=language_code, name=voice_name)
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                pitch=self.pitch,
                speaking_rate=self.speed,
                effects_profile_id=["large-home-entertainment-class-device"]
            )

            # Découper en phrases
            sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
            if not sentences:
                return False, "❌ Aucun segment détecté"

            combined = AudioSegment.silent(duration=0)
            pause = AudioSegment.silent(duration=450)

            for s in sentences:
                synthesis_input = texttospeech.SynthesisInput(text=s)
                resp = self.client.synthesize_speech(
                    input=synthesis_input,
                    voice=voice_params,
                    audio_config=audio_config,
                    timeout=30.0
                )
                # Charger segment depuis bytes
                seg = AudioSegment.from_file(io.BytesIO(resp.audio_content), format="mp3")
                combined += seg + pause

            combined.export(output_file, format="mp3")
            return True, f"✅ Audio généré (phrases + silences): {voice_name}"
        except Exception as e:
            # Fallback sans pydub: concat binaire simple (sans silences)
            try:
                temp_dir = Path(output_file).parent
                chunk_files = []
                sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
                language_code = GoogleVoiceConfig.LANGUAGE_CODES.get(self.langue, "fr-FR")
                voice_params = texttospeech.VoiceSelectionParams(language_code=language_code, name=voice_name)
                audio_config = texttospeech.AudioConfig(
                    audio_encoding=texttospeech.AudioEncoding.MP3,
                    pitch=self.pitch,
                    speaking_rate=self.speed,
                )
                for i, s in enumerate(sentences):
                    synthesis_input = texttospeech.SynthesisInput(text=s)
                    resp = self.client.synthesize_speech(input=synthesis_input, voice=voice_params, audio_config=audio_config, timeout=30.0)
                    cf = temp_dir / f"_sent_{i}.mp3"
                    with open(cf, "wb") as f:
                        f.write(resp.audio_content)
                    chunk_files.append(cf)
                # Concat via ffmpeg
                concat_file = temp_dir / "concat.txt"
                with open(concat_file, 'w') as f:
                    for cf in chunk_files:
                        f.write(f"file '{cf.absolute()}'\n")
                cmd = ['ffmpeg', '-f', 'concat', '-safe', '0', '-i', str(concat_file.absolute()), '-c', 'copy', '-y', output_file]
                subprocess.run(cmd, check=False)
                concat_file.unlink(missing_ok=True)
                for cf in chunk_files:
                    cf.unlink(missing_ok=True)
                return True, f"✅ Audio généré (phrases concat): {voice_name}"
            except Exception as e2:
                return False, f"❌ Erreur génération par phrases: {str(e2)}"
    
    def _generate_audio_chunked(self, text, output_file, voice):
        """Génère l'audio en divisant le texte en chunks"""
        import subprocess
        from pathlib import Path
        
        print(f"📦 Texte long ({len(text)} chars), division en chunks...")
        
        # Diviser par phrases (points, points d'exclamation, points d'interrogation)
        chunks = re.split(r'(?<=[.!?])\s+', text)
        
        # Regrouper les chunks pour atteindre ~2500 chars
        grouped_chunks = []
        current_chunk = ""
        
        for chunk in chunks:
            if len(current_chunk) + len(chunk) < 2500:
                current_chunk += " " + chunk
            else:
                if current_chunk:
                    grouped_chunks.append(current_chunk.strip())
                current_chunk = chunk
        
        if current_chunk:
            grouped_chunks.append(current_chunk.strip())
        
        chunk_files = []
        temp_dir = Path(output_file).parent
        
        for i, chunk_text in enumerate(grouped_chunks):
            chunk_file = temp_dir / f"_chunk_{i}.mp3"
            chunk_files.append(chunk_file)
            
            print(f"📝 Chunk {i+1}/{len(grouped_chunks)}: {len(chunk_text)} chars...")
            
            success, msg = self._synthesize_to_file(chunk_text, str(chunk_file), voice)
            if not success:
                for f in chunk_files:
                    f.unlink(missing_ok=True)
                return False, msg
        
        # Combiner les fichiers MP3
        try:
            concat_file = temp_dir / "concat.txt"
            with open(concat_file, 'w') as f:
                for chunk in chunk_files:
                    f.write(f"file '{chunk.absolute()}'\n")
            
            cmd = [
                'ffmpeg', '-f', 'concat', '-safe', '0',
                '-i', str(concat_file.absolute()),
                '-c', 'copy', '-y', output_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            concat_file.unlink(missing_ok=True)
            
            if result.returncode == 0:
                for chunk in chunk_files:
                    chunk.unlink(missing_ok=True)
                return True, f"✅ Audio généré (en chunks): {voice}"
            else:
                print(f"⚠️  ffmpeg error, essai combinaison binaire...")
                return self._combine_binary(chunk_files, output_file, voice)
        
        except (FileNotFoundError, subprocess.TimeoutExpired):
            print(f"⚠️  ffmpeg indisponible, essai combinaison binaire...")
            return self._combine_binary(chunk_files, output_file, voice)
    
    def _combine_binary(self, chunk_files, output_file, voice):
        """Combine les chunks avec concaténation binaire simple"""
        try:
            with open(output_file, 'wb') as outfile:
                for chunk in chunk_files:
                    with open(chunk, 'rb') as infile:
                        outfile.write(infile.read())
            
            for chunk in chunk_files:
                chunk.unlink(missing_ok=True)
            
            return True, f"✅ Audio généré (combiné): {voice}"
        
        except Exception as e:
            return False, f"❌ Erreur combinaison: {str(e)}"


class DialogueProcessor:
    """Traite les dialogues avec alternance de voix"""
    
    def __init__(self, language, gender=None, speed=1.0, pitch=-2.0, ssml_extended=False):
        self.generator = GoogleTTSGenerator(language, gender, None, speed, pitch, ssml_extended)
        self.language = language
        self.gender = gender
        self.speed = speed
        self.pitch = pitch
        self.ssml_extended = ssml_extended
        self.voices = []
    
    def process_dialogue(self, text, output_file):
        """Traite un dialogue avec voix alternées"""
        
        # Détecter les lignes de dialogue
        lines = text.strip().split('\n')
        segments = []
        
        for line in lines:
            # Nettoyer la ligne
            clean_line = line.strip()
            if not clean_line:
                continue
            
            # Extraire le texte de dialogue
            # Patterns: "texte", - texte, Nom: texte
            match = re.search(r'^[\s-]*[""""]?([^:]+)[\s:]*[""""]?(.*)$', clean_line)
            if match:
                text_content = match.group(2) if match.group(2) else match.group(1)
                text_content = text_content.strip()
                if text_content:
                    segments.append(text_content)
        
        if not segments:
            # Pas de dialogue détecté, traiter normalement
            return self.generator.generate_audio_from_text(text, output_file)
        
        # Générer les voix alternées
        print(f"🎭 Dialogue détecté ({len(segments)} segments)")
        
        import subprocess
        from pathlib import Path
        
        temp_dir = Path(output_file).parent
        segment_files = []
        
        for i, segment in enumerate(segments):
            # Alterner entre homme et femme
            gender = "male" if i % 2 == 0 else "female"
            voice = GoogleVoiceConfig.get_voice(self.language, gender)
            
            segment_file = temp_dir / f"_segment_{i}.mp3"
            segment_files.append(segment_file)
            
            gen = GoogleTTSGenerator(self.language, gender, voice, self.speed, self.pitch, self.ssml_extended)
            success, msg = gen._synthesize_to_file(segment, str(segment_file), voice)
            
            if not success:
                for f in segment_files:
                    f.unlink(missing_ok=True)
                return False, msg
        
        # Combiner
        try:
            concat_file = temp_dir / "concat.txt"
            with open(concat_file, 'w') as f:
                for seg in segment_files:
                    f.write(f"file '{seg.absolute()}'\n")
            
            cmd = [
                'ffmpeg', '-f', 'concat', '-safe', '0',
                '-i', str(concat_file.absolute()),
                '-c', 'copy', '-y', output_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            concat_file.unlink(missing_ok=True)
            
            if result.returncode == 0:
                for seg in segment_files:
                    seg.unlink(missing_ok=True)
                return True, f"✅ Dialogue généré: {len(segments)} segments"
        except:
            pass
        
        # Fallback: combinaison binaire
        with open(output_file, 'wb') as outfile:
            for seg in segment_files:
                with open(seg, 'rb') as infile:
                    outfile.write(infile.read())
        
        for seg in segment_files:
            seg.unlink(missing_ok=True)
        
        return True, f"✅ Dialogue généré (combiné): {len(segments)} segments"


def process_markdown_file(input_file, output_file, langue="fr", gender=None, voice_name=None, speed=1.0, pitch=-2.0, ssml_extended=False):
    """Traite un fichier Markdown complet (texte + vocabulaire)"""
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return False, f"❌ Erreur lecture: {str(e)}"
    
    # Extraire le corps du texte (après le frontmatter YAML)
    # Format: --- YAML --- CORPS
    parts = content.split('---')
    if len(parts) >= 3:
        body = '---'.join(parts[2:]).strip()
    else:
        body = content
    
    # Nettoyer un éventuel titre de section "Text"/"Texte"/"Texto"/"Text" en tête
    body = re.sub(r'^#+\s*(text|texte|texto|tekst|testo)\s*\n', '', body, flags=re.IGNORECASE)

    # Diviser texte et vocabulaire (multilingue)
    vocab_match = re.search(
        r'^#+\s+(vocabulaire|vocabulary|vocabulario|wortschatz|woordenschat|vocabolario|glossaire)\b',
        body,
        re.MULTILINE | re.IGNORECASE
    )
    
    if vocab_match:
        text_part = body[:vocab_match.start()].strip()
    else:
        text_part = body
    
    if not text_part:
        return False, "❌ Aucun texte trouvé"
    
    # Détecter dialogue
    is_dialogue = MarkdownCleaner.detect_dialogue(text_part)
    
    if is_dialogue:
        print("🎭 Format dialogue détecté")
        processor = DialogueProcessor(langue, gender, speed, pitch, ssml_extended)
        return processor.process_dialogue(text_part, output_file)
    else:
        print("📖 Format texte simple")
        generator = GoogleTTSGenerator(langue, gender, voice_name, speed, pitch, ssml_extended)
        return generator.generate_audio_from_text(text_part, output_file)


def main():
    parser = argparse.ArgumentParser(
        description="Convertir Markdown en MP3 avec Google Cloud Text-to-Speech",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  python md2mp3_google.py text.md -l fr
  python md2mp3_google.py text.md -l all --voix femme
  python md2mp3_google.py text.md -l us -o audio.mp3 --vitesse 0.9
        """
    )
    
    parser.add_argument("input_file", help="Fichier Markdown source")
    parser.add_argument("-l", "--langue", default="fr", 
                       choices=list(GoogleVoiceConfig.VOICES.keys()),
                       help="Langue (défaut: fr)")
    parser.add_argument("-o", "--output", help="Fichier MP3 de sortie (défaut: input_file.mp3)")
    parser.add_argument("-g", "--voix", dest="gender",
                       choices=["homme", "femme"],
                       help="Genre de voix (aléatoire si omis)")
    parser.add_argument("-v", "--voice-name", help="Nom spécifique de voix (ex: fr-FR-Neural2-A)")
    parser.add_argument("--vitesse", type=float, default=0.8,
                       help="Vitesse de lecture (0.25-4.0, défaut: 0.8)")
    parser.add_argument("--pitch", type=float, default=-2.0,
                       help="Hauteur (pitch) en demi-tons (-20 à 20, défaut: -2.0)")
    parser.add_argument("--ssml-extended", action="store_true",
                       help="Activer des variations légères de pitch/vitesse par phrase (intonation)")
    
    args = parser.parse_args()
    
    # Déterminer le fichier de sortie
    if args.output:
        output_file = args.output
    else:
        output_file = str(Path(args.input_file).with_suffix('.mp3'))
    
    print(f"🔊 Google Cloud Text-to-Speech")
    print(f"📄 Entrée: {args.input_file}")
    print(f"🎵 Sortie: {output_file}")
    print(f"🌐 Langue: {args.langue}")
    if args.gender:
        print(f"👤 Voix: {args.gender}")
    if args.voice_name:
        print(f"🎙️  Voix spécifique: {args.voice_name}")
    print(f"⏱️  Vitesse: {args.vitesse}x")
    print()
    
    success, message = process_markdown_file(
        args.input_file,
        output_file,
        langue=args.langue,
        gender=args.gender,
        voice_name=args.voice_name,
        speed=args.vitesse,
        pitch=args.pitch,
        ssml_extended=args.ssml_extended
    )
    
    print(message)
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
