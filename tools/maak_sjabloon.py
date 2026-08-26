#!/usr/bin/env python3
"""Maakt het Word-sjabloon uit een van de bestaande .dotx-bestanden.

Het uitgangspunt is dat de huisstijl niet wordt nagebouwd. Een bronbrief bevat
de briefkop, de voettekst, de afbeeldingen, de paginamarges en de stijlen al;
dit script haalt alleen de brieftekst uit de body en zet er de lussen voor in
de plaats die docxtpl invult.

    python3 tools/maak_sjabloon.py
    python3 tools/maak_sjabloon.py --bron "bronbrieven/kanaal enkelvoud.dotx"

Het resultaat is sjablonen/brief.docx. Dat bestand is met opzet niet met de hand
te onderhouden: draai dit script opnieuw als de huisstijl verandert.
"""

from __future__ import annotations

import argparse
import shutil
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET
from xml.sax.saxutils import escape

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
Wq = f"{{{W}}}"

# De stijl-id's zoals ze in de bronsjablonen heten. Nederlandstalig, want de
# sjablonen zijn in een Nederlandse Word gemaakt.
STIJL_TEKST = "Standaard"
STIJL_OPSOMMING = "Lijstalinea"

CT_SJABLOON = "application/vnd.openxmlformats-officedocument.wordprocessingml.template.main+xml"
CT_DOCUMENT = "application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"


def alinea(tekst: str, *, stijl: str | None = None, vet: bool = False,
           hangend: int | None = None) -> str:
    """Bouwt één <w:p>. `tekst` mag docxtpl-tags bevatten."""
    eigenschappen = ""
    if stijl or hangend is not None:
        eigenschappen = "<w:pPr>"
        if stijl:
            eigenschappen += f'<w:pStyle w:val="{stijl}"/>'
        if hangend is not None:
            eigenschappen += f'<w:ind w:hanging="{hangend}"/>'
        eigenschappen += "</w:pPr>"
    if not tekst:
        # Met een leeg tekstelement erin, zodat de alinea niet als <w:p />
        # wordt weggeschreven; zie de uitleg bij PARAGRAAFTAG in sjabloon.py.
        return f'<w:p>{eigenschappen}<w:r><w:t xml:space="preserve"></w:t></w:r></w:p>'
    opmaak = "<w:rPr><w:b/></w:rPr>" if vet else ""
    return (f"<w:p>{eigenschappen}<w:r>{opmaak}"
            f'<w:t xml:space="preserve">{escape(tekst)}</w:t></w:r></w:p>')


def sjabloonbody() -> str:
    """De lussen die docxtpl invult.

    De kop van de brief staat er los in omdat de betreft-regel een eigen
    inspringing heeft. Alles daarna loopt door één lus, zodat een nieuwe sectie
    in teksten.yaml geen wijziging in dit sjabloon vergt.
    """
    delen: list[str] = []

    for sectie, opties in (("geadresseerde", {}),
                           ("betreft", {"vet": True, "hangend": 709}),
                           ("kenmerken", {})):
        delen += [
            alinea("{%p for a in secties." + sectie + " %}"),
            alinea("{{ a.tekst }}", **opties),
            alinea("{%p endfor %}"),
            alinea(""),
        ]

    delen += [
        alinea("{%p for a in secties.aanhef %}"),
        alinea("{{ a.tekst }}"),
        alinea("{%p endfor %}"),
        alinea(""),
        # Vanaf hier alle overige secties in volgorde. Drie vormen: een kop,
        # een opsommingsregel en een gewone alinea.
        alinea("{%p for sectie in romp %}"),
        alinea("{%p for a in sectie %}"),
        alinea("{%p if a.stijl == 'kop' %}"),
        alinea("{{ a.tekst }}", vet=True),
        alinea("{%p elif a.stijl == 'opsomming' %}"),
        alinea("{{ a.tekst }}", stijl=STIJL_OPSOMMING),
        alinea("{%p else %}"),
        alinea("{{ a.tekst }}", stijl=STIJL_TEKST),
        alinea("{%p endif %}"),
        alinea("{%p endfor %}"),
        alinea(""),
        alinea("{%p endfor %}"),
    ]
    return "".join(delen)


def bouw(bron: Path, doel: Path) -> Path:
    with zipfile.ZipFile(bron) as zip_in:
        onderdelen = {naam: zip_in.read(naam) for naam in zip_in.namelist()}

    document = ET.fromstring(onderdelen["word/document.xml"])
    body = document.find(Wq + "body")
    if body is None:
        raise SystemExit(f"{bron} heeft geen body")

    # De sectPr onderaan de body bewaart paginaformaat, marges en de verwijzingen
    # naar de kop- en voetteksten. Die moet blijven staan.
    sectpr = body.find(Wq + "sectPr")
    for kind in list(body):
        body.remove(kind)

    ET.register_namespace("w", W)
    for knoop in ET.fromstring(f'<w:root xmlns:w="{W}">{sjabloonbody()}</w:root>'):
        body.append(knoop)
    if sectpr is not None:
        body.append(sectpr)

    onderdelen["word/document.xml"] = ET.tostring(document, encoding="UTF-8", xml_declaration=True)

    # Een .dotx is een sjabloon; het resultaat moet een gewoon document zijn,
    # anders opent Word het als "nieuw document op basis van".
    types = onderdelen["[Content_Types].xml"].decode("utf-8")
    onderdelen["[Content_Types].xml"] = types.replace(CT_SJABLOON, CT_DOCUMENT).encode("utf-8")

    doel.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(doel, "w", zipfile.ZIP_DEFLATED) as zip_uit:
        for naam, inhoud in onderdelen.items():
            zip_uit.writestr(naam, inhoud)
    return doel


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bron", type=Path, default=Path("bronbrieven/wand enkelvoud.dotx"))
    ap.add_argument("--doel", type=Path, default=Path("sjablonen/brief.docx"))
    keuzes = ap.parse_args()

    if not keuzes.bron.is_file():
        print(f"Bronbestand {keuzes.bron} bestaat niet.")
        return 1

    doel = bouw(keuzes.bron, keuzes.doel)
    with zipfile.ZipFile(doel) as z:
        media = [n for n in z.namelist() if n.startswith("word/media/")]
        koppen = [n for n in z.namelist() if "header" in n or "footer" in n]
    print(f"{doel} gemaakt op basis van {keuzes.bron.name}")
    print(f"  {len(media)} afbeelding(en) en {len(koppen)} kop-/voetteksten meegenomen")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
