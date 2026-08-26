"""Zet een ingevuld offerteformulier om in de tekst van een brief.

Per sectie wordt bepaald welke tekstblokken meegaan (op basis van hun
voorwaarde) en worden de {{ }}-plaatshouders ingevuld. Het resultaat is een
woordenboek van sectienaam naar een lijst alinea's, dat het Word-sjabloon
alleen nog hoeft af te lopen. De sectievolgorde volgt analyse/skelet.md.

Blokken die naar `regel` verwijzen worden herhaald: eenmaal per installatie of
per prijsregel. De rest wordt eenmalig beoordeeld.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Mapping

from .bibliotheek import Bibliotheek, Tekstblok
from .expressies import ExpressieFout, evalueer, is_waar
from .opmaak import FUNCTIES, bedrag, briefdatum, postcode, telwoord

# Welke lijst uit de offerte hoort bij welke herhalende sectie.
LOOPSECTIES = {
    "specificatie": "installaties",
    "prijs": "prijsregels",
}

PLAATSHOUDER = re.compile(r"\{\{(.+?)\}\}")


class SamenstelFout(ValueError):
    """De offerte kan niet worden samengesteld."""


@dataclass
class Brief:
    """Het samengestelde resultaat, klaar voor het Word-sjabloon."""
    secties: dict[str, list[str]] = field(default_factory=dict)
    context: dict[str, Any] = field(default_factory=dict)
    gebruikte_blokken: list[str] = field(default_factory=list)
    waarschuwingen: list[str] = field(default_factory=list)

    def tekst(self) -> str:
        """Platte tekst van de hele brief. Handig om snel te controleren."""
        regels: list[str] = []
        for sectie, alineas in self.secties.items():
            if alineas:
                regels.append(f"[{sectie}]")
                regels.extend(alineas)
                regels.append("")
        return "\n".join(regels)


def stel_samen(offerte: Mapping[str, Any], bib: Bibliotheek) -> Brief:
    context = _bouw_context(offerte, bib)
    brief = Brief(context=context)

    # Binnen een keuzegroep gaat hoogstens één blok mee: de eerste die past.
    # De volgorde in teksten.yaml is dus de voorrangsvolgorde, met de meest
    # algemene variant onderaan als terugval.
    vergeven_groepen: set[str] = set()

    for sectie in bib.secties:
        alineas: list[str] = []
        lijstnaam = LOOPSECTIES.get(sectie)
        # Prijsregels zijn al opgemaakt in de context; installaties niet.
        regels = list(context.get(lijstnaam) or []) if lijstnaam else []

        for groep, is_herhalend in _groepeer(bib.per_sectie(sectie), bool(lijstnaam)):
            if is_herhalend:
                for nummer, regel in enumerate(regels, start=1):
                    lokaal = dict(context, regel=regel, regelnummer=nummer)
                    for blok in groep:
                        if _meegaan(blok, lokaal, brief):
                            alineas.append(_vul_in(blok, lokaal))
                            _onthoud(brief, blok.id)
            else:
                for blok in groep:
                    if blok.keuzegroep and blok.keuzegroep in vergeven_groepen:
                        continue
                    if _meegaan(blok, context, brief):
                        alineas.append(_vul_in(blok, context))
                        _onthoud(brief, blok.id)
                        if blok.keuzegroep:
                            vergeven_groepen.add(blok.keuzegroep)

        brief.secties[sectie] = alineas

    return brief


def _groepeer(blokken: list[Tekstblok], sectie_herhaalt: bool):
    """Splitst een sectie in aaneengesloten reeksen herhalende en vaste blokken.

    In de specificatie staan kopregel en installatieregel na elkaar; die horen
    samen per installatie herhaald te worden, niet ieder apart over alle
    installaties. In de prijssectie staan de vaste kop en btw-regel eromheen.
    """
    groep: list[Tekstblok] = []
    huidige: bool | None = None
    for blok in blokken:
        herhaalt = sectie_herhaalt and _verwijst_naar_regel(blok)
        if huidige is None or herhaalt == huidige:
            groep.append(blok)
        else:
            yield groep, huidige
            groep = [blok]
        huidige = herhaalt
    if groep:
        yield groep, bool(huidige)


def _onthoud(brief: Brief, blok_id: str) -> None:
    """Houdt bij welke blokken zijn gebruikt, elk hoogstens één keer."""
    if blok_id not in brief.gebruikte_blokken:
        brief.gebruikte_blokken.append(blok_id)


def _meegaan(blok: Tekstblok, context: Mapping[str, Any], brief: Brief | None = None) -> bool:
    """Bepaalt of dit blok in de brief komt.

    Een blok met een omschrijving is een keuze uit een menu. Daar is de keuze
    van de opsteller leidend: staat het blok in `gekozen_blokken`, dan gaat het
    mee. Klopt de voorwaarde daar niet bij -- bijvoorbeeld de particuliere
    factureringsregel op een zakelijke offerte -- dan gaat het blok wél mee maar
    komt er een waarschuwing bij, zodat de fout opvalt vóór de brief de deur uit
    gaat in plaats van erna.
    """
    try:
        voorwaarde_klopt = is_waar(blok.voorwaarde, context, FUNCTIES)
    except ExpressieFout as fout:
        raise SamenstelFout(f"blok {blok.id!r}: {fout}") from fout

    if not blok.is_keuze:
        return voorwaarde_klopt

    gekozen = context.get("gekozen_blokken")
    if gekozen is None:
        return voorwaarde_klopt          # geen keuzelijst: voorwaarde beslist
    if blok.id not in gekozen:
        return False
    if not voorwaarde_klopt and brief is not None:
        _waarschuw(brief, f"blok {blok.id!r} is gekozen maar de voorwaarde "
                          f"{blok.voorwaarde!r} klopt niet voor deze offerte")
    return True


def _waarschuw(brief: Brief, tekst: str) -> None:
    if tekst not in brief.waarschuwingen:
        brief.waarschuwingen.append(tekst)


def _verwijst_naar_regel(blok: Tekstblok) -> bool:
    return "regel." in blok.voorwaarde or "regel." in blok.tekst


def _vul_in(blok: Tekstblok, context: Mapping[str, Any]) -> str:
    def vervang(treffer: re.Match[str]) -> str:
        expressie = treffer.group(1).strip()
        try:
            waarde = evalueer(expressie, context, FUNCTIES)
        except ExpressieFout as fout:
            raise SamenstelFout(f"blok {blok.id!r}: {fout}") from fout
        return "" if waarde is None else str(waarde)

    ingevuld = PLAATSHOUDER.sub(vervang, blok.tekst)
    # Waar een plaatshouder leeg blijft ontstaan dubbele spaties. Tabs blijven
    # staan: die lijnen de betreft-regel en de factureringstermijnen uit.
    ingevuld = re.sub(r" {2,}", " ", ingevuld)
    return "\n".join(regel.rstrip() for regel in ingevuld.split("\n")).strip()


# ---------------------------------------------------------------------------
# Afgeleide waarden: alles wat de tool zelf uitrekent en niet gevraagd wordt.
# ---------------------------------------------------------------------------

INSTALLATIE_OMSCHRIJVING = {
    "airconditioning": ("een airconditioninginstallatie", "airconditioninginstallaties"),
    "koelmachine": ("een koelmachine", "koelmachines"),
    "mechanische ventilatie": ("een mechanisch ventilatiesysteem", "mechanische ventilatiesystemen"),
    "warmtepomp": ("een warmtepompinstallatie", "warmtepompinstallaties"),
    "luchtslangsysteem": ("een luchtslangsysteem", "luchtslangsystemen"),
}

BETREFT_ONDERWERP = {
    "airconditioning": "Airconditioning",
    "koelmachine": "Koelmachine",
    "mechanische ventilatie": "Mechanische ventilatie",
    "warmtepomp": "Warmtepomp",
    "luchtslangsysteem": "Luchtslangsysteem",
}

AANHEFVORM = {
    "de heer": "heer",
    "mevrouw": "mevrouw",
    "de heer en mevrouw": "heer en mevrouw",
    "Fam.": "heer en mevrouw",
}


def _bouw_context(offerte: Mapping[str, Any], bib: Bibliotheek) -> dict[str, Any]:
    ctx: dict[str, Any] = dict(offerte)

    installaties = list(offerte.get("installaties") or [])
    prijsregels = list(offerte.get("prijsregels") or [])

    binnen = offerte.get("aantal_binnenunits")
    if binnen is None:
        binnen = sum(int(i.get("aantal_binnendelen") or 1) for i in installaties) or 1
    buiten = offerte.get("aantal_buitenunits")
    if buiten is None:
        buiten = len(installaties) or 1

    ctx["aantal_binnenunits"] = int(binnen)
    ctx["aantal_buitenunits"] = int(buiten)
    ctx["aantal_installaties"] = len(installaties) or 1

    ctx["is_meervoud_binnen"] = ctx["aantal_binnenunits"] > 1
    ctx["is_meervoud_buiten"] = ctx["aantal_buitenunits"] > 1
    ctx["is_meervoud_installatie"] = len(prijsregels) > 1 or len(installaties) > 1

    soort = str(offerte.get("installatietype") or "airconditioning")
    enkel, meer = INSTALLATIE_OMSCHRIJVING.get(soort, (f"een {soort}", f"{soort}en"))
    ctx["installatie_omschrijving"] = meer if ctx["is_meervoud_installatie"] else enkel

    if not offerte.get("betreft_onderwerp"):
        ctx["betreft_onderwerp"] = BETREFT_ONDERWERP.get(soort, soort.capitalize())

    aanspreek = str(offerte.get("aanspreekvorm") or "de heer")
    ctx["aanspreekvorm_aanhef"] = AANHEFVORM.get(aanspreek, aanspreek)

    ctx["btw_weergave"] = "inclusief" if offerte.get("klanttype") == "particulier" else "exclusief"

    ctx["briefdatum"] = briefdatum(offerte.get("briefdatum"))
    if offerte.get("postcode"):
        ctx["postcode"] = postcode(str(offerte["postcode"]))

    ctx["prijsregels"] = [_verrijk_prijsregel(r) for r in prijsregels]
    ctx["installaties"] = installaties

    for veld in ("meerprijs_coating", "meerprijs_ral", "meerprijs_advies", "totaalprijs"):
        if offerte.get(veld) is not None:
            ctx[veld] = bedrag(offerte[veld])

    ondertekenaar_sleutel = offerte.get("ondertekenaar")
    ondertekenaar = bib.ondertekenaars.get(ondertekenaar_sleutel or "", {})
    if ondertekenaar_sleutel and not ondertekenaar:
        raise SamenstelFout(
            f"ondertekenaar {ondertekenaar_sleutel!r} staat niet in config/ondertekenaars.yaml "
            f"(bekend: {', '.join(sorted(bib.ondertekenaars)) or 'geen'})"
        )
    ctx["ondertekenaar"] = ondertekenaar
    ctx["bedrijf"] = bib.bedrijf

    if not offerte.get("referentie") and ondertekenaar.get("initialen"):
        ctx["referentie"] = _stel_referentie_voor(
            ondertekenaar["initialen"], offerte.get("opsteller_initialen"), offerte.get("sa_nummer")
        )

    ctx["telwoord"] = telwoord
    return ctx


def _verrijk_prijsregel(regel: Mapping[str, Any]) -> dict[str, Any]:
    verrijkt = dict(regel)
    if "bedrag" in verrijkt:
        verrijkt["bedrag"] = bedrag(verrijkt["bedrag"])
    return verrijkt


def _stel_referentie_voor(initialen: str, opsteller: str | None, sa_nummer: Any) -> str:
    """Bouwt Ref. volgens het patroon uit de uitgewerkte brieven.

    <initialen ondertekenaar>/[<initialen opsteller>/]SA<volgnummer>
    Zonder volgnummer blijft het staartstuk leeg, zodat het handmatig ingevuld
    kan worden -- de teller zelf kennen we niet. Zie analyse/vragen.md vraag 1f.
    """
    delen = [initialen]
    if opsteller:
        delen.append(str(opsteller))
    delen.append(f"SA{sa_nummer}" if sa_nummer else "SA")
    return "/".join(delen)
