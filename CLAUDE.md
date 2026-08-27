# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Taal

Deze repository is volledig in het Nederlands: code, commentaar, variabelenamen,
commitberichten en documentatie. De gebruiker werkt in het Nederlands en de
teksten die de tool produceert zijn Nederlandse offertebrieven. Houd dat aan —
schakel niet terug naar Engelse identifiers.

## Wat dit is

Een tool die offertebrieven voor Schilt Airconditioning samenstelt uit een
bibliotheek van tekstblokken, in plaats van tientallen losse Word-sjablonen per
variant. De salesmedewerker beantwoordt een aantal vragen, de tool kiest de
passende blokken en levert een Word-bestand op.

## Commando's

```bash
# Het Word-sjabloon (opnieuw) maken uit een bronbrief
python3 tools/maak_sjabloon.py

# Een brief samenstellen en de tekst tonen
python3 -m brieventool voorbeelden/particulier-wand-enkelvoud.yaml
python3 -m brieventool <offerte>.yaml --blokken          # toon gebruikte blok-id's
python3 -m brieventool <offerte>.yaml --docx uit/brief.docx

# Tests
python3 -m unittest discover -s tests -t .
python3 -m unittest tests.test_samenstellen -v
python3 -m unittest tests.test_samenstellen.TestZakelijkeBrief.test_meervoud

# De tool toetsen tegen een werkelijk verstuurde brief
python3 tools/toets_tegen_echte_brief.py <offerte>.yaml bronbrieven/uitgewerkt/<brief>.docx

# Bronbrieven opnieuw uitlezen na wijziging in bronbrieven/
python3 tools/extract_docx.py
python3 tools/extract_pdf.py bronbrieven/uitgewerkt/<brief>.pdf

# Prototype gelijktrekken na wijziging in analyse/teksten.yaml
python3 ontwerp/ververs_prototype.py
```

## Architectuur

De kern is dat **de inhoud niet in de code zit**. Alle brieftekst staat in
`analyse/teksten.yaml`; de code kiest alleen welke blokken meegaan en vult de
plaatshouders in. Een gewijzigde garantietekst is dus een tekstwijziging, geen
codewijziging.

**De keten:** `analyse/teksten.yaml` (136 blokken) → `bibliotheek.py` laadt ze →
`samenstellen.py` kiest en vult → `sjabloon.py` schrijft het Word-bestand.

**Blokselectie werkt op gewone antwoorden, niet op blok-id's.** Wie
`condensafvoer: natuurlijk_verloop` en `aantal_binnenunits: 3` invult krijgt
vanzelf het blok dat "de units zijn" zegt in plaats van "de unit is". Verschillen
die alleen taalkundig zijn (enkelvoud/meervoud) zijn dus varianten van hetzelfde
blok met elk een eigen voorwaarde, geen aparte tekstblokken. Voeg nooit een
mechanisme toe waarbij de gebruiker blok-id's kiest; `gekozen_blokken` bestaat
alleen als noodrem en geeft een waarschuwing als de voorwaarde niet klopt.

**`expressies.py` evalueert de voorwaarden zonder `eval()`.** Het tekstenbestand
wordt door de gebruiker aangepast en mag daarom geen manier worden om code te
draaien: attribuuttoegang is beperkt tot woordenboeken (anders geeft
`iets.__class__` toegang tot de rest van Python), en functieaanroepen alleen uit
`opmaak.FUNCTIES`. Er is één toegift aan Jinja: `{{ 'x' if voorwaarde }}` zonder
`else` wordt aangevuld.

**Herhalende secties.** `LOOPSECTIES` in `samenstellen.py` koppelt een sectie aan
een lijst uit de offerte (`specificatie` → `installaties`, `prijs` →
`prijsregels`). Een aaneengesloten reeks blokken die naar `regel` verwijst wordt
als geheel per regel herhaald — niet blok voor blok over alle regels, anders
komen eerst alle ruimtekopjes en daarna pas alle installatieregels.

**Keuzegroepen.** Blokken met dezelfde `keuzegroep` sluiten elkaar uit; de eerste
die past wint. De volgorde in `teksten.yaml` is dus de voorrangsvolgorde, met de
meest algemene variant onderaan als terugval.

**Het Word-sjabloon wordt gegenereerd, niet met de hand gemaakt.**
`tools/maak_sjabloon.py` neemt een bronbrief uit `bronbrieven/`, gooit de body
leeg en zet er Jinja-lussen in; briefkop, voettekst, afbeeldingen, marges en
stijlen blijven die van Schilt. Verandert de huisstijl, draai het script dan
opnieuw — bewerk `sjablonen/brief.docx` niet in Word.

`sjabloon.py` vult dat sjabloon zelf in: een .docx is een zip met XML, dus
Jinja over `word/document.xml` en weer inpakken.

**Lees `word/document.xml` nooit in met een XML-lezer om het daarna opnieuw weg
te schrijven.** Het hoofdelement declareert 35 namespaces en somt er in
`mc:Ignorable` tien van op. Een lezer hernoemt de prefixen die hij zelf niet
tegenkomt, waarna `mc:Ignorable` naar prefixen wijst die niet meer bestaan en
Word het bestand als beschadigd beschouwt. Zowel `maak_sjabloon.py` als
`sjabloon.py` doen daarom tekstbewerking op de ruwe bytes en laten alles buiten
de body ongemoeid. Er staan vier tests op, die zowel het sjabloon als een
gemaakte brief vergelijken met de bronbrief.

Wat daaraan hangt: `headerReference type="first"` wijst naar `header1.xml` met
de Schilt-gegevens rechtsboven op pagina 1, `footerReference type="first"` naar
`footer3.xml`, en `titlePg` zet aan dat pagina 1 die afwijkende kop en voet
gebruikt. Alle afbeeldingen zitten in de kop- en voetteksten, niet in de body.

**De opmaak is nagemeten aan de bronbrief, niet benaderd.** Twee dingen bepalen
of de brief er verzorgd uitziet:

- *Witregels.* De bronbrieven zetten een lege alinea na elke gewone alinea.
  Uitzonderingen: opsommingsregels staan tegen elkaar aan (alleen na de laatste
  een witregel), en een met tabs uitgelijnde vervolgregel staat direct onder de
  regel waar hij bij hoort. `_zet_witregels` in `samenstellen.py` bepaalt dat;
  het sjabloon volgt alleen `a.witregel_erna`.
- *Opsommingstekens.* De stijl `Lijstalinea` zorgt alleen voor inspringing. Het
  streepje komt uit een `numPr`-verwijzing naar een lijstdefinitie in
  `numbering.xml`. Zonder die verwijzing staat de regel ingesprongen maar zonder
  teken ervoor.

- *Kopjes.* Kopjes met een dubbele punt zijn **onderstreept**, niet vet.
  `Aanbieding`, `Opdracht`, `Tot slot`, `TECHNISCHE SPECIFICATIES`, `Zie
  bijlage` en de ruimtekopjes zijn **vet** (stijl `kopvet`). Een regel die op
  een dubbele punt eindigt maar langer is dan 45 tekens is een aanloopzin en
  blijft gewoon — zo scheiden de bronbrieven `Wij specificeren onze aanbieding
  als volgt:` van `Voor de prijsvorming zijn wij er van uitgegaan dat:`.
- *Labels in de briefkop.* Blokken met `stijl: label` (`betreft`, `kenmerken`)
  worden bij de tab gesplitst: het label staat op 7 punten (`w:sz` 14) en de
  inhoud op de gewone 9. Zonder dat verschil landt de tab anders en loopt de
  regel scheef.
- *Vette bedragen.* Bij een blok met `stijl: prijs` splitst de motor de regel
  bij het eurobedrag: de aanloopzin blijft gewoon, het bedrag tot en met
  `netto.` wordt vet. `Alinea.tekst` en `Alinea.nadruk` zijn daardoor twee
  tekstdelen in Word; `Alinea.volledig` plakt ze weer aan elkaar voor alles wat
  de brief als platte tekst leest.

Een regel die met een tab of een vaste spatie begint is een uitgelijnde
vervolgregel, geen opsomming — een streepje daarin hoort bij de tekst.

Twee andere dingen zijn subtiel en hebben allebei een test: een alinea die
alleen een `{%p ... %}`-tag bevat wordt zelf verwijderd (maar een zelfsluitende
`<w:p />` mag niet worden opgeslokt, anders verdwijnen de witregels tussen de
secties), en tabtekens uit de gegevens moeten na het invullen worden omgezet in
`<w:tab/>`, anders toont Word ze als spatie en lopen de betreft-regel en de
factureringstermijnen scheef.

De afhankelijkheden zijn PyYAML en Jinja2, allebei pure Python. Er is met opzet
geen Word-bibliotheek nodig: die bestaan vooral om tags te repareren die Word
verspreidt bij handmatig typen, en ons sjabloon wordt gegenereerd.

**`ontwerp/prototype.html`** heeft de bibliotheek ingebakken tussen de
markeringen `/*<blokken>*/` en `/*</blokken>*/`, en spiegelt `samenstellen.py`
in JavaScript. Wijzig je de selectielogica in Python, werk dan ook het prototype
bij, anders lopen ze uiteen. Draai `ontwerp/ververs_prototype.py` na elke
wijziging in `teksten.yaml`; controleer daarna met `node --check` dat het script
nog geldig is, want een fout in de ingebakken gegevens breekt de hele pagina.

## Werken met de teksten

- **Neem de brontekst letterlijk over.** De formuleringen zijn commercieel en
  juridisch bewust zo gekozen. Herschrijf niets; zie je een verbetering, zet die
  als suggestie in `analyse/vragen.md` §D en laat het origineel intact.
- **Verzin geen brieftekst.** Ontbreekt er een variant (bijvoorbeeld een
  meervoudsvorm die niet in de bronbrieven staat), zet er dan een vraag over in
  `analyse/vragen.md` in plaats van zelf een zin te schrijven.
- **Aantekeningen horen in het veld `notitie`,** nooit in `tekst` — wat in `tekst`
  staat belandt in de brief naar de klant. Er staat een test op.
- **De juridisch bindende alinea's staan vastgelegd** in
  `tests/test_juridische_teksten.py`: garantie, algemene voorwaarden,
  aansprakelijkheid, btw, geldigheidsduur, betalingstermijnen. Wijzig je zo'n
  tekst bewust, neem de nieuwe dan in die test over en noteer in `vragen.md` wie
  erover besloot. Faalt die test onbedoeld, draai de wijziging dan terug.
- Elk blok heeft een `bron`-veld met het bestand waar de tekst vandaan komt.
  Houd dat bij, zodat elke zin terug te voeren is op een echte brief.

## Vaste waarden, geen variabelen

Deze staan in alle bronbrieven identiek en horen niet in het formulier:
levertijd (`in onderling overleg`), levering (`franco werk`), geldigheidsduur
(`30 dagen`), garantietermijn airconditioning (`12 maanden`), betalingstermijn
zakelijk (`30 dagen`). De btw-weergave is afgeleid van `klanttype` — particulier
inclusief, zakelijk exclusief — en wordt dus niet gevraagd.

Bedragen worden geschreven als `€ 7.595,-`, niet `€ 7.595,00`; dat is de notatie
uit de brieven zelf. Zie `analyse/vragen.md` vraag 13, die nog openstaat.

## Openstaande vragen

`analyse/vragen.md` is de lopende lijst met inconsistenties in de bronbrieven en
beslissingen die de opdrachtgever nog moet nemen. Werk die bij in plaats van een
aanname te doen; verwijs in code en YAML naar het vraagnummer.

**Technische specificaties.** Naast `Zie bijlage` kan de inhoud in de brief
zelf: uit `technische_specificaties_tekst` (ingetypt) of uit
`technische_specificaties_bestand` (Word, PDF of platte tekst, uitgelezen door
`brieventool/bijlage.py`). Dat blok heeft `stijl: letterlijk`: de regels worden
precies overgenomen, inclusief de lege regels ertussen, en er komen geen
witregels bij. Een productdatabase per merk en type blijft een latere optie.

## Persoonsgegevens

`bronbrieven/uitgewerkt/` staat in `.gitignore` omdat die brieven namen, adressen
en e-mailadressen van echte klanten bevatten. De analyse verwijst ernaar als
`uitgewerkt-1` tot en met `uitgewerkt-7`. Neem geen klantgegevens over in
bestanden die wel in git komen.

## Git

Ontwikkel op de branch `claude/new-session-99s0l8`. Commitberichten in het
Nederlands, in de gebiedende wijs noch de verleden tijd maar beschrijvend, met
uitleg van het waarom bij niet voor de hand liggende keuzes.
