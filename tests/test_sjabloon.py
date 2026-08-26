"""Toetst de laag die het Word-bestand schrijft.

docxtpl zelf wordt hier niet gedraaid; wel de twee dingen die eromheen fout
kunnen gaan: welke gegevens het sjabloon te zien krijgt, en de reparatie van
tabtekens.
"""

import unittest
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

import yaml

from brieventool import laad, stel_samen
from brieventool.sjabloon import (KOPSECTIES, PARAGRAAFTAG, Wq, context,
                                  schrijf_docx, tabs_naar_word)

WORTEL = Path(__file__).resolve().parent.parent
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def brief(naam="particulier-wand-enkelvoud.yaml"):
    offerte = yaml.safe_load((WORTEL / "voorbeelden" / naam).read_text(encoding="utf-8"))
    return stel_samen(offerte, laad(WORTEL))


class TestContext(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c = context(brief())

    def test_romp_slaat_de_briefkop_over(self):
        # De briefkop staat los in het sjabloon; die mag niet dubbel komen.
        namen = [n for n, a in brief().secties.items() if a]
        romp_namen = [n for n in namen if n not in KOPSECTIES]
        self.assertEqual(len(self.c["romp"]), len(romp_namen))

    def test_romp_bevat_geen_lege_secties(self):
        # Een lege sectie zou een lege regel in de brief opleveren.
        for sectie in self.c["romp"]:
            self.assertTrue(sectie)

    def test_romp_houdt_de_volgorde_aan(self):
        eerste = self.c["romp"][0][0].tekst
        self.assertTrue(eerste.startswith("Naar aanleiding"), eerste)

    def test_geen_functies_in_de_context(self):
        # telwoord() zit in de context voor de plaatshouders, maar docxtpl hoeft
        # hem niet te krijgen.
        for waarde in self.c.values():
            self.assertFalse(callable(waarde))

    def test_losse_velden_blijven_beschikbaar(self):
        self.assertEqual(self.c["referentie"], "NV/LH/SA35923")
        self.assertEqual(self.c["ondertekenaar"]["naam"], "Nick Vervoorn")


class TestParagraaftag(unittest.TestCase):
    """Het patroon dat {%p ... %}-alinea's uit het sjabloon haalt."""

    def uitpakken(self, xml):
        return PARAGRAAFTAG.sub(lambda m: "{%" + m.group(1) + "%}", xml)

    def test_tagalinea_verdwijnt_de_tag_blijft(self):
        xml = "<w:p><w:r><w:t>{%p endfor %}</w:t></w:r></w:p>"
        self.assertEqual(self.uitpakken(xml), "{% endfor %}")

    def test_zelfsluitende_lege_alinea_blijft_staan(self):
        # Dit was een echte fout: <w:p /> heeft geen </w:p>, dus het patroon
        # zocht door in de volgende alinea en slokte de witregel op.
        xml = '<w:p /><w:p><w:r><w:t>{%p endfor %}</w:t></w:r></w:p>'
        self.assertEqual(self.uitpakken(xml), "<w:p />{% endfor %}")

    def test_gewone_alinea_blijft_ongemoeid(self):
        xml = "<w:p><w:r><w:t>Geachte heer Jansen,</w:t></w:r></w:p>"
        self.assertEqual(self.uitpakken(xml), xml)

    def test_alinea_met_gewone_plaatshouder_blijft_staan(self):
        # {{ }} hoort in de alinea te blijven; alleen {%p %} haalt hem weg.
        xml = "<w:p><w:r><w:t>{{ a.tekst }}</w:t></w:r></w:p>"
        self.assertEqual(self.uitpakken(xml), xml)


class TestTabs(unittest.TestCase):
    def maak(self, tekst):
        return ET.fromstring(
            f'<w:r xmlns:w="{W}"><w:t xml:space="preserve">{tekst}</w:t></w:r>'
        )

    def test_tab_wordt_een_word_tab(self):
        run = self.maak("Betreft\tAirconditioning")
        self.assertEqual(tabs_naar_word(run), 1)
        self.assertEqual([k.tag.split("}")[1] for k in run], ["t", "tab", "t"])
        self.assertEqual(run[0].text, "Betreft")
        self.assertEqual(run[2].text, "Airconditioning")

    def test_meerdere_tabs_achter_elkaar(self):
        # De factureringstermijnen zijn met twee tabs uitgelijnd.
        run = self.maak("\t\t70% bij aanvang werkzaamheden")
        self.assertEqual(tabs_naar_word(run), 2)
        self.assertEqual([k.tag.split("}")[1] for k in run], ["tab", "tab", "t"])

    def test_tekst_zonder_tabs_blijft_ongemoeid(self):
        run = self.maak("Geachte heer Jansen,")
        self.assertEqual(tabs_naar_word(run), 0)
        self.assertEqual(len(run), 1)
        self.assertEqual(run[0].text, "Geachte heer Jansen,")

    def test_spaties_blijven_behouden(self):
        run = self.maak("Facturering:\t30% bij opdracht ")
        tabs_naar_word(run)
        laatste = run[-1]
        self.assertEqual(laatste.get("{http://www.w3.org/XML/1998/namespace}space"), "preserve")
        self.assertTrue(laatste.text.endswith(" "))


class TestSjabloonbestand(unittest.TestCase):
    """Het gemaakte sjabloon moet de huisstijl van de bronbrief behouden."""

    @classmethod
    def setUpClass(cls):
        cls.pad = WORTEL / "sjablonen" / "brief.docx"

    def test_sjabloon_bestaat(self):
        self.assertTrue(self.pad.is_file(),
                        "draai eerst: python3 tools/maak_sjabloon.py")

    def test_briefpapier_is_meegekomen(self):
        with zipfile.ZipFile(self.pad) as z:
            namen = z.namelist()
        self.assertTrue([n for n in namen if n.startswith("word/media/")], "afbeeldingen ontbreken")
        self.assertTrue([n for n in namen if "header" in n], "briefkop ontbreekt")
        self.assertTrue([n for n in namen if "footer" in n], "voettekst ontbreekt")
        self.assertIn("word/styles.xml", namen)

    def test_is_een_document_en_geen_sjabloon(self):
        # Een .dotx opent Word als "nieuw document op basis van"; dat willen we niet.
        with zipfile.ZipFile(self.pad) as z:
            types = z.read("[Content_Types].xml").decode("utf-8")
        self.assertIn("wordprocessingml.document.main+xml", types)
        self.assertNotIn("wordprocessingml.template.main+xml", types)

    def test_paginainstellingen_zijn_bewaard(self):
        with zipfile.ZipFile(self.pad) as z:
            body = ET.fromstring(z.read("word/document.xml")).find(Wq + "body")
        sectpr = body.find(Wq + "sectPr")
        self.assertIsNotNone(sectpr, "sectPr ontbreekt: marges en kop-/voetteksten zijn weg")
        self.assertIsNotNone(sectpr.find(Wq + "pgSz"))

    def test_elke_lus_is_gesloten(self):
        import zipfile
        with zipfile.ZipFile(self.pad) as z:
            tekst = "".join(
                t.text or "" for t in ET.fromstring(z.read("word/document.xml")).iter(Wq + "t")
            )
        self.assertEqual(tekst.count("{%p for"), tekst.count("{%p endfor %}"))
        self.assertEqual(tekst.count("{%p if"), tekst.count("{%p endif %}"))

    def test_sjabloon_verwijst_naar_bestaande_secties(self):
        import re
        with zipfile.ZipFile(self.pad) as z:
            tekst = "".join(
                t.text or "" for t in ET.fromstring(z.read("word/document.xml")).iter(Wq + "t")
            )
        genoemd = set(re.findall(r"secties\.(\w+)", tekst))
        bestaand = {b.sectie for b in laad(WORTEL).blokken}
        self.assertTrue(genoemd <= bestaand, f"onbekende secties: {genoemd - bestaand}")


class TestGeschrevenDocument(unittest.TestCase):
    """Schrijft echt een .docx en leest hem terug."""

    @classmethod
    def setUpClass(cls):
        import tempfile
        cls.map = tempfile.TemporaryDirectory()
        cls.pad = schrijf_docx(brief("zakelijk-cassette-meervoud.yaml"),
                               WORTEL / "sjablonen" / "brief.docx",
                               Path(cls.map.name) / "brief.docx")
        with zipfile.ZipFile(cls.pad) as z:
            cls.namen = z.namelist()
            cls.body = ET.fromstring(z.read("word/document.xml")).find(Wq + "body")
        cls.alineas = cls.body.findall(Wq + "p")

    @classmethod
    def tearDownClass(cls):
        cls.map.cleanup()

    def regels(self):
        uit = []
        for alinea in self.alineas:
            delen = []
            for kind in alinea.iter():
                if kind.tag == Wq + "t":
                    delen.append(kind.text or "")
                elif kind.tag == Wq + "tab":
                    delen.append("\t")
            uit.append("".join(delen))
        return uit

    def test_geen_sjabloontags_meer_over(self):
        tekst = "".join(self.regels())
        self.assertNotIn("{{", tekst)
        self.assertNotIn("{%", tekst)

    def test_briefpapier_is_meegekomen(self):
        self.assertTrue([n for n in self.namen if n.startswith("word/media/")])
        self.assertTrue([n for n in self.namen if "header" in n])
        self.assertIsNotNone(self.body.find(Wq + "sectPr"))

    def test_witregels_tussen_de_secties(self):
        # Een zelfsluitende <w:p /> werd eerder door het tagpatroon opgeslokt,
        # waardoor de brief één doorlopend blok tekst werd.
        leeg = [r for r in self.regels() if not r.strip()]
        self.assertGreater(len(leeg), 10, "de witregels tussen de secties zijn weg")

    def test_tabs_zijn_word_tabs_geworden(self):
        losse_tabs = [t.text for t in self.body.iter(Wq + "t") if t.text and "\t" in t.text]
        self.assertEqual(losse_tabs, [], "er staan nog tabtekens in de tekst")
        self.assertTrue([1 for _ in self.body.iter(Wq + "tab")], "geen enkele Word-tab")

    def test_betreft_en_termijnen_zijn_uitgelijnd(self):
        regels = self.regels()
        self.assertTrue(any(r.startswith("Betreft\t") for r in regels))
        self.assertTrue(any(r.startswith("\t\t") for r in regels), "termijnen niet ingesprongen")

    def test_opsommingen_hebben_de_lijststijl(self):
        stijlen = []
        for alinea in self.alineas:
            tekst = "".join(t.text or "" for t in alinea.iter(Wq + "t"))
            if tekst.startswith("betonboringen, hak-"):
                ppr = alinea.find(Wq + "pPr")
                stijlen.append(ppr.find(Wq + "pStyle").get(Wq + "val") if ppr is not None else None)
        self.assertEqual(stijlen, ["Lijstalinea"])

    def test_de_brief_bevat_de_juiste_inhoud(self):
        tekst = "\n".join(self.regels())
        for verwacht in ["Voorbeeld Vastgoed B.V.", "exclusief 21% btw", "€ 24.750,- netto",
                         "Kredietwaardigheid:", "De binnenunits zijn", "John van de Weetering"]:
            self.assertIn(verwacht, tekst)


if __name__ == "__main__":
    unittest.main()
