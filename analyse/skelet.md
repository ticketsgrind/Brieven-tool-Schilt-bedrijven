# Skelet van een offertebrief

Gebaseerd op 16 sjablonen uit `bronbrieven/` en 7 uitgewerkte brieven uit
`bronbrieven/uitgewerkt/` (4 × .docx, 3 × .pdf).

De structuur is opvallend stabiel: alle 16 sjablonen volgen dezelfde volgorde.
Wat verschilt zit vrijwel volledig in twee secties — de systeemomschrijving en de
werkzaamheden — plus een handvol voorwaardelijke alinea's. De juridische staart
(algemene voorwaarden, garantie, aansprakelijkheid, privacy) is in alle brieven
identiek op één uitzondering na (koelmachine, zie `vragen.md`).

## Overzicht

| # | Sectie | Altijd? | Varieert met |
|---|---|---|---|
| 1 | Briefkop (bedrijfsgegevens) | altijd | — (vast, staat in de Word-header) |
| 2 | Geadresseerde | altijd | `klanttype` (organisatieregel), aanhefvorm |
| 3 | Betreft-regel | altijd | `installatietype`, `klanttype`, `locatieaanduiding` |
| 4 | Plaats en datum | altijd | `briefdatum` |
| 5 | Project no. en Ref. | altijd | `documentsoort`, `ondertekenaar`, `opsteller` |
| 6 | Aanhef | altijd | geslacht/aantal geadresseerden, achternaam |
| 7 | Aanleiding | altijd | `aanleiding`, `installatietype`, enkelvoud/meervoud |
| 8 | Kop "Aanbieding" | altijd | `documentsoort` (bij opdracht: "Opdracht") |
| 9 | Uitgangspunten aanvraag | voorwaardelijk | alleen bij grote projecten/raamprijs |
| 10 | Aanbiedingsspecificatie | altijd | **herhalend** — 1..n installatieregels |
| 11 | Systeemomschrijving | altijd | `model_binnenunit`, enkelvoud/meervoud |
| 12 | Buitenunit | altijd | `opstelling_buitenunit`, enkelvoud/meervoud |
| 13 | Winterregeling | voorwaardelijk | ja/nee |
| 14 | Leidingwerk en condensafvoer | altijd | `condensafvoer`, enkelvoud/meervoud |
| 15 | Bediening | altijd | `bediening` (infrarood / bedraad) |
| 16 | Elektra door derden | voorwaardelijk | alleen VRF / grotere projecten |
| 17 | Technische specificaties | voorwaardelijk | uitgeschreven, "zie bijlage(n)", of weg |
| 18 | Inbegrepen werkzaamheden | altijd | keuzelijst |
| 19 | Niet-inbegrepen werkzaamheden | altijd | keuzelijst |
| 20 | Uitgangspunten offerte | voorwaardelijk | vrije tekst |
| 21 | Totaalprijs | altijd | 1..n posities, meerprijzen |
| 22 | Onderhoud niet inbegrepen | vrijwel altijd | — |
| 23 | Meerprijs condenswaterpomp | voorwaardelijk | `klanttype` (bedrag verschilt!) |
| 24 | Btw-regel | altijd | `klanttype` |
| 25 | Uitgangspunten prijsvorming | vrijwel altijd | — |
| 26 | Ontbindingsrecht bij late levering | voorwaardelijk | alleen `klanttype == particulier` |
| 27 | Levering | altijd | — |
| 28 | Facturering en betaling | altijd | **keuzeblok**, verschilt per `klanttype` |
| 29 | Kredietwaardigheid | voorwaardelijk | alleen zakelijk |
| 30 | Algemene voorwaarden | altijd | — |
| 31 | Garantietermijn | altijd | `installatietype` |
| 32 | Aansprakelijkheid | vrijwel altijd | — |
| 33 | Tot slot | altijd | documentatie bijgevoegd ja/nee |
| 34 | Geldigheidsduur | altijd | — (overal 30 dagen) |
| 35 | Slotzin | vrijwel altijd | — |
| 36 | Privacy-alinea | altijd | — |
| 37 | Ondertekening | altijd | `ondertekenaar` |
| 38 | Voettekst | altijd | — (vast, staat in de Word-footer) |

---

## Sectie voor sectie

### 1. Briefkop — altijd
Staat in de Word-header, niet in de brieftekst: Schilt Bedrijven B.V., Energieweg
29, 4231 DJ Meerkerk, telefoon, e-mail, website, btw-nummer, KvK, bankgegevens en
G-rekening. In alle 16 sjablonen letterlijk gelijk. Zie `config/ondertekenaars.yaml`
onder `bedrijf`.

### 2. Geadresseerde — altijd
Blok linksboven. Opbouw:

    [organisatie]            ← alleen zakelijk
    T.a.v. de heer <initiaal>. <achternaam>
    <straat en huisnummer>
    <postcode>  <PLAATS>
    [land]                   ← alleen buitenland, 1× gezien ("Nederland")
    [e-mailadres]            ← in 3 van de 7 uitgewerkte brieven

Bij een echtpaar vervalt "T.a.v." en staat er alleen "Fam. <achternaam>". De
plaats staat in de uitgewerkte brieven soms in kapitalen en soms niet — niet
consistent, zie `vragen.md`.

### 3. Betreft-regel — altijd
`Betreft` + tab + tekst. De sjablonen laten het achterste deel open. Gevonden
varianten:

- `Airconditioning t.b.v.` (11 sjablonen, open eind)
- `Airconditioning t.b.v. uw woning` (particulier)
- `Airconditioning t.b.v. uw vestiging te <plaats>` (zakelijk)
- `Airconditioning t.b.v. uw project <projectnaam>` (zakelijk, aannemer)
- `Airconditioning t.b.v. uw twee slaapkamers en de keuken` (particulier, ruimten)
- `Vervangen airconditioning t.b.v. uw woning <adres> <plaats>`
- `Koelmachine t.b.v.` / `Mechanische ventilatie t.b.v.`

Het eerste woord volgt dus `installatietype`, en wat erachter staat is een vrij
tekstveld met een aantal veelgebruikte vormen. Anders dan de aanvulling
suggereerde staat de locatieaanduiding **niet** tussen aanhalingstekens — in geen
van de 23 bestanden. Zie `vragen.md`.

### 4. Plaats en datum — altijd
`Meerkerk` + tab + datum, voluit in het Nederlands: `26 augustus 2026`.

### 5. Project no. en Ref. — altijd
Twee regels:

    Ons project no. Q.1077218.6.01
    Ref. NV/LH/SA35923

Beide patronen zijn afleidbaar; zie `variabelen.md` §2 en `vragen.md` #1.

### 6. Aanhef — altijd
De sjablonen bevatten vijf verschillende schrijfwijzen van dezelfde aanhef, wat
puur slordigheid lijkt (`Geachte heer/mevrouw,` / `Geachte heer/mevrouw ,` /
`Geachte heer ,` / `Geachte heer,mevrouw,` / `Geachte heer`). In de uitgewerkte
brieven staat altijd de ingevulde vorm: `Geachte heer <achternaam>,` en
`Geachte heer en mevrouw <achternaam>,`. Dit wordt één
blok met variabelen. Zie `vragen.md`.

### 7. Aanleiding — altijd
Twee hoofdvarianten, in de sjablonen allebei aanwezig zodat de opsteller er één
wegknipt:

- na een bezoek: `Naar aanleiding van het aangenaam onderhoud tussen u en <adviseur> d.d. <datum> jl. ...`
- na een aanvraag: `Naar aanleiding van uw aanvraag d.d. <datum> jl. ...`

In de uitgewerkte brieven kwamen daar nog bij: `uw telefonische aanvraag`,
`ons servicebezoek d.d. ...`, en bij een opdrachtbevestiging
`Onder dankzegging bevestigen wij hiermede uw schriftelijke opdrachtnr. <nr> d.d. <datum> jl. ...`.

Het staartstuk volgt `installatietype` en enkelvoud/meervoud:
`een airconditioninginstallatie` / `airconditioninginstallaties` /
`een koelmachine` / `een mechanisch ventilatiesysteem` / `een warmtepompinstallatie`.
**Dit is precies het geval waar enkelvoud/meervoud geen apart blok is maar een
variabele binnen één blok.**

### 8. Kop "Aanbieding" — altijd
`Aanbieding` + `Wij specificeren onze aanbieding als volgt:`. Bij een
opdrachtbevestiging wordt dit `Opdracht` + `Wij specificeren de opdracht als volgt:`.

### 9. Uitgangspunten aanvraag — voorwaardelijk
Alleen bij grote projecten (1 van de 23 bestanden): kop `Uitgangspunten:`,
`Wij hebben ons voorstel gebaseerd op de volgende uitgangspunten:` gevolgd door
de aanvraagomschrijving van de klant en tekeningnummers. Vrije tekst.

### 10. Aanbiedingsspecificatie — altijd, herhalend
Eén tot n regels, elk beginnend met `Het leveren en monteren van ...`. Zie
`variabelen.md` §3. Bij meerdere regels krijgt elke regel vaak een kopje met de
ruimte erboven (`T.b.v. de slaapkamer:`) en bij meerdere prijsvarianten een
letteraanduiding (`A.` / `B.`).

### 11. Systeemomschrijving — altijd
Per model binnenunit één alinea, in enkelvoud- en meervoudvorm. Zes modellen
gevonden: wand, cassette, kanaal (boven systeemplafond), vloer/laag-aan-de-muur,
plafondonderbouw, VRF. Zie `teksten.yaml`, sectie `systeemomschrijving`.

### 12. Buitenunit — altijd
Drie opstellingsvarianten (muursteun / plat dak / BigFoot-frame), elk in
enkelvoud en meervoud, plus twee vaste alinea's (geruisarm/omkasting, en
optionele coating).

### 13. Winterregeling — voorwaardelijk
Eén alinea, in 10 van de 16 sjablonen aanwezig.

### 14. Leidingwerk en condensafvoer — altijd
Vier condensafvoervarianten (riolering door derden / condenswaterpomp /
natuurlijk verloop / aanwezige afvoer), elk in enkelvoud en meervoud.

### 15. Bediening — altijd
`De <unit> is voorzien van een <infrarood|bedraad> afstandsbedieningspaneel.`

### 16. Elektra door derden — voorwaardelijk
Alleen VRF en grotere projecten: kop `Elektra:` met een opsomming van
voorzieningen die derden moeten leveren.

### 17. Technische specificaties — voorwaardelijk
Drie vormen: volledig uitgeschreven specificatieblok per unit, of de verwijzing
`Zie bijlage(n)`, of helemaal afwezig. Zie `vragen.md` — dit is de zwaarste
beslissing voor fase 2.

### 18. Inbegrepen werkzaamheden — altijd
`De installatie is aangeboden inclusief:` gevolgd door een keuzelijst. Zeven
regels gevonden.

### 19. Niet-inbegrepen werkzaamheden — altijd
`Niet tot onze werkzaamheden behoren:` gevolgd door een keuzelijst. Twaalf regels
gevonden.

### 20. Uitgangspunten offerte — voorwaardelijk
Kop `Uitgangspunten:` met vrije tekst; 2 van de 23 bestanden.

### 21. Totaalprijs — altijd
Kop `Totaalprijs:` (bij een raamprijs: `Raamprijs:`, bij warmtepomp `Totaalprijs`
met andere zin). Eén tot n prijsregels plus optionele meerprijzen (coating,
RAL-kleur, zwaardere unit). Bedragen staan als `€ 7.595,-` of `€ 28.250` —
niet consistent, zie `vragen.md`.

### 22. Onderhoud niet inbegrepen — vrijwel altijd
Vaste alinea, 14 van de 16 sjablonen.

### 23. Meerprijs condenswaterpomp — voorwaardelijk
Vaste alinea, maar het bedrag verschilt tussen zakelijk (€ 220,-) en particulier
(€ 260,-). Zie `vragen.md` #3.

### 24. Btw-regel — altijd
Vier schrijfwijzen gevonden, terug te brengen tot twee betekenissen:

- zakelijk: `De genoemde prijzen zijn exclusief btw.` / `... exclusief 21% btw.`
- particulier: `De genoemde prijzen zijn inclusief btw.` / `... inclusief 21% btw.`

Bevestigd in alle 7 uitgewerkte brieven. Het al dan niet noemen van "21%" is
inconsistent, zie `vragen.md` #2.

### 25. Uitgangspunten prijsvorming — vrijwel altijd
Vaste kop plus drie vaste regels. 13 van de 16 sjablonen.

### 26. Ontbindingsrecht bij late levering — voorwaardelijk
Alleen in de twee particuliere wandsjablonen. Consumentenbepaling. Zie
`vragen.md` #6.

### 27. Levering — altijd
`Levering:` + `De levering geschiedt franco werk.` + `Levertijd: in onderling
overleg.` In alle 15 sjablonen die de sectie hebben letterlijk gelijk; er is dus
maar één leveringsvariant. Zie `vragen.md` #7.

### 28. Facturering en betaling — altijd, keuzeblok
Zeven factureringsvarianten en drie betalingsvarianten. De particuliere
sjablonen hebben een eigen, afwijkend gecombineerd blok. Zie `teksten.yaml`.

### 29. Kredietwaardigheid — voorwaardelijk
Vaste alinea in 13 sjablonen; ontbreekt in de drie particuliere. Zie `vragen.md` #6.

### 30. Algemene voorwaarden — altijd
Metaalunievoorwaarden. In alle 15 letterlijk gelijk.

### 31. Garantietermijn — altijd
Standaardtekst (12 maanden) in 14 sjablonen. Koelmachine en KE-Fibertec wijken af.
Zie `vragen.md` #4.

### 32. Aansprakelijkheid — vrijwel altijd
Twee opsommingsregels (betonboringen, apparatuur onder binnenunits). 14 van de 16.

### 33. Tot slot — altijd
Kop `Tot slot`, optioneel gevolgd door `Wij hebben documentatie van de
betreffende apparatuur bijgevoegd.`

### 34. Geldigheidsduur — altijd
`Deze aanbieding wordt 30 dagen na heden gestand gedaan, daarna komt deze te
vervallen.` In alle 15 gelijk — 30 dagen is dus een constante, geen variabele.

### 35. Slotzin — vrijwel altijd
`Wij zijn ervan overtuigd u hiermede een zeer bruikbare en prijsgunstige
aanbieding te hebben gemaakt ...`. Ontbreekt in de opdrachtbevestiging.

### 36. Privacy-alinea — altijd
Verwijzing naar www.schiltbedrijven.nl/privacyverklaring.

### 37. Ondertekening — altijd
`Vertrouwende u hiermee van dienst te zijn geweest, tekenen wij met vriendelijke
groeten,` + `Business Unit Schilt Airconditioning` + `MEERKERK` + naam + functie.
De sjablonen bevatten alle drie de namen onder elkaar; de opsteller verwijdert er
twee. Zie `config/ondertekenaars.yaml`.

### 38. Voettekst — altijd
Staat in de Word-footer: paginanummering, de Metaalunie-regel en de
privacyverwijzing, plus de classificatiemarkering `C2-Vertrouwelijk`.
Zie `vragen.md` #12.
