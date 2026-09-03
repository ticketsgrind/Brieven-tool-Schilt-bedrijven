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
# De app starten (opent een browser op 127.0.0.1)
python3 -m brieventool.server
python3 -m brieventool.server --poort 8000 --geen-browser

# Het Word-sjabloon (opnieuw) maken uit een bronbrief
python3 tools/maak_sjabloon.py

# Een brief samenstellen en de tekst tonen
python3 -m brieventool voorbeelden/particulier-wand-enkelvoud.yaml
python3 -m brieventool <offerte>.yaml --blokken          # toon gebruikte blok-id's
python3 -m brieventool <offerte>.yaml --docx uit/brief.docx
python3 -m brieventool <offerte>.yaml --docx uit/brief.docx --toch   # ook met gaten erin

# Tests
python3 -m unittest discover -s tests -t .
python3 -m unittest tests.test_samenstellen -v
python3 -m unittest tests.test_samenstellen.TestZakelijkeBrief.test_meervoud

# De brief die het scherm zonder Python maakt naast die van de motor leggen
node tools/spiegel/draai_motor.js ontwerp/prototype.html <offerte>.json > brief.json
node tools/spiegel/draai_motor.js ontwerp/prototype.html <offerte>.json docx > brief.docx

# Meten hoeveel van de bestaande brieven de bibliotheek dekt
python3 tools/dekkingstoets.py

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

**De keten:** `analyse/teksten.yaml` (143 blokken) → `bibliotheek.py` laadt ze →
`samenstellen.py` kiest en vult → `sjabloon.py` schrijft het Word-bestand.
`controle.py` staat ertussen: het weigert een Word-bestand zolang er nog
gegevens ontbreken.

**Een halve brief wordt geen Word-bestand.** Een leeg antwoord werd stilzwijgend
als niets ingevuld, en dan staat er `bedraagt netto.` of `Ons project no.` in een
brief aan een klant. `controle.py` noemt bij naam wat er nog mist; `server.py`
weigert `/docx`, de opdrachtregel weigert `--docx` (met `--toch` als noodrem) en
het scherm weigert de knop. De **voorvertoning blijft wel werken** — je moet
kunnen meelezen terwijl je invult. Elke controle daar staat omdat het gat is
nagemeten in de samengestelde brief; voeg er geen toe op gevoel.

**Het enkelvoud/meervoud hangt aan `_aantallen`.** Die functie zegt per
installatieregel hoeveel binnen- en buitendelen er worden aangeboden: een
splitsysteem is één binnendeel op één buitendeel (maal `aantal_systemen`), een
multi-split of VRF heeft `aantal_binnendelen` en `aantal_buitendelen`. De optelsom
bepaalt `aantal_binnenunits` en `aantal_buitenunits`, en dus of de brief "De
binnenunit is" of "De binnenunits zijn" schrijft. Een blijven staan
`aantal_binnendelen` van een eerder gekozen multi-split telt bij een splitsysteem
níet mee — dat gaf meervoud bij één unit. De spiegel in `prototype.html` heeft
dezelfde functie; `tests/test_samenstellen.py` legt de zes gevallen vast. Het
scherm toont de uitkomst onder de installaties, zodat te zien is waar het
enkelvoud/meervoud vandaan komt.

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

**De volgorde van de secties is die van `teksten.yaml`.** Een sectie staat waar
haar eerste blok staat. Daarom heeft de aansprakelijkheid een eigen sectie onder
de garantie: in alle sjablonen staat `Garantietermijn:` boven
`Aansprakelijkheid:`, en met beide blokken in de sectie `voorwaarden` kwam de
aansprakelijkheid mee naar boven. `tests/test_werkzaamheden.py` legt de hele
witruimte van de brief naast `bronbrieven/wand enkelvoud.dotx`, regel voor regel.

**Keuzegroepen.** Blokken met dezelfde `keuzegroep` sluiten elkaar uit; de eerste
die past wint. De volgorde in `teksten.yaml` is dus de voorrangsvolgorde, met de
meest algemene variant onderaan als terugval. Let op: keuzegroepen werken
**alleen buiten een lus** — in een herhalende sectie (`specificatie`, `prijs`)
moeten de voorwaarden elkaar zelf uitsluiten, zoals bij de kopregel boven een
installatie (`regel.eigen_kop` tegenover `regel.ruimte and not regel.eigen_kop`).

**Facturering en betaling zijn twee losse keuzes.** Elk blok hangt aan zijn eigen
antwoord (`facturering == '...'`, `betaling == '...'`) en zit in een keuzegroep,
zodat er altijd precies één factureringsafspraak en één betalingsafspraak in de
brief staat. Dat ging eerder mis: de particuliere variant hing aan `klanttype` en
kwam er dus bovenop als je ook een termijn koos, waarna `Facturering:` twee keer
in de brief stond.

**De werkzaamhedenlijsten horen bij de systeemsoort.** Split, multi-split,
cassette en kanaal delen één lijst; VRF heeft een eigen lijst met andere regels
én een andere volgorde. `WERK_STANDAARD` en `WERK_VRF` in `prototype.html` zetten
de vinkjes; de volgorde in de brief is die van `teksten.yaml`, en die is zo
gekozen dat beide lijsten in de volgorde van hun bronbrief uitkomen.
`tests/test_werkzaamheden.py` leest die opsommingen uit `bronbrieven/*.dotx` en
vergelijkt ze regel voor regel — verander je de volgorde, dan valt die toets om.

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
  Drie uitzonderingen: opsommingsregels staan tegen elkaar aan (alleen na de
  laatste een witregel), een met tabs uitgelijnde vervolgregel staat direct
  onder de regel waar hij bij hoort, en een blok met `stijl: letterlijk` bepaalt
  zijn eigen witruimte — de witregels staan dan in de tekst zelf.
  `_zet_witregels` in `samenstellen.py` bepaalt dat; het sjabloon volgt alleen
  `a.witregel_erna`.
- *De werkzaamhedenlijst is één blok:* kop, opsomming, volgende kop en zijn
  opsomming staan tegen elkaar aan, met pas na de laatste regel een witregel.
  `AANEENGESLOTEN_SECTIES` in `samenstellen.py` regelt dat. Andersom kan ook: een
  blok met `witregel_tussen: true` — de aansprakelijkheid — krijgt juist wél een
  lege regel tussen zijn opsommingsregels. Allebei nagemeten in de sjablonen en
  de verstuurde brieven.
- *De briefkop is de uitzondering:* daar zit de witruimte tussen de secties en
  staat ze vast in het sjabloon — vier lege regels boven het adres, zes eronder,
  één na de betreft-regel, één na `Meerkerk <datum>` en drie na `Ref.`. Het
  adresblok en de regels met project no. en Ref. staan dus aaneengesloten.
  `_zet_witregels` geeft die secties daarom `witregel_erna=False`, zodat de
  voorvertoning hetzelfde tekent als Word in plaats van overal een witregel te
  zetten. `tests/test_sjabloon.py` telt die lege regels na.
- *De ondertekening.* Bedrijfsnaam en `MEERKERK` staan tegen elkaar aan, en de
  naam en de functie van de ondertekenaar ook; daartussen twee lege regels als
  ruimte voor de handtekening. Nagemeten in alle veertien sjablonen met een
  ondertekening en in de verstuurde brieven. Het blok heeft daarom
  `stijl: letterlijk`; `tests/test_samenstellen.py` legt de vorm vast.
- *Opsommingstekens.* De stijl `Lijstalinea` zorgt alleen voor inspringing. Het
  streepje komt uit een `numPr`-verwijzing naar een lijstdefinitie in
  `numbering.xml`. Zonder die verwijzing staat de regel ingesprongen maar zonder
  teken ervoor.

- *Cursief.* Een blok met `cursief: true` wordt schuingedrukt: de
  uitgangspunten voor de prijsvorming (cursief in alle 13 sjablonen), de
  garantietekst en de functie onder de ondertekening (cursief in alle verstuurde
  brieven). De vlag geldt voor het hele blok **behalve de kopregel** — in de
  bronbrieven is geen enkele kop cursief, die zijn onderstreept of vet. Daarom
  staat `Garantietermijn:` recht en de tekst eronder schuin, zonder dat het blok
  gesplitst hoeft te worden. De functie is wél een eigen blok, want daar is de
  kopregelregel geen hulp.
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

**`ontwerp/prototype.html` is één bestand met twee standen.** Draait er een
motor achter, dan stuurt het scherm de antwoorden naar `server.py` en toont het
wat `samenstellen.py` teruggeeft; dat is de werkende tool. Zonder motor rekent
het de brief zelf uit met een JavaScript-spiegel van de motor — dat is de
ontwerpversie.

**Het scherm herkent de motor aan `/app`, niet aan het protocol.** Bij het
starten vraagt het één keer om `app`; komt daar `{"app": true}` uit, dan is er
Python. Kijken naar `location.protocol` gaat mis zodra het bestand los over
`https` wordt bediend (als artefact bijvoorbeeld): het scherm denkt dan dat er
een motor is, krijgt HTML terug op zijn vraag om JSON en blijft leeg. Alle
adressen in het scherm zijn om dezelfde reden betrekkelijk (`fetch("brief")`,
niet `fetch("/brief")`), en valt de verbinding halverwege weg, dan zet
`verversViaApp` de stand terug op zelf rekenen. Er staan twee tests op in
`tests/test_server.py`.

**Het scherm maakt zelf een Word-bestand als er geen motor is.** Draait de app,
dan levert Python het bestand — die is de maat. Zonder app bouwt het scherm het
uit het sjabloon dat `ververs_prototype.py` als base64 in de pagina zet:
`maakDocument` vervangt de body van `word/document.xml` op precies dezelfde
manier als `tools/maak_sjabloon.py` hem opbouwt, en `schrijfZip` pakt het weer
in — de onderdelen die niet veranderen gaan ingepakt en al weer mee, alleen het
nieuwe document.xml gaat er onverpakt in, zodat er in de browser niets
gecomprimeerd hoeft te worden. `tests/test_spiegel.py` draait de spiegel in node
en legt beide brieven naast elkaar: dezelfde alinea's, dezelfde blokken en een
Word-bestand dat op de regeleinden in de XML-kop na byte voor byte gelijk is.
Wijk je in de een af, dan valt die toets om.

**Bewaren gebeurt op twee manieren.** De browser onthoudt de antwoorden in
`localStorage` (sleutel `brieventool.concept`), zodat een dichtgeklapt tabblad
geen werk kost; dat is een vangnet, geen archief, en het staat alleen op die ene
computer. Daarnaast slaat **Opslaan** de antwoorden op als `.json` met een merk
erin (`brieventool-offerte`), en leest **Openen** zo'n bestand terug. `A` is een
`const` die overal is doorgegeven, dus terugzetten gebeurt met `vulAntwoorden`:
leegmaken en vullen, niet vervangen. **Nieuw** vraagt eerst na door zelf even in
`Alles wissen?` te veranderen — een `confirm()` mag niet.

**De bestandsnaam is aan te passen voor het downloaden.** De knop opent eerst
een veldje met de voorgestelde naam (`achternaam-plaats-sa-nummer`, dezelfde als
`_bestandsnaam` in `server.py`); enter maakt het bestand, escape sluit het.
Wat de gebruiker typt blijft in `A.bestandsnaam` staan, met een knopje om het
voorstel terug te halen. In de app haalt het scherm daarna wel het bestand van
Python, maar niet meer de naam uit `Content-Disposition`.

**Geen `alert()`, `confirm()` of `prompt()` in het scherm.** Een ingelijste
pagina — het scherm als artefact — mag geen venster openen; de aanroep doet dan
zichtbaar niets. Meldingen gaan via `toonFout` en `toonMelding`, en invoer via
een veld in de pagina zelf. Om dezelfde reden komt het bestand daar niet uit een
downloadkoppeling maar uit `claude.use("downloads")`; een gewone koppeling is er
inert. Buiten die omgeving blijft de koppeling de weg.

Alleen die tweede stand kan uit de pas lopen met de motor. Wijzig je de
selectielogica in Python, werk dan ook de spiegel bij. Draai
`ontwerp/ververs_prototype.py` na elke wijziging in `teksten.yaml` én na elke
`tools/maak_sjabloon.py`, want het sjabloon zit ook in die pagina; controleer
daarna met `node --check` dat het script nog geldig is, want een fout in de
ingebakken gegevens breekt de hele pagina.

**De huisstijl komt van Schilt, niet uit mijn duim.** Het blauw `#3A5EC4` is dat
van schiltbedrijven.nl (koppen, knoppen), het leisteengrijs `#414B4D` is dat van
het woordmerk, en `#D9121E` is de rode zwiep eronder. De grijzen hebben een
blauwzweem zodat ze bij dat blauw horen. Knoppen zijn pillen, net als op de
site. Het amber van `--signal` staat daar los van: dat betekent "hier ontbreekt
nog iets" en is met opzet geen huisstijlkleur.

Het beeldmerk in de kop is **het echte bestand uit het briefpapier**
(`word/media/image1.jpeg`, de strook *professionals in air*), door
`ververs_prototype.py` als CSS-regel tussen `/*<logo>*/` gezet — vandaar dat het
een achtergrond is en geen `<img>`: in een HTML-attribuut zijn `/* */` gewone
tekens en geen commentaar. Zo toont het scherm hetzelfde merk als de brief; een
test vergelijkt beide bytes. Op een donkere achtergrond krijgt het merk een wit
plaatje (`--logoveld`), want de strook heeft zelf een witte rand. Het geschreven
woordmerk *Schilt* zit niet in het briefpapier en dus ook niet in de app; lever
dat bestand aan als het erin moet.

**De voorvertoning gebruikt het echte briefpapier.** `briefpapier.py` leest uit
`sjablonen/brief.docx` het paginaformaat, de marges, de gegevens rechtsboven, de
voettekst en de afbeeldingen; de app bedient die via `/briefpapier` en
`/beeld/<naam>`. Het vel op het scherm heeft daardoor A4-verhoudingen met de
echte marges, zodat de regels ongeveer op dezelfde plek afbreken als in Word.
Verzin hier nooit een kop of voet: dan wekt het scherm de indruk dat de brief er
zo uitziet terwijl het Word-bestand iets anders doet. Een EMF-afbeelding kan een
browser niet tonen; die komt als `onbekende_beelden` terug in plaats van
stilzwijgend te verdwijnen.

**De voorvertoning tekent de witregels van de motor.** Een lege regel op het vel
is precies één regelhoogte (`.alinea.witregel`), net als een lege alinea in Word;
de vaste lege regels van de briefkop tekent `regelgat()`. Het scherm zet dus geen
eigen marges meer tussen alinea's — anders staat er op het scherm ruimte waar
Word er geen zet, en dat is precies waar het eerder misging.

**De motor levert `tekst` en `nadruk` apart** waar een alinea uit twee
tekstdelen bestaat: bij `stijl: prijs` het bedrag, bij `stijl: label` de inhoud
achter de tab. In Word worden dat twee runs met eigen opmaak; het scherm plakt
ze weer aan elkaar.

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
`brieventool/bijlage.py`). Dat blok heeft `stijl: letterlijk`, net als de
ondertekening: de regels worden precies overgenomen, inclusief de lege regels
ertussen, en er komen geen witregels bij. Een productdatabase per merk en type blijft een latere optie.

## Persoonsgegevens

`bronbrieven/uitgewerkt/` staat in `.gitignore` omdat die brieven namen, adressen
en e-mailadressen van echte klanten bevatten. De analyse verwijst ernaar als
`uitgewerkt-1` tot en met `uitgewerkt-7`. Neem geen klantgegevens over in
bestanden die wel in git komen.

## Git

Ontwikkel op de branch `claude/new-session-99s0l8`. Commitberichten in het
Nederlands, in de gebiedende wijs noch de verleden tijd maar beschrijvend, met
uitleg van het waarom bij niet voor de hand liggende keuzes.
