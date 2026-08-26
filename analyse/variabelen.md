# Invulvariabelen

> **Status: niet geverifieerd.** Deze tabel is overgenomen uit jouw aanvulling
> (§1) plus de variabelen die in de kickoff-prompt genoemd worden. Er stonden nog
> geen brieven in `bronbrieven/`, dus niets hiervan is tegen de praktijk
> gecontroleerd en de kolom "waarden in de brieven" is nog leeg. Zodra de brieven
> er zijn vul ik die kolom, corrigeer ik de types en voeg ik toe wat ontbreekt.

## 1. Klant en briefkop

| Variabele | Type | Waarden in de brieven | Verplicht | Opmerking |
|---|---|---|---|---|
| `klantnaam` | tekst | nog te bepalen | ja | Naam van de contactpersoon |
| `organisatie` | tekst | nog te bepalen | nee | Alleen bij zakelijk; bepaalt mede de aanhef |
| `straat_huisnummer` | tekst | nog te bepalen | ja | |
| `postcode` | tekst | nog te bepalen | ja | Nederlandse notatie, `1234 AB` |
| `plaats` | tekst | nog te bepalen | ja | |
| `briefdatum` | datum | nog te bepalen | ja | Standaard vandaag, handmatig te overschrijven |
| `projectnummer` | tekst | nog te bepalen | ja | Opbouw nog onbekend — zie vragen.md #1 |
| `referentie` | tekst | nog te bepalen | ja | Het veld "Ref." — opbouw onbekend, zie vragen.md #1 |

## 2. Aard van de offerte

| Variabele | Type | Waarden in de brieven | Verplicht | Opmerking |
|---|---|---|---|---|
| `klanttype` | keuze | nog te bepalen | ja | Vermoedelijk `particulier` / `zakelijk`; stuurt aanhef, betreft-regel en btw-weergave |
| `locatieaanduiding` | tekst | nog te bepalen | ja | Het deel tussen aanhalingstekens in de betreft-regel — zie vragen.md #3 |
| `aantal_binnenunits` | getal | nog te bepalen | ja | Stuurt enkelvoud/meervoud in de lopende tekst |
| `opstelling_buitenunit` | keuze | nog te bepalen | ja | Bijv. muurbeugel, plat dak, op de grond — waarden uit de brieven halen |

## 3. Aanbiedingsspecificatie — herhalend

Dit is geen losse variabele maar een lijst van 1..n regels. Per regel
vermoedelijk onderstaande velden; te bevestigen tegen de brieven (vragen.md #4).

| Veld per regel | Type | Verplicht | Opmerking |
|---|---|---|---|
| `ruimte` | tekst | ja | Ruimte of verdieping |
| `merk` | tekst | ja | |
| `type` | tekst | ja | Typeaanduiding |
| `vermogen_kw` | getal | ja | In kW |
| `aantal` | getal | ja | |

De opmaak verschilt mogelijk tussen één en meerdere regels — zie vragen.md #5.

## 4. Prijs en voorwaarden

| Variabele | Type | Waarden in de brieven | Verplicht | Opmerking |
|---|---|---|---|---|
| `totaalprijs` | bedrag | nog te bepalen | ja | In- of exclusief btw nog onbekend, zie vragen.md #2. Notatie `€ 4.995,00` doet de tool |
| `btw_tarief` | keuze | nog te bepalen | ja | Vermoedelijk 21%; verlaagd tarief te controleren, zie vragen.md #4 |
| `levering` | keuze uit blokken | nog te bepalen | ja | Variant uit de tekstblokkenbibliotheek |
| `facturering` | keuze uit blokken | nog te bepalen | ja | Variant uit de tekstblokkenbibliotheek |
| `betaling` | keuze uit blokken | nog te bepalen | ja | Variant uit de tekstblokkenbibliotheek |
| `geldigheidsduur` | nog te bepalen | nog te bepalen | ja | Vaste tekst of variabel — uit de brieven af te leiden |
| `garantietermijn` | nog te bepalen | nog te bepalen | ja | Let op afwijkingen tussen brieven |

## 5. Ondertekenaar

| Variabele | Type | Waarden | Verplicht | Opmerking |
|---|---|---|---|---|
| `ondertekenaar` | keuze | `nick_vervoorn`, `john_van_de_wetering`, `ricardo_rozendaal` | ja | Gegevens staan in `config/ondertekenaars.yaml` |

## 6. Afgeleide waarden — niet invullen, wel gebruiken in de tekst

De tool leidt deze zelf af; ze staan niet in het formulier.

| Naam | Afgeleid van | Gebruik |
|---|---|---|
| `is_meervoud` | `aantal_binnenunits > 1` | "de unit" versus "de units" |
| `aanhef` | `klanttype`, `organisatie`, `klantnaam` | u versus jij, aanhefregel |
| `prijs_geformatteerd` | `totaalprijs` | Nederlandse notatie `€ 4.995,00` |
