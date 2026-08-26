"""Toetst de samenstelling tegen de echte bibliotheek in analyse/teksten.yaml."""

import unittest
from pathlib import Path

import yaml

from brieventool import laad, stel_samen

WORTEL = Path(__file__).resolve().parent.parent


def voorbeeld(naam):
    return yaml.safe_load((WORTEL / "voorbeelden" / naam).read_text(encoding="utf-8"))


class TestBibliotheek(unittest.TestCase):
    def test_bibliotheek_laadt(self):
        bib = laad(WORTEL)
        self.assertGreater(len(bib.blokken), 100)
        self.assertEqual(len({b.id for b in bib.blokken}), len(bib.blokken))

    def test_geen_notities_in_de_brieftekst(self):
        # Aantekeningen horen in het veld `notitie`, niet in de tekst: anders
        # belanden ze in de brief naar de klant.
        for blok in laad(WORTEL).blokken:
            self.assertNotIn("#", blok.tekst, f"blok {blok.id} heeft een # in de tekst")

    def test_geen_letterlijke_tab_ontsnapping(self):
        for blok in laad(WORTEL).blokken:
            self.assertNotIn("\\t", blok.tekst, f"blok {blok.id} heeft een letterlijke \\t")


class TestParticuliereBrief(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.brief = stel_samen(voorbeeld("particulier-wand-enkelvoud.yaml"), laad(WORTEL))

    def test_geen_waarschuwingen(self):
        self.assertEqual(self.brief.waarschuwingen, [])

    def test_btw_inclusief_bij_particulier(self):
        prijs = "\n".join(self.brief.regels("prijs"))
        self.assertIn("inclusief 21% btw", prijs)
        self.assertNotIn("exclusief", prijs)

    def test_enkelvoud(self):
        tekst = self.brief.tekst()
        self.assertIn("De binnenunit is ontworpen", tekst)
        self.assertIn("een airconditioninginstallatie", tekst)
        self.assertIn("De buitenunit wordt geplaatst", tekst)

    def test_geen_kredietwaardigheid_bij_particulier(self):
        self.assertNotIn("Kredietwaardigheid", "\n".join(self.brief.regels("voorwaarden")))

    def test_condenspomp_particulier_tarief(self):
        self.assertIn("€ 260,- per stuk", "\n".join(self.brief.regels("prijs")))

    def test_referentie_wordt_voorgesteld(self):
        self.assertEqual(self.brief.context["referentie"], "NV/LH/SA35923")

    def test_bedrag_in_nederlandse_notatie(self):
        self.assertIn("€ 3.900,- netto", "\n".join(self.brief.regels("prijs")))

    def test_geen_openstaande_plaatshouders(self):
        self.assertNotIn("{{", self.brief.tekst())


class TestZakelijkeBrief(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.brief = stel_samen(voorbeeld("zakelijk-cassette-meervoud.yaml"), laad(WORTEL))

    def test_geen_waarschuwingen(self):
        self.assertEqual(self.brief.waarschuwingen, [])

    def test_btw_exclusief_bij_zakelijk(self):
        self.assertIn("exclusief 21% btw", "\n".join(self.brief.regels("prijs")))

    def test_meervoud(self):
        tekst = self.brief.tekst()
        self.assertIn("De binnenunits zijn", tekst)
        self.assertIn("airconditioninginstallaties", tekst)
        self.assertIn("De buitenunits worden geplaatst", tekst)

    def test_kredietwaardigheid_bij_zakelijk(self):
        self.assertIn("Kredietwaardigheid", "\n".join(self.brief.regels("voorwaarden")))

    def test_condenspomp_zakelijk_tarief(self):
        self.assertIn("€ 220,- per stuk", "\n".join(self.brief.regels("prijs")))

    def test_installatieregels_staan_bij_hun_ruimte(self):
        # Kopregel en installatieregel horen te alterneren, niet eerst alle
        # kopregels en daarna alle installatieregels.
        spec = self.brief.regels("specificatie")
        self.assertEqual(len(spec), 4)
        self.assertTrue(spec[0].startswith("T.b.v."))
        self.assertTrue(spec[1].startswith("Het leveren en monteren"))
        self.assertTrue(spec[2].startswith("T.b.v."))
        self.assertTrue(spec[3].startswith("Het leveren en monteren"))

    def test_telwoord_in_de_specificatie(self):
        self.assertIn("twee luchtgekoelde splitsystem inverterunits", self.brief.regels("specificatie")[1])
        self.assertIn("één luchtgekoelde splitsystem inverterunit ", self.brief.regels("specificatie")[3])

    def test_organisatie_boven_het_adres(self):
        self.assertEqual(self.brief.regels("geadresseerde")[0], "Voorbeeld Vastgoed B.V.")

    def test_geen_openstaande_plaatshouders(self):
        self.assertNotIn("{{", self.brief.tekst())


class TestKeuzegroepen(unittest.TestCase):
    """Binnen een keuzegroep hoort precies één blok in de brief te komen."""

    def test_betreft_is_altijd_precies_een_regel(self):
        bib = laad(WORTEL)
        for naam in ("particulier-wand-enkelvoud.yaml", "zakelijk-cassette-meervoud.yaml"):
            with self.subTest(naam):
                self.assertEqual(len(stel_samen(voorbeeld(naam), bib).regels("betreft")), 1)

    def test_eerste_woord_volgt_het_installatietype(self):
        offerte = voorbeeld("zakelijk-cassette-meervoud.yaml")
        offerte["installatietype"] = "koelmachine"
        betreft = stel_samen(offerte, laad(WORTEL)).regels("betreft")
        self.assertEqual(len(betreft), 1)
        self.assertIn("Koelmachine t.b.v.", betreft[0])

    def test_aanleiding_is_altijd_precies_een_alinea(self):
        bib = laad(WORTEL)
        for naam in ("particulier-wand-enkelvoud.yaml", "zakelijk-cassette-meervoud.yaml"):
            with self.subTest(naam):
                self.assertEqual(len(stel_samen(voorbeeld(naam), bib).regels("aanleiding")), 1)


class TestWaarschuwingen(unittest.TestCase):
    def test_verkeerde_keuze_geeft_waarschuwing(self):
        offerte = voorbeeld("zakelijk-cassette-meervoud.yaml")
        # Particuliere factureringsregel op een zakelijke offerte.
        offerte["gekozen_blokken"] = ["facturering_betaling_particulier"]
        brief = stel_samen(offerte, laad(WORTEL))
        self.assertTrue(any("facturering_betaling_particulier" in w for w in brief.waarschuwingen))

    def test_onbekende_ondertekenaar_geeft_duidelijke_fout(self):
        from brieventool.samenstellen import SamenstelFout
        offerte = voorbeeld("particulier-wand-enkelvoud.yaml")
        offerte["ondertekenaar"] = "piet_pietersen"
        with self.assertRaises(SamenstelFout) as gevangen:
            stel_samen(offerte, laad(WORTEL))
        self.assertIn("piet_pietersen", str(gevangen.exception))


if __name__ == "__main__":
    unittest.main()
