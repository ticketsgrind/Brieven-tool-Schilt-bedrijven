"""Toetst of het scherm zonder Python dezelfde brief maakt als de motor.

Het prototype heeft een JavaScript-spiegel van samenstellen.py aan boord, zodat
het ook werkt als er geen app achter zit -- bijvoorbeeld wanneer het bestand als
artefact wordt bediend. Die spiegel kan uit de pas gaan lopen met de Python-kant,
en dan zou er een brief uit komen die net iets anders is dan de brief uit de app.
Deze toets draait de spiegel in node en legt beide uitkomsten naast elkaar.
"""

import base64
import json
import shutil
import subprocess
import unittest
import zipfile
from pathlib import Path

import yaml

from brieventool.bibliotheek import laad
from brieventool.samenstellen import stel_samen
from brieventool.sjabloon import schrijf_docx

WORTEL = Path(__file__).resolve().parent.parent
PROTOTYPE = WORTEL / "ontwerp" / "prototype.html"
SJABLOON = WORTEL / "sjablonen" / "brief.docx"
DRAAI = WORTEL / "tools" / "spiegel" / "draai_motor.js"

# toets-uitgewerkt-3 wijst een specificatiebestand aan dat niet in git staat.
VOORBEELDEN = ["particulier-wand-enkelvoud", "zakelijk-cassette-meervoud"]

node = shutil.which("node")


def offerte(naam):
    uit = yaml.safe_load((WORTEL / "voorbeelden" / f"{naam}.yaml").read_text(encoding="utf-8"))
    uit["briefdatum"] = str(uit["briefdatum"])
    return uit


@unittest.skipUnless(node, "node is niet beschikbaar")
class TestSpiegel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bib = laad(WORTEL)

    def draai(self, gegevens, tijdelijk, docx=False):
        invoer = Path(tijdelijk) / "offerte.json"
        invoer.write_text(json.dumps(gegevens, ensure_ascii=False), encoding="utf-8")
        opdracht = [node, str(DRAAI), str(PROTOTYPE), str(invoer)] + (["docx"] if docx else [])
        klaar = subprocess.run(opdracht, capture_output=True)
        if klaar.returncode:
            self.fail(f"de spiegel liep vast:\n{klaar.stderr.decode('utf-8')[-2000:]}")
        return klaar.stdout

    def test_zelfde_alineas(self):
        import tempfile
        for naam in VOORBEELDEN:
            with self.subTest(naam), tempfile.TemporaryDirectory() as tijdelijk:
                gegevens = offerte(naam)
                brief = stel_samen(gegevens, self.bib)
                python = [[a.stijl, a.tekst, a.nadruk, a.witregel_erna,
                           a.letterlijk, a.uitgelijnd]
                          for alineas in brief.secties.values() for a in alineas]
                uit = json.loads(self.draai(gegevens, tijdelijk))
                spiegel = [[a["stijl"], a["tekst"], a["nadruk"], a["witregel_erna"],
                            a["letterlijk"], a["uitgelijnd"]]
                           for alineas in uit["secties"].values() for a in alineas]
                self.assertEqual(python, spiegel)
                self.assertEqual(brief.gebruikte_blokken, uit["gebruikt"])

    def test_zelfde_worddocument(self):
        import tempfile
        for naam in VOORBEELDEN:
            with self.subTest(naam), tempfile.TemporaryDirectory() as tijdelijk:
                gegevens = offerte(naam)
                van_python = Path(tijdelijk) / "python.docx"
                schrijf_docx(stel_samen(gegevens, self.bib), SJABLOON, van_python)
                van_scherm = Path(tijdelijk) / "scherm.docx"
                van_scherm.write_bytes(self.draai(gegevens, tijdelijk, docx=True))

                with zipfile.ZipFile(van_python) as a, zipfile.ZipFile(van_scherm) as b:
                    self.assertEqual(a.namelist(), b.namelist())
                    self.assertIsNone(b.testzip(), "het scherm maakt een beschadigde zip")
                    for onderdeel in a.namelist():
                        if onderdeel == "word/document.xml":
                            # Jinja trekt de regeleinden in het sjabloon glad;
                            # het scherm laat ze staan. Word maakt dat niet uit.
                            self.assertEqual(a.read(onderdeel).replace(b"\r\n", b"\n"),
                                             b.read(onderdeel).replace(b"\r\n", b"\n"))
                        else:
                            self.assertEqual(a.read(onderdeel), b.read(onderdeel),
                                             f"{onderdeel} verschilt")


class TestIngebakkenSjabloon(unittest.TestCase):
    """Het sjabloon zit in het prototype; dat mag niet achterlopen."""

    def test_sjabloon_is_bijgewerkt(self):
        html = PROTOTYPE.read_text(encoding="utf-8")
        begin = html.index("/*<sjabloon>*/") + len("/*<sjabloon>*/")
        ingebakken = html[begin:html.index("/*</sjabloon>*/")].strip('"')
        self.assertEqual(base64.b64decode(ingebakken), SJABLOON.read_bytes(),
                         "draai ontwerp/ververs_prototype.py opnieuw")


if __name__ == "__main__":
    unittest.main()
