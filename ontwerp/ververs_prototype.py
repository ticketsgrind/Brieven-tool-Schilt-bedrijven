#!/usr/bin/env python3
"""Zet de actuele tekstblokken uit analyse/teksten.yaml in ontwerp/prototype.html.

Het prototype heeft de bibliotheek ingebakken zodat het zonder server werkt.
Na een wijziging in teksten.yaml draai je dit script om beide gelijk te trekken.
"""

import json
import re
from pathlib import Path

import yaml

WORTEL = Path(__file__).resolve().parent.parent
PROTOTYPE = WORTEL / "ontwerp" / "prototype.html"
BEGIN = "const BLOKKEN = "


def main() -> int:
    teksten = yaml.safe_load((WORTEL / "analyse" / "teksten.yaml").read_text(encoding="utf-8"))
    blokken = [
        {
            "id": b["id"], "sectie": b["sectie"],
            "v": b.get("voorwaarde") or "", "g": b.get("keuzegroep") or "",
            "o": b.get("omschrijving") or "", "t": b["tekst"].rstrip(),
        }
        for b in teksten["blokken"]
    ]
    nieuw = json.dumps(blokken, ensure_ascii=False, separators=(",", ":"))

    html = PROTOTYPE.read_text(encoding="utf-8")
    vervangen, aantal = re.subn(
        rf"{re.escape(BEGIN)}.*?;\n", f"{BEGIN}{nieuw};\n", html, count=1, flags=re.S
    )
    if not aantal:
        print(f"Kon de regel '{BEGIN}...' niet vinden in {PROTOTYPE.name}.")
        return 1

    PROTOTYPE.write_text(vervangen, encoding="utf-8")
    print(f"{len(blokken)} tekstblokken bijgewerkt in {PROTOTYPE.relative_to(WORTEL)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
