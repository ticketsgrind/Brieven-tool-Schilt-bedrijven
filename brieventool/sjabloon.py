"""Zet een samengestelde brief om in een Word-bestand.

Dit is de enige module met een externe afhankelijkheid (docxtpl). De rest van
de tool werkt zonder, zodat de logica overal te draaien en te testen is.

Het sjabloon is een gewoon Word-bestand met jullie eigen briefpapier: de
briefkop, de voettekst, de afbeeldingen en de stijlen blijven zoals ze zijn.
Er staan alleen lussen in die de secties aflopen, bijvoorbeeld:

    {% for alinea in secties.systeemomschrijving %}{{ alinea }}
    {% endfor %}

Zo hoeven de 141 tekstblokken niet in het Word-bestand onderhouden te worden;
die staan in analyse/teksten.yaml.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .samenstellen import Brief


class SjabloonFout(RuntimeError):
    """Het sjabloon ontbreekt of kan niet worden ingevuld."""


def schrijf_docx(brief: Brief, sjabloon: Path | str, doel: Path | str) -> Path:
    """Vult het Word-sjabloon met de samengestelde brief."""
    try:
        from docxtpl import DocxTemplate
    except ImportError as fout:
        raise SjabloonFout(
            "docxtpl is niet geïnstalleerd. Draai eerst: pip install -r requirements.txt"
        ) from fout

    sjabloon_pad = Path(sjabloon)
    if not sjabloon_pad.is_file():
        raise SjabloonFout(f"sjabloon {sjabloon_pad} bestaat niet")

    document = DocxTemplate(str(sjabloon_pad))
    document.render(context(brief))

    doel_pad = Path(doel)
    doel_pad.parent.mkdir(parents=True, exist_ok=True)
    document.save(str(doel_pad))
    return doel_pad


def context(brief: Brief) -> dict[str, Any]:
    """De gegevens die het sjabloon te zien krijgt.

    `secties` is een woordenboek van sectienaam naar een lijst alinea's; de rest
    zijn de losse velden zoals klantnaam en projectnummer, zodat die ook buiten
    een sectie in het sjabloon te gebruiken zijn.
    """
    gegevens: dict[str, Any] = {
        naam: waarde for naam, waarde in brief.context.items()
        if not callable(waarde)
    }
    gegevens["secties"] = brief.secties
    return gegevens
