"""Toetst de lokale app: de antwoorden die het scherm van de motor krijgt."""

import json
import re
import threading
import unittest
import urllib.error
import urllib.request
import zipfile
from http.server import ThreadingHTTPServer
from io import BytesIO
from pathlib import Path

import yaml

from brieventool.bibliotheek import laad
from brieventool.server import Bediening, _bestandsnaam

WORTEL = Path(__file__).resolve().parent.parent


def offerte(naam="zakelijk-cassette-meervoud.yaml", **extra):
    uit = yaml.safe_load((WORTEL / "voorbeelden" / naam).read_text(encoding="utf-8"))
    uit["briefdatum"] = str(uit["briefdatum"])      # datum als tekst, zoals de browser stuurt
    uit.update(extra)
    return uit


class TestApp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Bediening)
        cls.server.bibliotheek = laad(WORTEL)
        cls.adres = f"http://127.0.0.1:{cls.server.server_address[1]}"
        cls.draad = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.draad.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def haal(self, pad):
        with urllib.request.urlopen(f"{self.adres}{pad}") as antwoord:
            return antwoord.status, antwoord.read(), dict(antwoord.headers)

    def stuur(self, pad, gegevens):
        verzoek = urllib.request.Request(f"{self.adres}{pad}",
                                         json.dumps(gegevens).encode("utf-8"),
                                         {"Content-Type": "application/json"})
        with urllib.request.urlopen(verzoek) as antwoord:
            return antwoord.status, antwoord.read(), dict(antwoord.headers)

    # --- geen halve brief --------------------------------------------------

    def test_docx_weigert_een_onvolledige_offerte(self):
        gegevens = offerte()
        gegevens["prijsregels"] = [{"bedrag": ""}]
        code, inhoud, koppen = self.stuur("/docx", gegevens)
        self.assertEqual(code, 200)
        self.assertIn("application/json", koppen["Content-Type"])
        uit = json.loads(inhoud)
        self.assertIn("het bedrag", uit["fout"])
        self.assertEqual(uit["ontbreekt"], ["het bedrag"])

    def test_brief_vertelt_wat_er_ontbreekt(self):
        gegevens = offerte()
        gegevens["projectnummer"] = ""
        uit = json.loads(self.stuur("/brief", gegevens)[1])
        self.assertEqual(uit["ontbreekt"], ["het projectnummer"])
        # De voorvertoning blijft wel gewoon werken tijdens het invullen.
        self.assertTrue(uit["secties"])

    # --- het scherm --------------------------------------------------------

    def test_app_meldt_zich(self):
        # Het scherm herkent de motor hieraan, niet aan het protocol: los
        # bediend over https is er geen Python en moet het zelf rekenen.
        code, inhoud, koppen = self.haal("/app")
        self.assertEqual(code, 200)
        self.assertIn("application/json", koppen["Content-Type"])
        uit = json.loads(inhoud)
        self.assertIs(uit["app"], True)
        self.assertGreater(uit["blokken"], 0)

    def test_scherm_vraagt_zonder_schuine_streep(self):
        # Alle adressen in het scherm zijn betrekkelijk, zodat het ook werkt
        # wanneer het bestand onder een submap wordt bediend.
        scherm = (WORTEL / "ontwerp" / "prototype.html").read_text(encoding="utf-8")
        for adres in re.findall(r'fetch\("([^"]*)"', scherm):
            self.assertFalse(adres.startswith("/"),
                             f"adres {adres!r} is absoluut")
        self.assertNotIn("location.protocol", scherm)

    def test_scherm_wordt_bediend(self):
        code, inhoud, koppen = self.haal("/")
        self.assertEqual(code, 200)
        self.assertIn("text/html", koppen["Content-Type"])
        self.assertIn(b"Offertebrieven", inhoud)

    def test_favicon_geeft_geen_fout(self):
        # Zonder dit staat er bij elke start een 404 in de foutmelding van de browser.
        code, _, _ = self.haal("/favicon.ico")
        self.assertEqual(code, 204)

    def test_onbekend_adres(self):
        with self.assertRaises(urllib.error.HTTPError) as gevangen:
            self.haal("/bestaatniet")
        self.assertEqual(gevangen.exception.code, 404)

    # --- de brief ----------------------------------------------------------

    def test_brief_komt_terug_met_alineas(self):
        _, inhoud, _ = self.stuur("/brief", offerte())
        uit = json.loads(inhoud)
        self.assertNotIn("fout", uit)
        namen = [s["naam"] for s in uit["secties"]]
        self.assertIn("betreft", namen)
        self.assertIn("prijs", namen)
        self.assertTrue(uit["blokken"])

    def test_de_opmaak_komt_mee(self):
        # Het scherm moet weten wat vet, onderstreept of een opsomming is.
        _, inhoud, _ = self.stuur("/brief", offerte())
        stijlen = {a["stijl"] for s in json.loads(inhoud)["secties"] for a in s["alineas"]}
        self.assertTrue({"kop", "kopvet", "opsomming", "prijs"} <= stijlen, stijlen)

    def test_het_vette_bedrag_staat_apart(self):
        _, inhoud, _ = self.stuur("/brief", offerte())
        prijzen = [a for s in json.loads(inhoud)["secties"] if s["naam"] == "prijs"
                   for a in s["alineas"] if a["stijl"] == "prijs"]
        self.assertTrue(prijzen)
        for alinea in prijzen:
            self.assertTrue(alinea["nadruk"].startswith("€"))

    def test_klanttype_verandert_de_brief(self):
        def btw(klanttype):
            _, inhoud, _ = self.stuur("/brief", offerte(klanttype=klanttype))
            return " ".join(a["tekst"] for s in json.loads(inhoud)["secties"]
                            for a in s["alineas"])
        self.assertIn("exclusief 21% btw", btw("zakelijk"))
        self.assertIn("inclusief 21% btw", btw("particulier"))

    def test_lege_secties_komen_niet_mee(self):
        _, inhoud, _ = self.stuur("/brief", offerte())
        for sectie in json.loads(inhoud)["secties"]:
            self.assertTrue(sectie["alineas"], sectie["naam"])

    def test_fout_komt_terug_als_tekst_en_niet_als_crash(self):
        _, inhoud, _ = self.stuur("/brief", offerte(ondertekenaar="piet"))
        uit = json.loads(inhoud)
        self.assertIn("piet", uit["fout"])

    def test_onleesbaar_verzoek(self):
        verzoek = urllib.request.Request(f"{self.adres}/brief", b"{geen json",
                                         {"Content-Type": "application/json"})
        with self.assertRaises(urllib.error.HTTPError) as gevangen:
            urllib.request.urlopen(verzoek)
        self.assertEqual(gevangen.exception.code, 400)

    # --- het Word-bestand --------------------------------------------------

    def test_docx_is_een_word_bestand(self):
        _, inhoud, koppen = self.stuur("/docx", offerte())
        self.assertIn("wordprocessingml.document", koppen["Content-Type"])
        with zipfile.ZipFile(BytesIO(inhoud)) as bestand:
            namen = bestand.namelist()
        self.assertIn("word/document.xml", namen)
        self.assertTrue([n for n in namen if n.startswith("word/media/")],
                        "het briefpapier is niet meegekomen")

    def test_bestandsnaam_volgt_de_klant(self):
        _, _, koppen = self.stuur("/docx", offerte())
        self.assertIn("de-wit-meerkerk-35950.docx", koppen["Content-Disposition"])

    def test_bestandsnaam_zonder_gegevens(self):
        self.assertEqual(_bestandsnaam({}), "offerte.docx")

    def test_bestandsnaam_laat_geen_rare_tekens_door(self):
        naam = _bestandsnaam({"achternaam": "de Vries/../etc", "plaats": "Meerkerk"})
        self.assertNotIn("/", naam)
        self.assertNotIn("..", naam)

    def test_fout_bij_docx_komt_als_tekst_terug(self):
        _, inhoud, koppen = self.stuur("/docx", offerte(ondertekenaar="piet"))
        self.assertIn("json", koppen["Content-Type"])
        self.assertIn("piet", json.loads(inhoud)["fout"])

    # --- het datablad ------------------------------------------------------

    def test_datablad_wordt_uitgelezen(self):
        import base64
        inhoud = base64.b64encode("Type\t: S-6071PU3E\nKoudemiddel\t: R32".encode()).decode()
        _, antwoord, _ = self.stuur("/datablad", {"naam": "blad.txt", "inhoud": inhoud})
        self.assertEqual(json.loads(antwoord)["tekst"], "Type\t: S-6071PU3E\nKoudemiddel\t: R32")

    def test_datablad_van_een_onbekend_soort(self):
        import base64
        _, antwoord, _ = self.stuur("/datablad", {
            "naam": "blad.xlsx", "inhoud": base64.b64encode(b"iets").decode()})
        self.assertIn(".docx", json.loads(antwoord)["fout"])

    def test_beschadigd_datablad(self):
        _, antwoord, _ = self.stuur("/datablad", {"naam": "blad.txt", "inhoud": "geen base64!"})
        self.assertIn("fout", json.loads(antwoord))

    # --- keuzes voor het formulier ----------------------------------------

    def test_briefpapier_wordt_bediend(self):
        _, inhoud, _ = self.haal("/briefpapier")
        uit = json.loads(inhoud)
        self.assertAlmostEqual(uit["pagina"]["breedte"], 210.0, delta=0.5)
        self.assertIn("Schilt Bedrijven B.V.", uit["kop"]["regels"])
        self.assertTrue(uit["kop"]["beelden"])

    def test_beeld_wordt_bediend(self):
        _, inhoud, koppen = self.haal("/beeld/image1.jpeg")
        self.assertEqual(koppen["Content-Type"], "image/jpeg")
        self.assertGreater(len(inhoud), 1000)

    def test_beeld_buiten_het_sjabloon_wordt_geweigerd(self):
        for poging in ("..%2f..%2fetc%2fpasswd", "image3.emf", "bestaatniet.png"):
            with self.subTest(poging), self.assertRaises(urllib.error.HTTPError) as gevangen:
                self.haal(f"/beeld/{poging}")
            self.assertEqual(gevangen.exception.code, 404)

    def test_keuzes_voor_het_formulier(self):
        _, inhoud, _ = self.haal("/keuzes")
        uit = json.loads(inhoud)
        self.assertTrue(uit["secties"]["facturering"])
        self.assertTrue(any(o["naam"] == "Nick Vervoorn" for o in uit["ondertekenaars"]))
        self.assertIn(".pdf", uit["bestandssoorten"])


if __name__ == "__main__":
    unittest.main()
