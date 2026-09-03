#!/usr/bin/env python3
"""Zet de actuele tekstblokken uit analyse/teksten.yaml in ontwerp/prototype.html.

Het prototype heeft de bibliotheek ingebakken zodat het zonder server werkt.
Na een wijziging in teksten.yaml draai je dit script om beide gelijk te trekken.
"""

import base64
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
# Het Word-sjabloon zit ook in het prototype, zodat het scherm zonder Python een
# brief op het echte briefpapier kan opleveren.
SJABLOON = re.compile(r"/\*<sjabloon>\*/.*?/\*</sjabloon>\*/", re.S)
# Het beeldmerk in de kop van het scherm komt uit het briefpapier zelf, zodat de
# app hetzelfde merk toont als de brief en er geen los logobestand rondslingert.
LOGO = re.compile(r"/\*<logo>\*/.*?/\*</logo>\*/", re.S)
LOGOBEELD = "word/media/image1.jpeg"


def main() -> int:
    teksten = yaml.safe_load((WORTEL / "analyse" / "teksten.yaml").read_text(encoding="utf-8"))
    blokken = [
        {
            "id": b["id"], "sectie": b["sectie"],
            "v": b.get("voorwaarde") or "", "g": b.get("keuzegroep") or "",
            "o": b.get("omschrijving") or "", "stijl": b.get("stijl") or "",
            "c": bool(b.get("cursief")), "w": bool(b.get("witregel_tussen")),
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

    sjabloon = WORTEL / "sjablonen" / "brief.docx"
    if sjabloon.is_file():
        ingepakt = base64.b64encode(sjabloon.read_bytes()).decode("ascii")
        vervangen, gevonden = SJABLOON.subn(
            lambda _: f'/*<sjabloon>*/"{ingepakt}"/*</sjabloon>*/', vervangen, count=1
        )
        if not gevonden:
            print(f"Kon de markering /*<sjabloon>*/ niet vinden in {PROTOTYPE.name}.")
            return 1
    else:
        print(f"Let op: {sjabloon} bestaat niet; het scherm kan dan geen Word-bestand "
              f"maken. Maak het eerst met: python3 tools/maak_sjabloon.py")

    if sjabloon.is_file():
        import zipfile
        with zipfile.ZipFile(sjabloon) as zip_in:
            beeldmerk = base64.b64encode(zip_in.read(LOGOBEELD)).decode("ascii")
        regel = ('.merk .beeldmerk{background-image:url("data:image/jpeg;base64,'
                 + beeldmerk + '")}')
        vervangen, gevonden = LOGO.subn(
            lambda _: f"/*<logo>*/{regel}/*</logo>*/", vervangen, count=1
        )
        if not gevonden:
            print(f"Kon de markering /*<logo>*/ niet vinden in {PROTOTYPE.name}.")
            return 1

    PROTOTYPE.write_text(vervangen, encoding="utf-8")
    print(f"{len(blokken)} tekstblokken bijgewerkt in {PROTOTYPE.relative_to(WORTEL)}")
    if sjabloon.is_file():
        print(f"  sjabloon meegenomen: {len(ingepakt) // 1024} kB aan tekens")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
