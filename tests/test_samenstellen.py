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
        regels = self.brief.regels("geadresseerde")
        self.assertEqual(regels[0], "Voorbeeld Vastgoed B.V.")
        self.assertTrue(regels[1].startswith("T.a.v."), regels[1])

    def test_geen_openstaande_plaatshouders(self):
        self.assertNotIn("{{", self.brief.tekst())


class TestOpmaakVanAlineas(unittest.TestCase):
    """De opmaak is nagemeten aan de bronbrieven; zie analyse/skelet.md."""

    @classmethod
    def setUpClass(cls):
        cls.brief = stel_samen(voorbeeld("particulier-wand-enkelvoud.yaml"), laad(WORTEL))

    def test_opsommingsregels_staan_tegen_elkaar_aan(self):
        # In de bronbrieven staat er geen witregel tussen twee opsommingsregels,
        # wel na de laatste. Zonder dat onderscheid staat de brief opgepropt.
        regels = self.brief.secties["werkzaamheden_inclusief"]
        opsommingen = [a for a in regels if a.stijl == "opsomming"]
        self.assertGreater(len(opsommingen), 2)
        for alinea in opsommingen[:-1]:
            self.assertFalse(alinea.witregel_erna, alinea.tekst)
        self.assertTrue(opsommingen[-1].witregel_erna)

    def test_witregel_na_elke_gewone_alinea(self):
        prijs = [a for a in self.brief.secties["prijs"] if a.stijl == "tekst"]
        for alinea in prijs:
            self.assertTrue(alinea.witregel_erna, alinea.tekst)

    def test_kop_gevolgd_door_witregel(self):
        koppen = [a for a in self.brief.alle_alineas if a.stijl == "kop"]
        self.assertGreater(len(koppen), 3)
        for kop in koppen:
            self.assertTrue(kop.witregel_erna, kop.tekst)

    def test_uitgelijnde_vervolgregel_hoort_bij_de_regel_erboven(self):
        # De factureringstermijnen zijn met tabs uitgelijnd; tussen een regel en
        # zijn vervolgregel hoort geen witregel.
        regels = self.brief.secties["facturering"]
        vervolg = [n for n, a in enumerate(regels) if a.uitgelijnd]
        self.assertTrue(vervolg, "geen uitgelijnde vervolgregels gevonden")
        for nummer in vervolg:
            self.assertFalse(regels[nummer - 1].witregel_erna)

    def test_streepje_in_een_uitgelijnde_regel_is_geen_opsomming(self):
        # "\t\t- laatste termijn" begint na strippen met "- ", maar is een
        # uitgelijnde vervolgregel en geen opsommingsregel.
        for alinea in self.brief.secties["facturering"]:
            if alinea.uitgelijnd:
                self.assertEqual(alinea.stijl, "tekst")
                self.assertIn("- laatste termijn", alinea.tekst)
                self.assertTrue(alinea.tekst.startswith("\t"))

    def test_streepje_aan_het_begin_wordt_wel_een_opsomming(self):
        # De uitgangspunten bij de prijsvorming staan met "- " in teksten.yaml.
        uitgangspunten = [a for a in self.brief.secties["prijs"]
                          if "goed bereikbaar" in a.tekst]
        self.assertEqual(len(uitgangspunten), 1)
        self.assertEqual(uitgangspunten[0].stijl, "opsomming")
        self.assertFalse(uitgangspunten[0].tekst.startswith("-"))


class TestAdresblok(unittest.TestCase):
    """Nagemeten in de uitgewerkte brieven."""

    def test_zonder_organisatie_geen_tav(self):
        # "De heer K. ten Broek", niet "T.a.v. de heer ...".
        brief = stel_samen(voorbeeld("particulier-wand-enkelvoud.yaml"), laad(WORTEL))
        eerste = brief.regels("geadresseerde")[0]
        self.assertFalse(eerste.startswith("T.a.v."), eerste)
        self.assertTrue(eerste.startswith("De heer"), eerste)

    def test_met_organisatie_wel_tav(self):
        brief = stel_samen(voorbeeld("zakelijk-cassette-meervoud.yaml"), laad(WORTEL))
        self.assertTrue(brief.regels("geadresseerde")[1].startswith("T.a.v."))

    def test_maar_een_van_de_twee_adresregels(self):
        for naam in ("particulier-wand-enkelvoud.yaml", "zakelijk-cassette-meervoud.yaml"):
            with self.subTest(naam):
                regels = stel_samen(voorbeeld(naam), laad(WORTEL)).regels("geadresseerde")
                self.assertEqual(sum(1 for r in regels if "heer" in r), 1, regels)

    def test_tussenvoegsel_krijgt_hoofdletter_in_de_aanhef(self):
        # "De heer K. ten Broek" in het adres, "Geachte heer Ten Broek," in de aanhef.
        offerte = voorbeeld("particulier-wand-enkelvoud.yaml")
        offerte["achternaam"] = "ten Broek"
        brief = stel_samen(offerte, laad(WORTEL))
        self.assertEqual(brief.regels("geadresseerde")[0], "De heer J. ten Broek")
        self.assertEqual(brief.regels("aanhef")[0], "Geachte heer Ten Broek,")

    def test_emailadres_onderaan_indien_bekend(self):
        offerte = voorbeeld("particulier-wand-enkelvoud.yaml")
        offerte["email_klant"] = "voorbeeld@example.nl"
        regels = stel_samen(offerte, laad(WORTEL)).regels("geadresseerde")
        self.assertEqual(regels[-1], "voorbeeld@example.nl")

    def test_geen_lege_regel_zonder_emailadres(self):
        regels = stel_samen(voorbeeld("particulier-wand-enkelvoud.yaml"),
                            laad(WORTEL)).regels("geadresseerde")
        self.assertTrue(all(r.strip() for r in regels))


class TestVettePrijs(unittest.TestCase):
    """In de bronbrieven staat het bedrag vet en de aanloopzin niet."""

    @classmethod
    def setUpClass(cls):
        cls.brief = stel_samen(voorbeeld("zakelijk-cassette-meervoud.yaml"), laad(WORTEL))

    def prijsregels(self):
        return [a for a in self.brief.secties["prijs"] if a.stijl == "prijs"]

    def test_bedrag_staat_apart_van_de_aanloopzin(self):
        regels = self.prijsregels()
        self.assertTrue(regels, "geen prijsregels gevonden")
        for alinea in regels:
            self.assertTrue(alinea.nadruk.startswith("€"), alinea.nadruk)
            self.assertTrue(alinea.nadruk.rstrip().endswith("netto."), alinea.nadruk)
            self.assertNotIn("€", alinea.tekst)

    def test_totaalprijs_en_meerprijzen_zijn_prijsregels(self):
        teksten = [a.tekst for a in self.prijsregels()]
        self.assertTrue(any("De totaalprijs" in t for t in teksten))
        self.assertTrue(any("De meerprijs voor het coaten" in t for t in teksten))

    def test_condenswaterpomp_is_geen_prijsregel(self):
        # Die regel eindigt op "per stuk" en staat in de bronbrieven niet vet.
        for alinea in self.brief.secties["prijs"]:
            if "condenswater" in alinea.tekst:
                self.assertEqual(alinea.stijl, "tekst")
                self.assertEqual(alinea.nadruk, "")
                return
        self.fail("de condenswaterpompregel is niet gevonden")

    def test_btw_regel_is_geen_prijsregel(self):
        for alinea in self.brief.secties["prijs"]:
            if "btw" in alinea.tekst:
                self.assertEqual(alinea.stijl, "tekst")

    def test_regel_zonder_bedrag_blijft_heel(self):
        from brieventool.samenstellen import _splits_bedrag
        self.assertEqual(_splits_bedrag("Geen bedrag hier."), ("Geen bedrag hier.", ""))


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
