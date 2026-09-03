"""Toetst de voorgeselecteerde werkzaamheden tegen de bronbrieven.

De opsomming "De installatie is aangeboden inclusief" en "Niet tot onze
werkzaamheden behoren" staat woord voor woord in de sjablonen. Split,
multi-split, cassette en kanaal delen een lijst; VRF heeft een eigen lijst met
andere regels en een andere volgorde. Deze toets leest die lijsten uit de
bronbrieven zelf, zodat de tool niet stilletjes van de brief af gaat lopen.
"""

import re
import unittest
import zipfile
from pathlib import Path

import yaml

from brieventool import laad
from brieventool.samenstellen import stel_samen

WORTEL = Path(__file__).resolve().parent.parent

# De sets die het scherm voorselecteert; ze staan ook in ontwerp/prototype.html.
STANDAARD = {
    "inclusief": ["demontage", "montage", "bekabeling", "transport", "inbedrijfstelling"],
    "exclusief": ["bouwkundig", "sparingen", "betonboringen", "elektra_stopcontact",
                  "elektra_voeding", "elektra_voedingskabel", "regeltechniek",
                  "condensafvoerleiding", "plakplaat", "beplating"],
}
VRF = {
    "inclusief": ["demontage", "montage", "sturingsbekabeling", "flexibele_leidingen",
                  "starre_leidingen", "inbedrijfstelling"],
    "exclusief": ["koellast", "bouwkundig", "sparingen_uitgebreid", "elektra_alles",
                  "regeltechniek_bedraden", "kabelgoot", "waterzijdig", "luchttechniek",
                  "inregelen", "condensafvoerleiding_meervoud", "plakplaten",
                  "beplating_stucco", "transport_vergunningen", "hoogwerker"],
}


def uit_bronbrief(bestand):
    """De twee opsommingen uit een sjabloon, in de volgorde van de brief."""
    xml = zipfile.ZipFile(WORTEL / "bronbrieven" / bestand).read("word/document.xml").decode("utf-8")
    body = xml[xml.index("<w:body"):]
    # In de sjablonen staat hier en daar een vaste spatie waar een gewone hoort;
    # dat is een typefout in Word en geen verschil in de tekst.
    regels = ["".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", p)).replace("\u00a0", " ").strip()
              for p in re.findall(r"<w:p\b[^>]*(?:/>|>.*?</w:p>)", body, re.S)]
    begin = next(n for n, r in enumerate(regels) if r.startswith("De installatie is aangeboden"))
    eind = next(n for n, r in enumerate(regels) if r.startswith("Totaalprijs"))
    return [r for r in regels[begin:eind] if r]


def brief_met(werk, systeemsoort):
    offerte = yaml.safe_load((WORTEL / "voorbeelden" / "zakelijk-cassette-meervoud.yaml")
                             .read_text(encoding="utf-8"))
    offerte["briefdatum"] = str(offerte["briefdatum"])
    offerte["werk_inclusief"] = werk["inclusief"]
    offerte["werk_exclusief"] = werk["exclusief"]
    offerte["installaties"] = [dict(offerte["installaties"][0], systeemsoort=systeemsoort)]
    brief = stel_samen(offerte, laad(WORTEL))
    return [a.tekst for sectie in ("werkzaamheden_inclusief", "werkzaamheden_exclusief")
            for a in brief.secties[sectie] if a.tekst.strip()]


def cursief_uit_bronbrief(bestand):
    """De schuingedrukte regels uit een sjabloon."""
    xml = zipfile.ZipFile(WORTEL / "bronbrieven" / bestand).read("word/document.xml").decode("utf-8")
    body = xml[xml.index("<w:body"):]
    uit = []
    for alinea in re.findall(r"<w:p\b[^>]*(?:/>|>.*?</w:p>)", body, re.S):
        for run in re.findall(r"<w:r\b.*?</w:r>", alinea, re.S):
            if re.search(r"<w:i/>|<w:i ", run):
                tekst = "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", run)).replace("\u00a0", " ").strip()
                if tekst:
                    uit.append(tekst)
    return uit


class TestCursiefVolgtDeBronbrief(unittest.TestCase):
    """Wat in de bronbrief schuingedrukt staat, staat dat in onze brief ook."""

    def test_dezelfde_regels_zijn_cursief(self):
        offerte = yaml.safe_load((WORTEL / "voorbeelden" / "particulier-wand-enkelvoud.yaml")
                                 .read_text(encoding="utf-8"))
        offerte["briefdatum"] = str(offerte["briefdatum"])
        brief = stel_samen(offerte, laad(WORTEL))
        onze = {a.tekst for alineas in brief.secties.values() for a in alineas if a.cursief}
        alle = {a.tekst for alineas in brief.secties.values() for a in alineas if a.tekst.strip()}

        bron = cursief_uit_bronbrief("wand enkelvoud.dotx")
        # Wat de bronbrief cursief zet en in onze brief voorkomt, hoort bij ons
        # ook cursief te zijn. De functieregels vallen af omdat het sjabloon er
        # drie toont en onze brief er een kiest.
        gedeeld = [r for r in bron if r in alle]
        self.assertEqual(len(gedeeld), 4, gedeeld)
        self.assertTrue(gedeeld[0].startswith("Voor de prijsvorming"), gedeeld)
        for regel in gedeeld:
            self.assertIn(regel, onze, f"in de bronbrief cursief, bij ons niet: {regel!r}")
        # En de functie van de gekozen ondertekenaar, die de bronbrief ook
        # schuingedrukt zet.
        self.assertIn("Technisch Commercieel Adviseur", onze)


class TestWerkzaamheden(unittest.TestCase):
    def test_standaardlijst_is_die_van_de_bronbrief(self):
        self.assertEqual(brief_met(STANDAARD, "splitsystem"),
                         uit_bronbrief("wand enkelvoud.dotx"))

    def test_dezelfde_lijst_voor_cassette(self):
        # cassette, kanaal en multi-split hebben in de sjablonen dezelfde lijst
        self.assertEqual(uit_bronbrief("cassette meervoud.dotx"),
                         uit_bronbrief("wand enkelvoud.dotx"))
        self.assertEqual(brief_met(STANDAARD, "multi-splitsystem"),
                         uit_bronbrief("cassette meervoud.dotx"))

    def test_vrf_heeft_een_eigen_lijst(self):
        self.assertEqual(brief_met(VRF, "vrf"), uit_bronbrief("VRF.dotx"))

    def test_de_twee_lijsten_verschillen_echt(self):
        self.assertNotEqual(brief_met(VRF, "vrf"), brief_met(STANDAARD, "splitsystem"))

    def test_het_scherm_selecteert_dezelfde_regels_voor(self):
        # De sets hierboven staan ook in het scherm; die mogen niet uiteenlopen.
        scherm = (WORTEL / "ontwerp" / "prototype.html").read_text(encoding="utf-8")
        for naam, set_ in [("WERK_STANDAARD", STANDAARD), ("WERK_VRF", VRF)]:
            blok = scherm[scherm.index(f"const {naam}="):]
            blok = blok[:blok.index("};")]
            for sleutel in set_["inclusief"] + set_["exclusief"]:
                self.assertIn(f'"{sleutel}"', blok, f"{sleutel} ontbreekt in {naam}")


if __name__ == "__main__":
    unittest.main()
