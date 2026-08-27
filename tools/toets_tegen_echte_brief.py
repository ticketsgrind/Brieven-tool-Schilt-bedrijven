#!/usr/bin/env python3
"""Bouwt een verstuurde brief na met de tool en vergelijkt regel voor regel.

Dit is de zwaarste toets die er is: kan de tool produceren wat er werkelijk de
deur uit is gegaan? De uitkomst is geen cijfer om te halen maar een lijst met
verschillen, en elk verschil is er een van drie soorten:

  1. een gat in de bibliotheek -- een variant die in de brieven bestaat maar
     nog niet in analyse/teksten.yaml staat;
  2. maatwerk van de opsteller -- een zin die voor die ene klant is aangepast,
     en die in de tool uit een eigen alinea moet komen;
  3. een verkeerd ingevuld antwoord in het offertebestand.

Gebruik:
    python3 tools/toets_tegen_echte_brief.py <offerte.yaml> <echte-brief.docx>

De uitgewerkte brieven staan niet in git omdat er klantgegevens in staan; zie
bronbrieven/LEESMIJ.md.
"""

from __future__ import annotations

import argparse
import difflib
import re
import sys
import zipfile
from pathlib import Path

import yaml

# Het script staat in tools/; de tool zelf ligt een map hoger.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from brieventool import laad, stel_samen
from brieventool.sjabloon import schrijf_docx

# Regels uit een uitgeschreven specificatieblok. Die komen niet uit de
# bibliotheek maar uit een bijlage of een productdatabase; zie vragen.md
# beslissing 1. Ze tellen daarom niet mee in de vergelijking.
SPECIFICATIEREGEL = re.compile(
    r"^(Type|Koelvermogen|Verwarmingsvermogen|Aansluitspanning|SEER|SCOP|Koudemiddel|"
    r"Luchthoeveelheid|Geluidsniveau|Afmetingen|Paneel|Gewicht|Leiding|Afzekerwaarde|"
    r"Max\.|Nom\.|Koelen|Verwarmen|PANASONIC|TOSHIBA|Aansluiten op|Voorgevuld|"
    r"Extra vulling|Verbinding|De unit is standaard)"
)


def regels(pad: Path) -> list[str]:
    """De tekstregels van een Word-bestand, met tabs als scheidingsteken."""
    with zipfile.ZipFile(pad) as zipbestand:
        xml = zipbestand.read("word/document.xml").decode("utf-8")
    body = xml[xml.index("<w:body"):]
    uit = []
    for alinea in re.findall(r"<w:p\b[^>]*/>|<w:p\b.*?</w:p>", body, re.S):
        delen = re.findall(r"<w:t[^>]*>([^<]*)</w:t>|(<w:tab/>)", alinea)
        tekst = "".join(t or "\t" for t, _ in delen)
        tekst = re.sub(r"[\s  ]+", " ", tekst).strip()
        if tekst:
            uit.append(tekst)
    return uit


def toets(offerte_pad: Path, echt_pad: Path, sjabloon: Path, wortel: Path) -> int:
    offerte = yaml.safe_load(offerte_pad.read_text(encoding="utf-8"))
    brief = stel_samen(offerte, laad(wortel))

    import tempfile
    with tempfile.TemporaryDirectory() as tijdelijk:
        nagebouwd = schrijf_docx(brief, sjabloon, Path(tijdelijk) / "brief.docx")
        onze = regels(nagebouwd)

    echt = regels(echt_pad)
    kern = [r for r in echt if not SPECIFICATIEREGEL.match(r)]
    overgeslagen = len(echt) - len(kern)

    gelijk = sum(blok.size for blok in
                 difflib.SequenceMatcher(None, kern, onze).get_matching_blocks())
    print(f"echte brief : {len(echt)} regels"
          + (f" ({overgeslagen} regels uitgeschreven specificatie, niet meegeteld)"
             if overgeslagen else ""))
    print(f"nagebouwd   : {len(onze)} regels")
    print(f"overeenkomst: {gelijk} van {len(kern)} regels ({gelijk * 100 // max(len(kern), 1)}%)")

    ontbreekt = [r for r in kern if r not in onze]
    teveel = [r for r in onze if r not in kern]

    for kop, lijst, teken in (("Wel in de echte brief, niet in de nagebouwde", ontbreekt, "-"),
                              ("Wel in de nagebouwde brief, niet in de echte", teveel, "+")):
        print(f"\n{kop} ({len(lijst)}):")
        for regel in lijst:
            dichtbij = difflib.get_close_matches(regel, teveel if teken == "-" else ontbreekt,
                                                 n=1, cutoff=0.8)
            merk = "  (bijna gelijk aan een regel aan de andere kant)" if dichtbij else ""
            print(f"  {teken} {regel[:96]}{'…' if len(regel) > 96 else ''}{merk}")

    return 0 if not ontbreekt and not teveel else 2


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("offerte", type=Path, help="YAML met de antwoorden voor deze brief")
    ap.add_argument("echt", type=Path, help="de werkelijk verstuurde .docx")
    ap.add_argument("--sjabloon", type=Path, default=Path("sjablonen/brief.docx"))
    keuzes = ap.parse_args()

    for pad in (keuzes.offerte, keuzes.echt, keuzes.sjabloon):
        if not pad.is_file():
            print(f"Bestand niet gevonden: {pad}", file=sys.stderr)
            return 1

    return toets(keuzes.offerte, keuzes.echt, keuzes.sjabloon,
                 Path(__file__).resolve().parent.parent)


if __name__ == "__main__":
    raise SystemExit(main())
