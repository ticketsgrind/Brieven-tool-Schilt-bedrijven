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
import re
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

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

    onderdelen["word/document.xml"] = _vervang_body(onderdelen["word/document.xml"])

    # Een .dotx is een sjabloon; het resultaat moet een gewoon document zijn,
    # anders opent Word het als "nieuw document op basis van".
    types = onderdelen["[Content_Types].xml"].decode("utf-8")
    onderdelen["[Content_Types].xml"] = types.replace(CT_SJABLOON, CT_DOCUMENT).encode("utf-8")

    doel.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(doel, "w", zipfile.ZIP_DEFLATED) as zip_uit:
        for naam, inhoud in onderdelen.items():
            zip_uit.writestr(naam, inhoud)
    return doel


def _vervang_body(document_xml: bytes) -> bytes:
    """Zet de lussen in de body en laat de rest van het bestand ongemoeid.

    Dit gebeurt met tekstbewerking en niet door de XML in te lezen en opnieuw
    weg te schrijven. Het hoofdelement van een Word-document declareert 35
    namespaces en somt er in mc:Ignorable een aantal van op; een XML-lezer
    hernoemt de prefixen die hij zelf niet tegenkomt, waarna mc:Ignorable naar
    prefixen wijst die niet meer bestaan en Word het bestand als beschadigd
    beschouwt. Alles buiten de body blijft daarom byte voor byte gelijk --
    inclusief de verwijzingen naar de briefkop, de voetteksten en titlePg, die
    samen de eerste pagina met de Schilt-gegevens rechtsboven opmaken.
    """
    opening = re.search(rb"<w:body[^>]*>", document_xml)
    if not opening:
        raise SystemExit("geen <w:body> gevonden")
    einde = document_xml.rfind(b"</w:body>")
    if einde == -1:
        raise SystemExit("geen </w:body> gevonden")

    # De sectPr onderaan de body bewaart paginaformaat, marges, titlePg en de
    # verwijzingen naar de kop- en voetteksten. Die moet blijven staan.
    sectpr = document_xml.rfind(b"<w:sectPr", opening.end(), einde)
    staart = document_xml[sectpr:einde] if sectpr != -1 else b""

    return (document_xml[:opening.end()]
            + sjabloonbody().encode("utf-8")
            + staart
            + document_xml[einde:])


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
