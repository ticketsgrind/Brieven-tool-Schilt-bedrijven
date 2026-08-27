# Vragen en inconsistenties

Gebaseerd op 16 sjablonen uit `bronbrieven/` en 7 uitgewerkte brieven uit
`bronbrieven/uitgewerkt/`.

De eerste twee tabellen zijn wat ik nodig heb voordat fase 2 kan beginnen. Daarna
volgen de inconsistenties en de suggesties.

---

## A. Vragen die je zelf al had gesteld — beantwoord

### 1. Opbouw van `projectnummer` en `referentie` — patroon gevonden

**`Ons project no.`** — zeven waarnemingen, allemaal `<letter>.<7 cijfers>.6.01`:

| Nummer | Brief | Soort |
|---|---|---|
| `Q.1007999.6.01` | uitgewerkt-1 | offerte |
| `Q.1018394.6.01` | uitgewerkt-3 | offerte |
| `Q.1062195.6.01` | uitgewerkt-6 | offerte |
| `Q.1069413.6.01` | uitgewerkt-7 | offerte |
| `Q.1073133.6.01` | uitgewerkt-5 | offerte |
| `Q.1077218.6.01` | uitgewerkt-4 | offerte |
| `P.0990480.6.01` | uitgewerkt-2 | **opdrachtbevestiging** |

De `.6.01` is constant. Het middendeel loopt netjes op met de datum en komt
vrijwel zeker uit een ander systeem.

> **Vraag 1a.** Klopt het dat `Q.` staat voor offerte en `P.` voor project, en dat
> de letter dus meebeweegt met het documentsoort?
>
> **Vraag 1b.** Waar komt het zevencijferige nummer vandaan — Navision, AFAS,
> iets anders? Als de tool dat systeem kan bevragen, kan het hele nummer
> automatisch. Zo niet, dan blijft het een handmatig veld.
>
> **Vraag 1c.** Is `.6.` inderdaad de code van de business unit Airconditioning,
> en is `.01` een volgnummer dat oploopt bij een herziene offerte?

**`Ref.`** — zeven waarnemingen: `RH/RdJ/SA35709`, `NV/RdJ/SA35738`,
`NV/RdJ/SA35859`, `NV/VL/SA35862`, `NV/RdJ/SA35887`, `NV/SA35900`,
`NV/LH/SA35923`.

Patroon: `<initialen ondertekenaar>/[<initialen tweede persoon>/]SA<5 cijfers>`.
Het eerste deel volgt de ondertekenaar (NV = Nick Vervoorn, RH = Robert Hartman).
Het `SA`-nummer loopt op met de datum: 35709 op 2 maart, 35923 op 26 augustus.

> **Vraag 1d.** Wie is de tweede persoon in het middendeel — `RdJ`, `VL`, `LH`?
> De opsteller van de brief, de calculator, of de binnendienstmedewerker?
> `LH` zijn jouw initialen, dus ik vermoed de opsteller.
>
> **Vraag 1e.** In `NV/SA35900` ontbreekt het middendeel. Is dat omdat de
> ondertekenaar de brief zelf heeft opgesteld, of is het gewoon vergeten?
>
> **Vraag 1f.** Waar komt het `SA`-nummer vandaan? Als het een doorlopende teller
> binnen de business unit is, kan de tool het volgende nummer voorstellen.

### 2. Wordt `totaalprijs` inclusief of exclusief btw getoond?

**Je vermoeden klopt, en het volgt `klanttype`, niet het soort pand.** Bevestigd
in alle zeven uitgewerkte brieven:

| Brief | Klant | Betreft | Btw-regel |
|---|---|---|---|
| uitgewerkt-4 | particulier | uw woning | **inclusief** 21% btw |
| uitgewerkt-3 | particulier | uw twee slaapkamers en de keuken | **inclusief** 21% btw |
| uitgewerkt-7 | particulier | uw woning | **inclusief** 21% btw |
| uitgewerkt-6 | zakelijk | **uw woning** <adres> | **exclusief** 21% btw |
| uitgewerkt-5 | zakelijk | uw kantoren | exclusief 21% btw |
| uitgewerkt-2 | zakelijk | uw vestiging | exclusief btw |
| uitgewerkt-1 | zakelijk | uw project | exclusief btw |

De regel van uitgewerkt-6 is het bewijs dat het klanttype beslist en niet het woord
"woning": het gaat om een woning, maar de klant is een vastgoedbedrijf en dan is
de prijs exclusief.

Er komt in geen van de 23 bestanden een verlaagd btw-tarief voor. `btw_tarief`
kan dus voorlopig een constante van 21% zijn.

> **Vraag 2.** Komt het verlaagde tarief voor arbeid bij woningen ouder dan twee
> jaar in jullie werk nooit voor? Zo ja, dan moet `btw_tarief` alsnog een keuze
> worden.

### 3. Wat staat er in de betreft-regel?

Vijf vormen aangetroffen. Belangrijk: **er staan nergens aanhalingstekens**, in
geen enkel van de 23 bestanden. De aanvulling ging daarvan uit, maar de brieven
doen het niet.

- `Airconditioning t.b.v. uw woning` — particulier, zonder verdere aanduiding
- `Airconditioning t.b.v. uw vestiging te <plaats>` — zakelijk, plaatsnaam
- `Airconditioning t.b.v. uw project <projectnaam>` — zakelijk, projectnaam
- `Airconditioning t.b.v. uw twee slaapkamers en de keuken` — particulier, ruimten
- `Vervangen airconditioning t.b.v. uw woning <adres> <plaats>` — adres

> **Vraag 3.** Wil je deze vijf vormen als keuze in het formulier, of liever één
> vrij tekstveld met de vormen als voorbeeld? Ik neig naar het laatste: er zit te
> veel variatie in om het dicht te timmeren.

### 4. Welke gegevens komen per regel in de specificatie terug?

Anders dan verwacht: het is **geen tabel met kolommen** maar een lopende zin per
installatie. Zie `variabelen.md` §3 voor de negen velden. Het vermogen in kW
staat **niet** in de specificatieregel — dat staat in het technische
specificatieblok verderop, of in een bijlage.

### 5. Verschilt de opmaak tussen één en meerdere installaties?

Nee, niet zoals verwacht. Ook bij meerdere installaties blijft het lopende tekst;
er wordt geen tabel of bullet-opsomming gebruikt. Wat er wél bij komt is een
kopregel per installatie (`T.b.v. de slaapkamer:`) en bij meerdere prijsvarianten
een letter (`A.` / `B.`).

Wat wél meebeweegt met het aantal is de taal in de omliggende alinea's — precies
zoals je voorspelde. `een airconditioninginstallatie` ↔ `airconditioninginstallaties`,
`De binnenunit is` ↔ `De binnenunits zijn`, `De buitenunit wordt geplaatst` ↔
`De buitenunits worden geplaatst`. Die zijn in `teksten.yaml` als enkelvoud- en
meervoudvariant van hetzelfde blok opgenomen.

### 6. Verschilt de afsluiting per ondertekenaar?

Alleen de functieomschrijving verschilt. De sjablonen bevatten alle drie de namen
onder elkaar zodat de opsteller er twee wegknipt:

- John van de Weetering — Technisch Commercieel Manager
- Nick Vervoorn — Technisch Commercieel Adviseur
- Ricardo Rozendaal — Project Engineer

In de uitgewerkte brieven kwam een vierde naam voor: **Robert Hartman, Business
Unit General Manager** (uitgewerkt-1, Ref. `RH/…`).

> **Vraag 4.** Robert Hartman stond niet in je lijst van drie. Moet hij als
> ondertekenaar in de tool, of tekent hij alleen bij grote projecten?

Er staan geen telefoonnummers of e-mailadressen bij de ondertekening — die staan
alleen als algemene bedrijfsgegevens in de briefkop. `config/ondertekenaars.yaml`
heeft daarom lege velden voor telefoon, mobiel en e-mail.

> **Vraag 5.** Wil je per ondertekenaar een direct telefoonnummer en e-mailadres
> onder de ondertekening zetten? Dat staat er nu niet, maar het veld is
> voorbereid. Zo ja, dan heb ik die gegevens nodig.

### 7. Zit er een handtekeningafbeelding in de brieven?

Elk bestand bevat drie afbeeldingen, en dat zijn in alle 16 sjablonen dezelfde
drie: een `.jpeg`, een `.png` en een `.emf`. Dat is het briefpapier — logo,
beeldmerk en de vectorafbeelding in de header. Er is **geen** handtekening te
vinden: geen enkel sjabloon heeft een vierde afbeelding op de plek van de
ondertekening, en de uitgewerkte brieven ook niet (de extra afbeeldingen daar
zijn productfoto's in het specificatieblok).

> **Vraag 6.** Klopt het dat de brieven ongetekend de deur uit gaan? Zo nee, dan
> lever je de handtekeningen apart aan en zet ik ze per persoon in
> `config/ondertekenaars.yaml`.

---

## B. Inconsistenties tussen de brieven

Deze moet je intern uitzoeken. Ik heb overal het origineel laten staan.

### Inconsistentie 1 — meerprijs condenswaterpomp: € 220 of € 260?

- **€ 220,- per stuk** in 9 zakelijke sjablonen (VRF, cassette enkelvoud, cassette
  meervoud, kanaal enkelvoud, kanaal meervoud, multi split, wand en cassette, wand
  enkelvoud, wand meervoud) — én in een zakelijke uitgewerkte brief.
- **€ 260,- per stuk** in de 3 particuliere sjablonen (multi split particulier,
  wand enkelvoud particulier, wand meervoud particulier).

**Beantwoord — dit is geen fout maar een bewuste afronding.** € 220 is het
tarief exclusief btw. Inclusief zou dat € 266,20 zijn, en dat staat niet netjes
in een brief aan een particulier; daarom is het naar beneden afgerond op
€ 260 inclusief btw. Beide bedragen blijven dus staan, elk aan hun eigen kant
van de btw-grens.

Zo staat het ook in de tool: `meerprijs_condenspomp_zakelijk` geeft € 220,- en
`meerprijs_condenspomp_particulier` € 260,-, gekozen op `klanttype`. Er staat
een test op in `tests/test_juridische_teksten.py`, dus een van de twee per
ongeluk aanpassen valt op.

### Inconsistentie 2 — btw-regel: mét of zonder percentage?

Vier schrijfwijzen voor twee betekenissen:

| Tekst | Aantal | Bestanden |
|---|---|---|
| `De genoemde prijzen zijn exclusief btw.` | 9 | VRF, cassette ×2, kanaal ×2, koelmachine, mech. ventilatie, multi split, warmtepomp |
| `De genoemde prijzen zijn exclusief 21% btw.` | 3 | wand en cassette, wand enkelvoud, wand meervoud |
| `De genoemde prijzen zijn inclusief btw.` | 1 | multi split particulier |
| `De genoemde prijzen zijn inclusief 21% btw.` | 2 | wand enkelvoud particulier, wand meervoud particulier |

> **Vraag 8.** Welke vorm is de juiste? Ik zou het percentage altijd noemen — bij
> particulieren is "inclusief 21% btw" duidelijker dan "inclusief btw", en het
> voorkomt discussie als het tarief ooit verandert. In `teksten.yaml` staat nu de
> vorm mét percentage; zeg het als je het anders wilt.

### Inconsistentie 3 — bedrijfsnaam in de aansprakelijkheidsclausule

- `Business Unit Schilt Airconditioning` in 13 sjablonen.
- `Schilt Airconditioning B.V.` in **cassette meervoud.dotx**.

> **Vraag 9.** Welke rechtspersoon is het? Dit staat in een
> aansprakelijkheidsuitsluiting, dus het maakt juridisch uit welke naam er staat.
> De briefkop noemt `Schilt Bedrijven B.V.`, wat weer een derde naam is.

### Inconsistentie 4 — garantietermijn koelmachine

De standaardtekst in 14 sjablonen is 12 maanden na inbedrijfstelling, zonder
bovengrens. `koelmachine.dotx` heeft een andere tekst:

> Gedurende 12 maanden na inbedrijfstelling op materiaal en arbeidsloon met een
> maximum van 18 maanden na aflevering (de kortste termijn is doorslaggevend).

Plus een extra regel over 24 maanden op de compressor en MCHE-batterijen.

> **Vraag 10.** Is die 18-maandengrens bewust alleen voor koelmachines, of hoort
> hij overal te staan? Bij de standaardtekst kan een klant in theorie jaren na
> aflevering nog garantie claimen als de inbedrijfstelling is uitgesteld.

### Inconsistentie 5 — vijf schrijfwijzen van dezelfde aanhef

`Geachte heer/mevrouw,` (7×), `Geachte heer/mevrouw` (2×), `Geachte heer/mevrouw ,`
(1×, spatie voor de komma), `Geachte heer ,` (3×), `Geachte heer,mevrouw,` (1×,
komma in plaats van schuine streep), `Geachte heer` (1×, zonder komma).

Dit is duidelijk slordigheid, geen bedoeling — in de uitgewerkte brieven staat
altijd de nette ingevulde vorm. De tool lost dit vanzelf op.

### Inconsistentie 6 — particuliere sjablonen missen de kredietwaardigheidsclausule

De alinea over het toetsen van de kredietwaardigheid staat in 13 sjablonen maar
niet in de drie particuliere. Dat is waarschijnlijk bewust — je toetst geen
consument bij een kredietadviseur — maar het staat nergens vastgelegd.

> **Vraag 11.** Bevestig je dat deze clausule bewust alleen zakelijk is? Idem voor
> de omgekeerde situatie: het ontbindingsrecht bij overschrijding van de
> leverdatum met 6 maanden staat alléén in twee particuliere sjablomen (wand
> enkelvoud/meervoud particulier), en niet in multi split particulier. Dat lijkt
> me een omissie in dat derde sjabloon, want het is een consumentenbepaling.

### Inconsistentie 7 — kapitalisatie van de plaatsnaam

In twee van de zeven uitgewerkte brieven staat de plaatsnaam van de klant in
kapitalen, in de overige vijf normaal. `MEERKERK` in de ondertekening staat
altijd in kapitalen.

> **Vraag 12.** Kapitalen of niet? De tool moet één vorm kiezen.

### Inconsistentie 8 — notatie van bedragen

Aangetroffen: `€ 7.595,-`, `€ 28.250` (zonder streepje), `€3.900,-` (zonder
spatie), `€ 1.265.000,-`, `€ 220,-`.

> **Vraag 13.** De aanvulling vraagt om `€ 4.995,00`. Die vorm komt in geen enkele
> brief voor — jullie schrijven consequent `,-` in plaats van `,00`. Wil je dat de
> tool overgaat op `€ 4.995,00`, of houden we jullie eigen `€ 4.995,-` aan? Ik
> neig naar het laatste, want dat is wat klanten van jullie gewend zijn.

### De privacylink is niet meer klikbaar

In de bronbrief is `www.schiltbedrijven.nl/privacyverklaring` in de laatste
alinea een echte hyperlink. De tekst van die alinea staat nu in `teksten.yaml`
als gewone tekst, dus in de gemaakte brief is het geen link meer. In de voettekst
staat hij nog wel, want die is onaangeroerd.

> **Vraag 23.** Moet die link in de lopende tekst klikbaar blijven? Zo ja, dan
> bouw ik hem terug in; het is een kleine toevoeging aan het sjabloon.

### Inconsistentie 11 — koppen zijn de ene keer vet en de andere keer niet

Bij het maken van het Word-sjabloon bleek dat de bronbrief zelf niet consequent
is in welke sectiekoppen vet staan:

| Regel | In `wand enkelvoud.dotx` |
|---|---|
| `Betreft ...` | vet |
| `Aanbieding` | vet |
| `Totaalprijs:` | niet vet |
| `Levering:` | niet vet |
| `Garantietermijn:` | niet vet |
| `De totaalprijs compleet geleverd en gemonteerd bedraagt € … netto.` | **vet** |

Het sjabloon zet nu alle sectiekoppen vet, omdat dat het meest verzorgd oogt en
de brief leesbaarder maakt.

**Het bedrag is inmiddels wel vet**, op verzoek van de opdrachtgever en in
overeenstemming met de bronbrieven. Nagemeten in acht brieven, sjablonen en
verstuurde: vet is niet de hele zin maar het deel vanaf het eurobedrag tot en
met `netto.`, bij de totaalprijs, de raamprijs en de meerprijzen voor coating en
RAL-kleur. De condenswaterpompregel eindigt op `per stuk` en staat nergens vet.

**Beantwoord.** De opdrachtgever koos voor onderstrepen, wat overeenkomt met de
bronbrieven. De regel is nu:

| Vorm | Regels |
|---|---|
| onderstreept | de kopjes met dubbele punt: `Totaalprijs:`, `Levering:`, `Facturering en betaling:`, `Kredietwaardigheid:`, `Algemene voorwaarden:`, `Garantietermijn:`, `Aansprakelijkheid:`, `De installatie is aangeboden inclusief:`, `Niet tot onze werkzaamheden behoren:`, `Wij specificeren onze aanbieding als volgt:` |
| vet | `Aanbieding`, `Opdracht`, `Tot slot`, `TECHNISCHE SPECIFICATIES`, `Zie bijlage`, de ruimtekopjes `T.b.v. …:` |
| gewoon | `Voor de prijsvorming zijn wij er van uitgegaan dat:` — een aanloopzin, geen kopje |

Ook nagemeten: in de betreft-regel staat het woord `Betreft` op 7 punten en niet
vet, terwijl de inhoud erachter op 9 punten en vet staat. Bij `Meerkerk` staat
het label eveneens op 7 punten en de datum gewoon. Zonder dat verschil in
tekengrootte landt de tab anders en loopt de regel scheef.

### Inconsistentie 10 — ontbrekende meervoudsvormen

Bij het bouwen van de motor bleek dat een paar blokken alleen in het enkelvoud
bestaan, terwijl ze ook bij meerdere units gebruikt worden. De brief zegt dan
"de buitenunit" terwijl er twee staan:

| Blok | Tekst nu | Ontbreekt |
|---|---|---|
| `buitenunit_winterregeling` | "De buitenunit **is** voorzien van een winterregeling" | meervoudsvorm |
| `systeem_opbouw_meervoud` | "... en **één buitenunit** die d.m.v. koelmiddelleidingen" | vorm voor meerdere buitenunits |

> **Vraag 21.** Mag ik hiervoor een meervoudsvariant schrijven ("De buitenunits
> zijn voorzien van een winterregeling"), of wil je de formulering zelf
> aanleveren? Het is nieuwe tekst en die verzin ik liever niet zelf.

### Inconsistentie 9 — spel- en typefouten in de sjablonen

Onaangeroerd gelaten, maar de moeite van het corrigeren waard:

| Fout | Zou moeten zijn | Bestand |
|---|---|---|
| `rioleringaansluiting` | `rioleringsaansluiting` | kanaal enkelvoud, kanaal meervoud |
| `laaag geluidsniveau` | `laag geluidsniveau` | koelmachine |
| `scrolcompressoren` | `scrollcompressoren` | koelmachine |
| `(GBS) e.d..` | `(GBS) e.d.` | kanaal enkelvoud, kanaal meervoud |
| `dwz.` | `d.w.z.` | multi split particulier |
| `De binnenunit wordt voorzien ... welke door derden dienen te worden bedraad` | `dient te worden` | wand enkelvoud, multi split |
| `de condensor van de buitenunits` | `de condensors van de buitenunits` | cassette meervoud |
| `John van de Weetering` | `John van de Wetering`? | alle sjablonen |

> **Vraag 14.** De naam van John: de sjablonen schrijven consequent
> **Weetering** met dubbele e, jouw aanvulling schrijft **Wetering**. Welke is
> goed? Ik heb in `config/ondertekenaars.yaml` de sjabloonspelling aangehouden
> met een notitie erbij, omdat die in 15 bestanden staat — maar iemands eigen
> naam verkeerd spellen in elke offerte is niet best.

---

## B2. Bevindingen uit de werkzaamheidstest

Een werkelijk verstuurde offerte (uitgewerkt-3: particulier, twee installaties)
is met de tool nagebouwd en regel voor regel vergeleken. Van de 67 regels
brieftekst kwamen er 56 letterlijk overeen. De verschillen staan hieronder;
draai de toets zelf met:

    python3 tools/toets_tegen_echte_brief.py <offerte.yaml> <verstuurde-brief.docx>

Twee dingen zijn naar aanleiding hiervan meteen gerepareerd: zonder organisatie
begint het adres met `De heer …` in plaats van `T.a.v. de heer …`, het
e-mailadres van de klant kan onder het adres, en het tussenvoegsel krijgt in de
aanhef een hoofdletter (`De heer K. ten Broek` maar `Geachte heer Ten Broek,`).

### Gat 1 — de opstelling van de buitenunit is niet per installatie te kiezen

De echte brief heeft twee verschillende opstellingen naast elkaar:

> De buitenunit **voor de keuken** wordt geplaatst op steunen met
> trillingsdempers tegen de buitengevel.
> De buitenunit **voor de slaapkamer op de begane grond** wordt geplaatst op
> geluiddempende rubberen opstelbalken op de grond.

De tool kent één opstelling per brief en maakt er dus één regel van. Bij twee of
meer installaties op verschillende plekken klopt dat niet.

> **Vraag 24.** Moet `opstelling_buitenunit` een veld per installatieregel
> worden in plaats van per brief? Dat lijkt me nodig; het komt in meer dan één
> brief voor.

### Gat 2 — het aantal condensafvoeren

De echte brief zegt `condensafvoer d.m.v. natuurlijk verloop (3x)`; de tool laat
het aantal weg en schrijft `d.m.v. een natuurlijk verloop`.

> **Vraag 25.** Hoort dat aantal er standaard bij zodra er meer dan één
> binnenunit is, en zo ja: telt het de binnenunits of de afvoeren?

### Gat 3 — meervoud van "stopcontact"

De echte brief heeft `passen we de bestaande geaarde stopcontacten toe`, de
bibliotheek kent alleen het enkelvoud. Zelfde soort gat als vraag 21.

### Gat 4 — de aanleidingszin eindigt soms op "ruimte"

De tool schrijft `t.b.v. bovengenoemd project`, de echte brief
`t.b.v. bovengenoemde ruimte`.

> **Vraag 26.** Wanneer kiezen jullie welke? Bij een particulier de ruimte en
> bij een bedrijf het project, of hangt het van iets anders af?

### Tegenstrijdigheid — kredietwaardigheid bij een particulier

In `analyse/skelet.md` staat dat de kredietwaardigheidsclausule alleen zakelijk
is; dat volgde uit de sjablonen, waar hij in de drie particuliere ontbreekt.
Maar in deze verstuurde particuliere brief **staat hij wel**. Omgekeerd
ontbreekt in dezelfde brief het ontbindingsrecht bij late levering, dat de tool
er juist bij zet.

**Beantwoord: de standaardbrieven zijn leidend.** De sjablonen in
`bronbrieven/` bepalen wat er in een brief hoort, niet een losse verstuurde
brief. Daarmee blijft het zoals het nu is:

- de kredietwaardigheidsclausule alleen bij zakelijke klanten;
- het ontbindingsrecht bij overschrijding van de leverdatum alleen bij
  particulieren.

De verstuurde brief waarin het andersom stond is dus een afwijking van de
standaard geweest, geen aanwijzing dat de standaard verkeerd is. Bij een
volgende werkzaamheidstest komen die twee regels daarom als verschil terug; dat
is verwacht en geen fout.

### Maatwerk — geen gat, wel het bewijs dat de eigen alinea nodig is

Twee zinnen zijn door de opsteller aangepast aan deze klant:

> De **Z25/35CFEAW** binnenunits zijn speciaal ontworpen laag aan de muur …
> De **TZ35ZKEW** binnenunit is ontworpen voor montage hoog aan de wand …

De bibliotheek heeft de algemene formulering zonder typeaanduiding. Dat hoort
geen blok te worden; dit is precies waarvoor de knop "eigen alinea" in het
ontwerp zit.

---

## B3. Dekking van de bibliotheek

`python3 tools/dekkingstoets.py` legt elke alinea uit alle 20 brieven naast de
bibliotheek en kijkt of er een blok bestaat dat hem kan voortbrengen. Zonder
ingevuld offertebestand, dus het meet de bibliotheek zelf en niet een enkele
brief.

**Stand: 98% van 1786 alinea's.** De airconditioningbrieven zitten op 98 tot
100%; vier ervan volledig, waaronder twee werkelijk verstuurde. Wat overblijft
zit vrijwel helemaal in drie andere productsoorten:

| Brief | Dekking | Wat ontbreekt |
|---|---|---|
| KE-Fibertec luchtslangsysteem | 92% | productbeschrijvingen (Dire-Jet, KE-Hybrid, Cradle to Cradle) |
| koelmachine | 92% | technische beschrijving van de Carrier-koelmachine |
| mechanische ventilatie | 98% | de Stork dakventilator-regel |

> **Vraag 29.** Moeten koelmachines, mechanische ventilatie en luchtslangen ook
> uit deze tool komen, of blijven dat losse brieven? Als ze meemoeten is het
> werk overzichtelijk -- de teksten staan in de sjablonen en hoeven alleen
> overgenomen te worden -- maar het heeft geen zin als jullie die brieven
> nauwelijks sturen.

De rest van het verschil zijn varianten op de condensafvoer- en
leidinglengteregel die net anders geformuleerd zijn dan de opgenomen versie.

---

## B4. Wat de voorvertoning wel en niet laat zien

Het scherm bootst de eerste pagina na met het echte briefpapier uit het
sjabloon: A4 met de marges van 4 cm boven en 2,8 cm links, de logostrip
linksboven, de bedrijfsgegevens rechtsboven en de voorwaardentekst onderaan.

Twee dingen wijken bewust af, en die staan er niet in:

- **De verticale strip in de voettekst** is een EMF-afbeelding. Browsers kunnen
  dat formaat niet tonen. Hij zit wel gewoon in het Word-bestand.
- **Paginaovergangen.** De voorvertoning is één doorlopend vel; waar Word een
  pagina afbreekt is op het scherm niet te zien.

> **Vraag 30.** Is dat laatste hinderlijk? Ik kan een lijn tekenen op elke
> 297 mm, zodat je ziet of een brief op twee of drie pagina's uitkomt. Dat is
> een benadering -- Word rekent regelafbrekingen net iets anders -- dus het is
> de vraag of dat helpt of juist verwarring geeft.

---

## B5. De witruimte in de ondertekening

Nagemeten in alle veertien sjablonen met een ondertekening en in de vier
verstuurde brieven waar het blok in staat:

    Vertrouwende u hiermee van dienst te zijn geweest, tekenen wij ...
    (lege regel)
    Business Unit Schilt Airconditioning
    MEERKERK
    (lege regel)
    (lege regel)
    <naam>
    <functie>

Bedrijfsnaam en `MEERKERK` staan dus tegen elkaar aan, en naam en functie ook.
De tool zette daar tot nu toe overal een witregel tussen; dat is rechtgezet op
verzoek van Lars (27 augustus 2026) en vastgelegd in
`tests/test_samenstellen.py`.

Twee bestanden wijken af met één lege regel in plaats van twee tussen `MEERKERK`
en de naam: `bronbrieven/multi split.dotx` en een van de verstuurde brieven. De
overige dertien sjablonen en drie brieven hebben er twee, dus die zijn
aangehouden.

> **Vraag 31.** Klopt het dat twee lege regels de bedoeling zijn -- ruimte voor
> een handtekening? Zo niet, dan zet ik er één.

---

## C. Openstaande beslissingen voor fase 2

### Beslissing 1 — wat doen we met de technische specificaties?

Dit is de zwaarste. Drie vormen in de brieven:

1. **Volledig uitgeschreven** (uitgewerkt-2, -3 en -6): een blok van 20 tot
   40 regels per unit, met vermogen, aansluitspanning, SEER, SCOP, koudemiddel,
   luchthoeveelheid, geluidsniveau, afmetingen, gewicht, leidingdiameters. Per
   merk en type verschillend.
2. **Verwijzing** (`Zie bijlage`, `Technische specificaties zie bijlagen.`).
3. **Afwezig** (uitgewerkt-1).

Vorm 1 is te gestructureerd voor een vrij tekstveld en te variabel voor een vast
blok. Er zijn drie routes:

- **a.** Een productdatabase: per merk/type de specificaties vastleggen, de tool
  genereert het blok. Mooiste resultaat, maar iemand moet die database vullen en
  bijhouden — bij elke nieuwe Panasonic-serie opnieuw.
- **b.** Alleen `Zie bijlage` ondersteunen, en de bijlage blijft handwerk. Snelst
  te bouwen, maar je verliest wat je nu wel hebt.
- **c.** Een vrij tekstveld waar je het blok in plakt. Werkt altijd, maar lost het
  kopieerprobleem niet op.

**Route c is gekozen en gebouwd.** Naast `Zie bijlage` kun je de
specificaties nu in de brief zelf zetten, op twee manieren:

- **een datablad aanleveren** — Word, PDF of platte tekst. De tool leest de
  tekst eruit en zet die in de brief. In het scherm is dat een vak waar je een
  bestand naartoe sleept of op klikt.
- **de tekst plakken** in het veld eronder.

De regels worden letterlijk overgenomen, inclusief de tabs die de uitlijning
maken en de lege regels die de binnen- van de buitenunit scheiden. Is er
allebei ingevuld, dan wint de getypte tekst.

Route **a**, een productdatabase per merk en type, blijft open als latere
verbetering voor de types die je het vaakst offreert. Zolang die er niet is
levert de leverancier het datablad en plak of sleep je het erin.

> **Vraag 28.** Uit een gescande PDF komt geen tekst; daar is tekstherkenning
> voor nodig die de tool niet heeft. De tool meldt dat dan met de suggestie het
> als Word-bestand aan te leveren of de tekst te plakken. Komt dat vaak voor?

### Beslissing 2 — offerte of opdrachtbevestiging?

Uitgewerkt-2 is geen offerte maar een opdrachtbevestiging: `Opdracht` in plaats
van `Aanbieding`, `Wij specificeren de opdracht als volgt`, `Onder dankzegging
bevestigen wij hiermede uw schriftelijke opdrachtnr. ...`, projectnummer met `P.`
in plaats van `Q.`, en geen geldigheidsduur en slotzin.

Verder is de brief identiek. Dat is dus geen tweede sjabloon maar een schakelaar.

> **Vraag 16.** Wil je opdrachtbevestigingen ook uit deze tool laten rollen? Het
> is weinig extra werk nu, en veel werk als het er later bij moet.

### Beslissing 3 — vaste teksten die geen variabele zijn

Deze staan in alle brieven identiek en horen wat mij betreft niet in het
formulier: levertijd (`in onderling overleg`), levering (`franco werk`),
geldigheidsduur (`30 dagen`), garantietermijn (`12 maanden`), betalingstermijn
zakelijk (`30 dagen`).

> **Vraag 17.** Akkoord dat die vast staan? Als er offertes bestaan met een
> afwijkende levertijd of geldigheidsduur die ik niet heb gezien, hoor ik dat
> graag — dan worden het alsnog velden.

### Beslissing 4 — persoonsgegevens in de repository

`bronbrieven/uitgewerkt/` bevat namen, adressen, e-mailadressen en prijzen van
echte klanten: vier .docx- en drie pdf-brieven. Die staan nu in de git-geschiedenis van deze repository.

Ik heb ze daarom **niet** gecommit: `bronbrieven/uitgewerkt/` staat in
`.gitignore`, en in de opgeleverde analyse verwijs ik ernaar als `uitgewerkt-1`
tot en met `uitgewerkt-7` zonder namen, adressen of e-mailadressen. Wat er wel in
staat zijn de patronen zelf (de opbouw van `Ref.`, de btw-regel per klanttype) en
de bedragen die in de sjablonen staan.

Eén sjabloon uit de zip is niet helemaal leeg: **wand meervoud particulier.docx**
bevat nog een adres (straat, postcode en plaats) en een prijs van een echte
offerte. Die staat wel in git, omdat je hem als sjabloon aanleverde.

> **Vraag 20.** Wil je dat ik dat adres uit `wand meervoud particulier.docx` haal
> en er een echt leeg sjabloon van maak? En wil je de uitgewerkte brieven alsnog
> in de repository hebben, of blijven ze buiten git?

### Beslissing 5 — de classificatiemarkering in de voettekst

In elke voettekst staat `C2-Vertrouwelijk`, en tweemaal achter elkaar
(`C2-VertrouwelijkC2-Vertrouwelijk`). Dat is vermoedelijk een automatische
markering van jullie documentclassificatiesysteem.

> **Vraag 19.** Moet die markering in de gegenereerde brieven blijven staan? En
> zo ja, hoort hij er één keer of twee keer te staan? Nu staat hij er dubbel, wat
> op een fout in het sjabloon lijkt.

---

## D. Suggesties — origineel blijft intact

Deze heb ik **niet** doorgevoerd; de brontekst staat ongewijzigd in
`teksten.yaml`.

1. **`Wij leveren en monteren ... Tevens wordt de unit door ons in bedrijf
   gesteld`** — de zin is lang en bevat drie onderwerpen. Splitsen zou hem
   leesbaarder maken, maar het is een werkzaamhedenomschrijving met juridische
   lading, dus ik raak hem niet aan.

2. **De aanhef `Geachte heer/mevrouw,`** verdwijnt vanzelf zodra de tool de naam
   invult. Overweeg wel wat er moet gebeuren als de aanspreekvorm onbekend is —
   `Geachte heer of mevrouw,` is netter dan de schuine streep.

3. **`De installatie is aangeboden inclusief:`** bij een opdrachtbevestiging is
   raar — daar is niets meer aangeboden. `De opdracht omvat:` zou beter zijn.
   Speelt alleen als je Beslissing 2 met ja beantwoordt.

4. **Bedragen zonder streepje** (`€ 28.250` in uitgewerkt-5) lezen
   als onaf. Ongeacht wat je bij Vraag 13 kiest, zou de tool één notatie moeten
   afdwingen.

5. **De particuliere facturerings- en betalingsblokken** zijn met tabs
   uitgelijnd, wat in Word bij een andere regellengte scheef loopt. In het nieuwe
   sjabloon zou dit een tabel zonder randen moeten worden.
