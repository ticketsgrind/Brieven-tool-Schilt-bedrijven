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
# Expliciete markeringen rond de blokkenlijst. Een patroon dat tot het eerste
# ";" op een regeleinde zocht ging mis: dat teken staat ook aan het eind van een
# opsommingsregel in de brieftekst, waardoor maar een deel werd vervangen.
BLOKKEN = re.compile(r"/\*<blokken>\*/.*?/\*</blokken>\*/", re.S)


def main() -> int:
    teksten = yaml.safe_load((WORTEL / "analyse" / "teksten.yaml").read_text(encoding="utf-8"))
    blokken = [
        {
            "id": b["id"], "sectie": b["sectie"],
            "v": b.get("voorwaarde") or "", "g": b.get("keuzegroep") or "",
            "o": b.get("omschrijving") or "", "stijl": b.get("stijl") or "",
            "t": b["tekst"].rstrip(),
        }
        for b in teksten["blokken"]
    ]
    nieuw = json.dumps(blokken, ensure_ascii=False, separators=(",", ":"))

    html = PROTOTYPE.read_text(encoding="utf-8")
    # De vervanging als functie doorgeven: re.sub leest backslashes in een
    # vervangtekst als stuurcodes, waardoor elke \n in de blokteksten een echte
    # regelovergang zou worden midden in een JavaScript-string.
    vervangen, aantal = BLOKKEN.subn(
        lambda _: f"/*<blokken>*/{nieuw}/*</blokken>*/", html, count=1
    )
    if not aantal:
        print(f"Kon de markering /*<blokken>*/ niet vinden in {PROTOTYPE.name}.")
        return 1

    PROTOTYPE.write_text(vervangen, encoding="utf-8")
    print(f"{len(blokken)} tekstblokken bijgewerkt in {PROTOTYPE.relative_to(WORTEL)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
