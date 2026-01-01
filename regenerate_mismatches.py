#!/usr/bin/env python3
"""
Regenerates resources whose word count is outside the tolerance.
- Reads _temp_mismatches.json
- Skips Korean/French
- Reruns genmp3.py with target length per level
- Copies text.md and audio.mp3 back into the existing folder, then removes the temporary folder
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
DOCS = ROOT / "docs"
MISMATCH_PATH = ROOT / "_temp_mismatches.json"
PYTHON = ROOT / ".venv312" / "bin" / "python"
GEN_SCRIPT = ROOT / "genmp3.py"

LANG_MAP = {
    "Anglais (UK)": "eng",
    "Anglais (US)": "us",
    "Allemand": "all",
    "Espagnol (Espagne)": "esp",
    "Espagnol (Amerique du Sud)": "hisp",
    "Espagnol (Amérique du Sud)": "hisp",
    "Neerlandais": "nl",
    "Néerlandais": "nl",
    "Italien": "it",
}

EXCLUDED = {"Coreen", "Coréen", "Francais", "Français"}

EXPECTED_LENGTHS = {
    "A1": 150,
    "A2": 200,
    "B1": 250,
    "B2": 300,
    "C1": 350,
    "C2": 400,
}


def load_mismatches():
    if not MISMATCH_PATH.exists():
        raise FileNotFoundError(f"Liste introuvable: {MISMATCH_PATH}")
    data = json.loads(MISMATCH_PATH.read_text(encoding="utf-8"))
    filtered = [m for m in data if m.get("langue") not in EXCLUDED]
    return filtered


def pick_new_folder(before):
    after = set(DOCS.iterdir())
    new_dirs = [p for p in after - before if p.is_dir()]
    if not new_dirs:
        raise RuntimeError("Aucun dossier genere par genmp3.py")
    if len(new_dirs) > 1:
        # choisir le plus recent
        new_dirs.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return new_dirs[0]


def regenerate_item(item):
    lang_display = item.get("langue")
    code = LANG_MAP.get(lang_display)
    if not code:
        raise ValueError(f"Langue non supportee: {lang_display}")

    target_folder = Path(item["path"]).parent
    niveau = item.get("niveau")
    expected_len = EXPECTED_LENGTHS.get(niveau)
    prompt = item.get("prompt", "").strip()
    genre = item.get("genre", "femme").lower()
    genre_opt = "homme" if genre.startswith("h") else "femme"

    print(f"\n=== {target_folder.name} ({lang_display} {niveau}) => {expected_len} mots ===")
    before = set(DOCS.iterdir())

    cmd = [
        str(PYTHON),
        str(GEN_SCRIPT),
        "-l",
        code,
        "-p",
        prompt,
        "--niveau",
        niveau,
        "--longueur",
        str(expected_len),
        "-g",
        genre_opt,
    ]

    subprocess.run(cmd, check=True)

    new_folder = pick_new_folder(before)
    src_md = new_folder / "text.md"
    src_mp3 = new_folder / "audio.mp3"
    if not src_md.exists():
        raise FileNotFoundError(f"text.md manquant dans {new_folder}")
    if not src_mp3.exists():
        raise FileNotFoundError(f"audio.mp3 manquant dans {new_folder}")

    shutil.copy2(src_md, target_folder / "text.md")
    shutil.copy2(src_mp3, target_folder / "audio.mp3")
    shutil.rmtree(new_folder)
    print(f"Remplace dans {target_folder}")


def main():
    items = load_mismatches()
    print(f"Total a traiter (non FR/KR): {len(items)}")
    for idx, item in enumerate(items, 1):
        try:
            print(f"\n[{idx}/{len(items)}]")
            regenerate_item(item)
        except subprocess.CalledProcessError as e:
            print(f"Erreur subprocess: {e}")
            return 1
        except Exception as e:
            print(f"Erreur: {e}")
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
