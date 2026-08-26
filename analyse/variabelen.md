# Invulvariabelen

Afgeleid uit 16 sjablonen (`bronbrieven/`) en 7 uitgewerkte brieven
(`bronbrieven/uitgewerkt/`). De kolom "waarden in de brieven" bevat alleen wat
werkelijk is aangetroffen.

## 1. Klant en geadresseerde

| Variabele | Type | Waarden in de brieven | Verplicht | Opmerking |
|---|---|---|---|---|
| `klanttype` | keuze | `particulier`, `zakelijk` | ja | Stuurt btw-regel, facturering, kredietwaardigheid en ontbindingsrecht |
| `organisatie` | tekst | naam van de organisatie | nee | Alleen zakelijk; eerste regel van het adresblok |
| `aanspreekvorm` | keuze | `de heer`, `mevrouw`, `de heer en mevrouw`, `Fam.` | ja | Bij `Fam.` vervalt "T.a.v." |
| `voorletters` | tekst | `P.`, `D.`, `K.`, `B.`, `L.` | nee | Alleen bij een individuele contactpersoon |
| `achternaam` | tekst | achternaam van de contactpersoon | ja | |
| `straat_huisnummer` | tekst | straatnaam met huisnummer | ja | |
| `postcode` | tekst | `1234 AB` | ja | Nederlandse notatie `1234 AB` |
| `plaats` | tekst | plaatsnaam | ja | Kapitalisatie inconsistent, zie vragen.md #5 |
| `land` | tekst | `Nederland` | nee | 1× aangetroffen; alleen tonen indien ingevuld |
| `email_klant` | tekst | e-mailadres van de contactpersoon | nee | In 3 van de 7 uitgewerkte brieven |

## 2. Briefkop en kenmerken

| Variabele | Type | Waarden in de brieven | Verplicht | Opmerking |
|---|---|---|---|---|
| `briefdatum` | datum | `2 april 2026`, `26 augustus 2026` | ja | Voluit Nederlands. Standaard vandaag |
| `plaats_afzender` | tekst | `Meerkerk` | ja | Constante |
| `documentsoort` | keuze | `offerte`, `opdrachtbevestiging` | ja | Zie vragen.md #8 |
| `projectnummer` | tekst | zie hieronder | ja | |
| `referentie` | tekst | zie hieronder | ja | |
| `installatietype` | keuze | `airconditioning`, `koelmachine`, `mechanische ventilatie`, `warmtepomp`, `luchtslangsysteem` | ja | Stuurt betreft-regel, aanleiding en garantie |

### Opbouw `projectnummer`

Zeven waarnemingen: zes maal `Q.<7 cijfers>.6.01` en eenmaal `P.<7 cijfers>.6.01`.

Patroon: `<letter>.<7 cijfers>.<6>.<01>`

- **letter** — `Q.` bij alle zes de offertes, `P.` bij de enige
  opdrachtbevestiging. Sterk vermoeden: Q = offerte (quote), P = project.
- **7 cijfers** — loopt op met de datum (1007999 in maart → 1077218 in augustus).
  Komt vrijwel zeker uit een ander systeem en is niet af te leiden.
- **`.6.`** — constant in alle zeven; vermoedelijk de code van de business unit.
- **`.01`** — constant; vermoedelijk een volgnummer binnen het project.

Zie vragen.md #1: alleen `.6.01` is automatisch in te vullen, het middendeel niet.

### Opbouw `referentie`

Zeven waarnemingen: `RH/RdJ/SA35709`, `NV/RdJ/SA35738`, `NV/VL/SA35862`, `NV/SA35900`, `NV/LH/SA35923`.

Patroon: `<initialen ondertekenaar>/[<initialen opsteller>/]SA<5 cijfers>`

- eerste deel volgt de ondertekenaar: `NV` = Nick Vervoorn, `RH` = Robert Hartman.
- tweede deel is optioneel (ontbreekt in `NV/SA35900`) en is een tweede persoon:
  `RdJ`, `VL`, `LH`.
- `SA` + volgnummer loopt op met de datum: 35709 (2 maart) → 35923 (26 augustus).

De tool kan het eerste deel en het `SA`-voorvoegsel voorstellen; het volgnummer
niet. Zie vragen.md #1.

## 3. Aanbiedingsspecificatie — herhalende lijst

Geen keuze uit een lijst maar 1..n regels. In het sjabloon een loop.

| Veld per regel | Type | Waarden | Verplicht | Opmerking |
|---|---|---|---|---|
| `positie` | tekst | `A.`, `B.`, `Pos A.`, `pos. A` | nee | Alleen bij meerdere prijsvarianten |
| `ruimte` | tekst | `T.b.v. de slaapkamer:`, `T.b.v. woonkamer, slaapkamer, werkkamer en de zolder:`, `Vervanging airconditioning t.b.v. de grote kantoren aan de achterzijde` | nee | Kopregel boven de installatieregel |
| `aantal_systemen` | getal | 1, 2, 3 | ja | Wordt uitgeschreven: `één`, `twee`, `drie` |
| `systeemsoort` | keuze | `splitsystem`, `multi-splitsystem`, `VRF systeem`, `lucht-water warmtepomp`, `vloeistofkoelmachine` | ja | |
| `montagewijze` | keuze | `wandmontage`, `vloermontage`, `wand/vloermontage`, `plafondinbouwmontage`, `plafondonderbouwmontage`, `montage boven het systeemplafond`, `buitenopstelling` | ja | |
| `merk` | keuze | `Panasonic`, `Toshiba`, `LG`, `Mitsubishi Electric`, `Daikin`, `Carrier`, `Stork`, `Trox`, `KE-Fibertec` | ja | |
| `type_binnendeel` | tekst | `KIT-71PU3Z5`, `CS-TZ35CKEW`, `RAV-HM901UTP` | ja | |
| `aantal_binnendelen` | getal | 1, 2, 3 | nee | Alleen bij multi-split/VRF |
| `type_buitendeel` | tekst | `CU-2Z50CBE`, `U-71PZ3E5A`, `RAS-2M18G3AVG` | nee | Alleen bij multi-split/VRF |

**Opmaak bij één versus meerdere regels.** Bij één installatie is het lopende
tekst zonder opsommingsteken. Bij meerdere regels blijft het lopende tekst, maar
krijgt elke regel een `ruimte`-kopregel erboven. Er is in geen enkele brief een
tabel of bullet-opsomming gebruikt voor de specificatie. De enkelvoud/meervoud-
verschillen zitten in de omliggende alinea's, niet in de opsomming zelf.

## 4. Systeemomschrijving en werkzaamheden

| Variabele | Type | Waarden in de brieven | Verplicht | Opmerking |
|---|---|---|---|---|
| `aantal_binnenunits` | getal | 1 t/m 3 | ja | Stuurt enkelvoud/meervoud in de hele brief |
| `aantal_buitenunits` | getal | 1, 2 | ja | Stuurt enkelvoud/meervoud van de buitenunit-alinea's |
| `model_binnenunit` | keuze | `wand`, `cassette`, `kanaal`, `vloer`, `plafondonderbouw`, `vrf` | ja | Bepaalt de omschrijvingsalinea |
| `opstelling_buitenunit` | keuze | `muursteun`, `plat_dak`, `bigfoot`, `grond` | ja | Vier varianten aangetroffen |
| `condensafvoer` | keuze | `riolering_derden`, `condenswaterpomp`, `natuurlijk_verloop`, `aanwezige_afvoer` | ja | |
| `bediening` | keuze | `infrarood`, `bedraad` | ja | |
| `winterregeling` | ja/nee | | ja | Alinea over functioneren tot -15 °C |
| `storingscontact` | ja/nee | | nee | Bedrijf-/storingscontact voor GBS |
| `verse_luchtaansluiting` | ja/nee | | nee | Alleen cassette |
| `elektra_derden` | ja/nee | | nee | Alleen VRF/grote projecten |
| `technische_specificaties` | keuze | `uitgeschreven`, `zie_bijlage`, `geen` | ja | Zie vragen.md #9 |
| `werk_inclusief` | meervoudige keuze | 7 regels, zie teksten.yaml | ja | |
| `werk_exclusief` | meervoudige keuze | 12 regels, zie teksten.yaml | ja | |

## 5. Prijs en voorwaarden

| Variabele | Type | Waarden in de brieven | Verplicht | Opmerking |
|---|---|---|---|---|
| `prijsregels` | lijst | 1..n | ja | Per regel `positie` (optioneel) en `bedrag` |
| `prijssoort` | keuze | `totaalprijs`, `raamprijs` | ja | `raamprijs` bij grote projecten |
| `totaalprijs` | bedrag | `€ 3.700,-` t/m `€ 1.265.000,-` | ja | Notatie inconsistent, zie vragen.md #10 |
| `meerprijs_coating` | bedrag | open in sjablonen | nee | |
| `meerprijs_ral` | bedrag | open in sjablonen | nee | |
| `meerprijs_advies` | bedrag | open | nee | Zwaardere unit, 1× aangetroffen |
| `btw_weergave` | afgeleid | `exclusief` / `inclusief` | ja | Volgt `klanttype` — bevestigd in alle 7 uitgewerkte brieven |
| `btw_tarief` | keuze | `21%` | ja | Alleen 21% aangetroffen; verlaagd tarief komt niet voor |
| `condenspomp_meerprijs` | bedrag | `€ 220,-` (zakelijk), `€ 260,-` (particulier) | nee | Zie vragen.md #3 |
| `facturering` | keuze uit blokken | 8 varianten | ja | Zie teksten.yaml |
| `betaling` | keuze uit blokken | 4 varianten | ja | Zie teksten.yaml |
| `documentatie_bijgevoegd` | ja/nee | | ja | |
| `onderhoud_alinea` | ja/nee | | ja | Standaard aan |

**Constanten, geen variabelen.** Deze staan in alle brieven identiek en horen
niet in het formulier:

- levertijd: `in onderling overleg`
- levering: `franco werk`
- geldigheidsduur: `30 dagen`
- garantietermijn airconditioning: `12 maanden`
- betalingstermijn zakelijk: `30 dagen na de factuurdatum`

## 6. Ondertekenaar

| Variabele | Type | Waarden | Verplicht | Opmerking |
|---|---|---|---|---|
| `ondertekenaar` | keuze | `nick_vervoorn`, `john_van_de_weetering`, `ricardo_rozendaal`, `robert_hartman` | ja | Vier personen aangetroffen, zie vragen.md #11 |
| `opsteller_initialen` | tekst | `RdJ`, `VL`, `LH` | nee | Tweede deel van `referentie` |

Gegevens per persoon staan in `config/ondertekenaars.yaml`.

## 7. Afgeleide waarden — niet invullen, wel gebruiken

| Naam | Afgeleid van | Gebruik |
|---|---|---|
| `is_meervoud_binnen` | `aantal_binnenunits > 1` | `de binnenunit is` ↔ `de binnenunits zijn` |
| `is_meervoud_buiten` | `aantal_buitenunits > 1` | `de buitenunit wordt` ↔ `de buitenunits worden` |
| `is_meervoud_installatie` | `len(prijsregels) > 1` | `een airconditioninginstallatie` ↔ `airconditioninginstallaties` |
| `aanhef` | `aanspreekvorm`, `achternaam` | `Geachte heer <achternaam>,` |
| `adresregel_organisatie` | `organisatie` | Alleen tonen indien ingevuld |
| `btw_weergave` | `klanttype` | `exclusief` bij zakelijk, `inclusief` bij particulier |
| `prijs_geformatteerd` | `totaalprijs` | `€ 4.995,00` — zie vragen.md #10 |
| `telwoord` | een getal | `1` → `één`, `2` → `twee`, `3` → `drie` |
