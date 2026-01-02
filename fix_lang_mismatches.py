#!/usr/bin/env python3
"""Corrige les frontmatters dont la langue détectée ne correspond pas aux sections texte/vocabulaire."""
from pathlib import Path
import re

ROOT = Path(__file__).parent / "docs"

label_to_code = {
    "Text": "eng",
    "Texto": "esp",
    "Texte": "fr",
    "Tekst": "nl",
    "Testo": "it",
    "텍스트": "cor",
}

vocab_to_code = {
    "Vocabulary": "eng",
    "Vocabulario": "esp",
    "Vocabulaire": "fr",
    "Woordenschat": "nl",
    "Vocabolario": "it",
    "Wortschatz": "all",
    "어휘": "cor",
}

front_to_code = {
    "Anglais (UK)": "eng",
    "Anglais (US)": "eng",
    "Anglais": "eng",
    "Espagnol (Espagne)": "esp",
    "Espagnol (Amérique du Sud)": "esp",
    "Espagnol": "esp",
    "Français": "fr",
    "Allemand": "all",
    "Néerlandais": "nl",
    "Coréen": "cor",
    "Italien": "it",
}

code_to_display = {
    "eng": "Anglais (UK)",
    "esp": "Espagnol (Espagne)",
    "fr": "Français",
    "all": "Allemand",
    "nl": "Néerlandais",
    "cor": "Coréen",
    "it": "Italien",
}

code_to_flag = {
    "eng": "🇬🇧",
    "esp": "🇪🇸",
    "fr": "🇫🇷",
    "all": "🇩🇪",
    "nl": "🇳🇱",
    "cor": "🇰🇷",
    "it": "🇮🇹",
}

mismatches = []

for md in ROOT.glob("*/text.md"):
    text = md.read_text(encoding="utf-8")
    if not text.startswith("---"):
        continue
    parts = text.split("---", 2)
    if len(parts) < 3:
        continue
    fm_text = parts[1]
    body = parts[2]

    data = {}
    order = []
    for line in fm_text.split("\n"):
        if not line.strip() or ":" not in line:
            continue
        k, v = line.split(":", 1)
        key = k.strip()
        val = v.strip()
        data[key] = val
        order.append(key)

    front_code = front_to_code.get(data.get("langue"))

    text_label_match = re.search(r"^##\s+([^\n]+)", body, re.MULTILINE)
    text_label = text_label_match.group(1).strip() if text_label_match else ""

    vocab_label_match = re.search(r"^##\s+([^\n]+)", body.split("\n##", 1)[-1], re.MULTILINE)
    vocab_label = vocab_label_match.group(1).strip() if vocab_label_match else ""

    detected_code = vocab_to_code.get(vocab_label) or label_to_code.get(text_label)

    if detected_code and front_code and detected_code != front_code:
        new_lang = code_to_display[detected_code]
        data["langue"] = new_lang
        if "drapeau" in data:
            data["drapeau"] = code_to_flag.get(detected_code, data.get("drapeau"))
        else:
            data["drapeau"] = code_to_flag.get(detected_code, "")
        mismatches.append((md.parent.name, data.get("langue"), text_label, vocab_label))

        # Reconstituer le frontmatter
        lines = ["---"]
        for key in order:
            if key in data:
                lines.append(f"{key}: {data[key]}")
        # Ajouter les clés qui n'étaient pas présentes initialement
        for extra in data:
            if extra not in order:
                lines.append(f"{extra}: {data[extra]}")
        lines.append("---")
        lines.append(body.lstrip("\n"))
        md.write_text("\n".join(lines), encoding="utf-8")

print(f"Corrigé {len(mismatches)} fichiers")
for m in mismatches:
    print(m)
