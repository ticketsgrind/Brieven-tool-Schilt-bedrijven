"""Zet een samengestelde brief om in een Word-bestand.

Het sjabloon in sjablonen/brief.docx is gemaakt uit een van de bestaande
.dotx-bestanden door tools/maak_sjabloon.py: de briefkop, de voettekst, de
afbeeldingen, de marges en de stijlen zijn die van Schilt zelf. In de body staan
alleen Jinja-lussen, zodat de tekstblokken in analyse/teksten.yaml blijven staan
en niet in een Word-bestand onderhouden hoeven te worden.

Een .docx is een zip met XML, dus invullen komt neer op: het document eruit
halen, er Jinja overheen draaien en het weer inpakken. Daar is geen aparte
Word-bibliotheek voor nodig — die bestaat vooral om tags te repareren die Word
over meerdere tekstdelen verspreidt wanneer je ze met de hand intypt, en ons
sjabloon wordt door een script gemaakt. Voor de zekerheid worden die tekstdelen
alsnog samengevoegd voordat er wordt ingevuld.
"""

from __future__ import annotations

import re
import zipfile
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

from .samenstellen import Brief

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
Wq = f"{{{W}}}"
XML_SPACE = "{http://www.w3.org/XML/1998/namespace}space"
DOCUMENT = "word/document.xml"

# Deze secties staan los in het sjabloon omdat ze een eigen plaats of
# inspringing hebben; de rest loopt door één lus.
KOPSECTIES = ("geadresseerde", "betreft", "kenmerken", "aanhef")

# Een alinea die alleen een {%p ... %}-tag bevat verdwijnt zelf uit de brief;
# alleen de tag blijft over. Zo levert een lus geen lege regels op.
#
# De (?<!/) sluit een zelfsluitende <w:p /> uit. Die heeft geen </w:p>, dus
# zonder die uitsluiting zoekt het patroon door in de volgende alinea en
# verdwijnt de lege alinea ertussen — de witregel tussen twee secties.
PARAGRAAFTAG = re.compile(
    r"<w:p\b[^>]*(?<!/)>(?:(?!</w:p>).)*?\{%p(.+?)%\}.*?</w:p>", re.S
)


class SjabloonFout(RuntimeError):
    """Het sjabloon ontbreekt of kan niet worden ingevuld."""


def schrijf_docx(brief: Brief, sjabloon: Path | str, doel: Path | str) -> Path:
    """Vult het Word-sjabloon met de samengestelde brief."""
    sjabloon_pad, doel_pad = Path(sjabloon), Path(doel)
    if not sjabloon_pad.is_file():
        raise SjabloonFout(
            f"sjabloon {sjabloon_pad} bestaat niet. "
            f"Maak het met: python3 tools/maak_sjabloon.py"
        )

    with zipfile.ZipFile(sjabloon_pad) as zip_in:
        onderdelen = {naam: zip_in.read(naam) for naam in zip_in.namelist()}
    if DOCUMENT not in onderdelen:
        raise SjabloonFout(f"{sjabloon_pad} is geen Word-bestand")

    onderdelen[DOCUMENT] = vul_document(onderdelen[DOCUMENT], context(brief))

    doel_pad.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(doel_pad, "w", zipfile.ZIP_DEFLATED) as zip_uit:
        for naam, inhoud in onderdelen.items():
            zip_uit.writestr(naam, inhoud)
    return doel_pad


def vul_document(document_xml: bytes, gegevens: dict[str, Any]) -> bytes:
    """Draait Jinja over word/document.xml en repareert de tabs."""
    try:
        from jinja2 import Environment, StrictUndefined
    except ImportError as fout:
        raise SjabloonFout(
            "jinja2 is niet geïnstalleerd. Draai eerst: pip install -r requirements.txt"
        ) from fout

    xml = _voeg_tekstdelen_samen(document_xml).decode("utf-8")
    xml = PARAGRAAFTAG.sub(lambda m: "{%" + m.group(1) + "%}", xml)

    omgeving = Environment(autoescape=True, undefined=StrictUndefined,
                           keep_trailing_newline=True)
    try:
        ingevuld = omgeving.from_string(xml).render(**gegevens)
    except Exception as fout:
        raise SjabloonFout(f"het sjabloon kon niet worden ingevuld: {fout}") from fout

    wortel = ET.fromstring(ingevuld)
    tabs_naar_word(wortel)
    ET.register_namespace("w", W)
    return ET.tostring(wortel, encoding="UTF-8", xml_declaration=True)


def context(brief: Brief) -> dict[str, Any]:
    """De gegevens die het sjabloon te zien krijgt.

    `secties` bevat elke sectie op naam, `romp` de secties die door de grote lus
    lopen: alles behalve de briefkop, en zonder de secties die leeg zijn
    gebleven — die zouden anders een lege regel opleveren.
    """
    gegevens: dict[str, Any] = {
        naam: waarde for naam, waarde in brief.context.items() if not callable(waarde)
    }
    gegevens["secties"] = brief.secties
    gegevens["romp"] = [
        alineas for naam, alineas in brief.secties.items()
        if naam not in KOPSECTIES and alineas
    ]
    return gegevens


def tabs_naar_word(wortel) -> int:
    """Zet tabtekens in de ingevulde tekst om in echte Word-tabs.

    Een tab die uit de gegevens komt belandt als los teken in een <w:t> en wordt
    door Word als spatie weergegeven. De betreft-regel en de uitlijning van de
    factureringstermijnen hangen daarvan af, dus splitsen we die tekst achteraf
    op in <w:t>- en <w:tab>-elementen. Geeft terug hoeveel tabs zijn omgezet.
    """
    omgezet = 0
    for run in wortel.iter(Wq + "r"):
        kinderen = list(run)
        if not any(k.tag == Wq + "t" and k.text and "\t" in k.text for k in kinderen):
            continue
        vervanging: list[Any] = []
        for kind in kinderen:
            if kind.tag == Wq + "t" and kind.text and "\t" in kind.text:
                stukken = kind.text.split("\t")
                omgezet += len(stukken) - 1
                for nummer, stuk in enumerate(stukken):
                    if nummer:
                        vervanging.append(ET.Element(Wq + "tab"))
                    if stuk:
                        tekst = ET.Element(Wq + "t")
                        tekst.set(XML_SPACE, "preserve")
                        tekst.text = stuk
                        vervanging.append(tekst)
            else:
                vervanging.append(kind)
        for kind in kinderen:
            run.remove(kind)
        for kind in vervanging:
            run.append(kind)
    return omgezet


def _voeg_tekstdelen_samen(document_xml: bytes) -> bytes:
    """Voegt opeenvolgende <w:t> binnen één alinea samen.

    Word knipt tekst die je met de hand intypt op in losse stukken, waardoor een
    tag als {{ a.tekst }} over meerdere elementen verspreid kan raken en Jinja
    hem niet meer herkent. Ons sjabloon wordt door een script gemaakt en heeft
    dat probleem niet, maar dit maakt het bestand ook bestand tegen een
    handmatige bewerking in Word.
    """
    wortel = ET.fromstring(document_xml)
    for alinea in wortel.iter(Wq + "p"):
        tekstdelen = [t for r in alinea.findall(Wq + "r") for t in r.findall(Wq + "t")]
        if len(tekstdelen) < 2:
            continue
        volledig = "".join(t.text or "" for t in tekstdelen)
        if "{{" not in volledig and "{%" not in volledig:
            continue
        tekstdelen[0].text = volledig
        tekstdelen[0].set(XML_SPACE, "preserve")
        for overtollig in tekstdelen[1:]:
            overtollig.text = ""
    ET.register_namespace("w", W)
    return ET.tostring(wortel, encoding="UTF-8", xml_declaration=True)
