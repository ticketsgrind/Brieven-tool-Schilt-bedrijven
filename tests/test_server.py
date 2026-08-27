"""Toetst de lokale app: de antwoorden die het scherm van de motor krijgt."""

import json
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

    # --- het scherm --------------------------------------------------------

    def test_scherm_wordt_bediend(self):
        code, inhoud, koppen = self.haal("/")
        self.assertEqual(code, 200)
        self.assertIn("text/html", koppen["Content-Type"])
        self.assertIn(b"Brieventool", inhoud)

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

    def test_keuzes_voor_het_formulier(self):
        _, inhoud, _ = self.haal("/keuzes")
        uit = json.loads(inhoud)
        self.assertTrue(uit["secties"]["facturering"])
        self.assertTrue(any(o["naam"] == "Nick Vervoorn" for o in uit["ondertekenaars"]))
        self.assertIn(".pdf", uit["bestandssoorten"])


if __name__ == "__main__":
    unittest.main()
