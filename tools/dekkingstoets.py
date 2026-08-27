#!/usr/bin/env python3
"""Meet hoeveel van de bestaande brieven de tekstblokkenbibliotheek dekt.

Anders dan tools/toets_tegen_echte_brief.py is hiervoor geen ingevuld
offertebestand nodig. Deze toets pakt elke alinea uit een brief en kijkt of er
in analyse/teksten.yaml een blok staat dat hem kan voortbrengen, met de
plaatshouders als jokers. Zo is in een keer over alle brieven te zien wat er
nog ontbreekt, en of een gat eenmalig is of overal terugkomt.

    python3 tools/dekkingstoets.py
    python3 tools/dekkingstoets.py bronbrieven/uitgewerkt

Wat niet meetelt: de briefkop en de ondertekening (die komen uit het sjabloon en
uit config/ondertekenaars.yaml), en de uitgeschreven technische specificaties
(die komen uit een datablad).
"""

from __future__ import annotations

import argparse
import re
import sys
import zipfile
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from brieventool import laad

PLAATSHOUDER = re.compile(r"\{\{.*?\}\}")
ALINEA = re.compile(r"<w:p\b[^>]*/>|<w:p\b.*?</w:p>", re.S)
TEKST_OF_TAB = re.compile(r"<w:t[^>]*>([^<]*)</w:t>|(<w:tab/>)")

# Regels die niet uit de bibliotheek horen te komen.
BUITEN_BESCHOUWING = re.compile(
    r"^(Type|Koelvermogen|Verwarmingsvermogen|Aansluitspanning|SEER|SCOP|Koudemiddel|"
    r"Luchthoeveelheid|Geluidsniveau|Afmetingen|Paneel|Gewicht|Leiding|Afzekerwaarde|"
    r"Max\.|Nom\.|Koelen|Verwarmen|PANASONIC|TOSHIBA|MITSUBISHI|DAIKIN|LG |Aansluiten op|"
    r"Voorgevuld|Extra vulling|Verbinding|De unit is standaard|C2-Vertrouwelijk|"
    r"Schilt Bedrijven|Energieweg|Telefoon \+31|info@|www\.|BTW nr|KvK nr|Bankgegevens|"
    r"BIC|IBAN|G-rekening|Wij leveren volgens de algemene voorwaarden van de Koninklijke|"
    r"zoals deze luiden volgens|Voor meer informatie over de verwerking|"
    r"onze privacyverklaring:|- \d+ -)"
)


def alineas(pad: Path) -> list[str]:
    with zipfile.ZipFile(pad) as bestand:
        xml = bestand.read("word/document.xml").decode("utf-8")
    body = xml[xml.index("<w:body"):]
    uit = []
    for stuk in ALINEA.findall(body):
        tekst = "".join(t or "\t" for t, _ in TEKST_OF_TAB.findall(stuk))
        tekst = re.sub(r"[   ]+", " ", tekst)
        tekst = re.sub(r" {2,}", " ", tekst).strip()
        if tekst and not BUITEN_BESCHOUWING.match(tekst):
            uit.append(tekst)
    return uit


def patronen(wortel: Path) -> list[tuple[str, re.Pattern[str]]]:
    """Per regel van elk blok een patroon, met de plaatshouders als joker."""
    uit = []
    for blok in laad(wortel).blokken:
        for regel in blok.tekst.split("\n"):
            kaal = re.sub(r"[  ]+", " ", regel).strip()
            if not kaal:
                continue
            # De motor haalt het streepje van een opsommingsregel weg en maakt
            # er een echt opsommingsteken van; in de brief staat het dus niet
            # meer in de tekst.
            if kaal.startswith("- "):
                kaal = kaal[2:].strip()
            delen = [re.escape(d) for d in PLAATSHOUDER.split(kaal)]
            patroon = ".{0,80}?".join(delen).replace(r"\ ", r"\s+").replace(r"\\t", r"\s+")
            uit.append((blok.id, re.compile(rf"^{patroon}$", re.I)))
    return uit


def toets(mappen: list[Path], wortel: Path) -> int:
    blokpatronen = patronen(wortel)
    bestanden = sorted(p for m in mappen for p in m.iterdir()
                       if p.suffix.lower() in (".docx", ".dotx") and not p.name.startswith("~$"))
    if not bestanden:
        print("Geen brieven gevonden.", file=sys.stderr)
        return 1

    ongedekt: Counter[str] = Counter()
    totaal = gedekt_totaal = 0

    print(f"{'brief':<44} {'alinea’s':>9} {'gedekt':>7}")
    print("-" * 62)
    for pad in bestanden:
        regels = alineas(pad)
        gedekt = [r for r in regels if any(p.match(r) for _, p in blokpatronen)]
        for regel in regels:
            if regel not in gedekt:
                ongedekt[regel] += 1
        totaal += len(regels)
        gedekt_totaal += len(gedekt)
        deel = len(gedekt) * 100 // max(len(regels), 1)
        print(f"{pad.name[:44]:<44} {len(regels):>9} {deel:>6}%")

    print("-" * 62)
    print(f"{'samen':<44} {totaal:>9} {gedekt_totaal * 100 // max(totaal, 1):>6}%")

    if ongedekt:
        print(f"\nNiet in de bibliotheek ({len(ongedekt)} verschillende regels), "
              f"vaakst voorkomend eerst:\n")
        for regel, aantal in ongedekt.most_common(40):
            merk = f"{aantal}x" if aantal > 1 else "  "
            print(f"  {merk:>3} {regel[:104]}{'…' if len(regel) > 104 else ''}")
    return 0


def main() -> int:
    wortel = Path(__file__).resolve().parent.parent
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("mappen", nargs="*", type=Path,
                    default=[wortel / "bronbrieven", wortel / "bronbrieven" / "uitgewerkt"])
    keuzes = ap.parse_args()
    mappen = [m for m in keuzes.mappen if m.is_dir()]
    if not mappen:
        print("Geen van de opgegeven mappen bestaat.", file=sys.stderr)
        return 1
    return toets(mappen, wortel)


if __name__ == "__main__":
    raise SystemExit(main())
