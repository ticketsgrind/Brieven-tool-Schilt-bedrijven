# Brieven-tool Schilt Airconditioning

Eén sjabloon plus een bibliotheek van tekstblokken, in plaats van tientallen
losse Word-bestanden per variant. Via een formulier worden een paar keuzes
gemaakt (klanttype, model, aantal binnenunits, montagewijze, extra's), waarna er
een Word-bestand en een PDF uitrollen.

## Waar staat het nu

**Fase 1 — inventarisatie — is afgerond.** Er is nog geen applicatiecode: geen
sjabloon, geen webformulier. Dat is fase 2, en daarvoor liggen er eerst vragen in
[`analyse/vragen.md`](analyse/vragen.md).

Geanalyseerd: 16 sjablonen en 7 uitgewerkte brieven. Resultaat: 141 tekstblokken
en circa 45 invulvariabelen.

## Indeling

    bronbrieven/         de 16 lege sjablonen (.dotx)
      uitgewerkt/        ingevulde klantbrieven — niet in git, zie LEESMIJ.md
    tools/
      extract_docx.py    leest .docx en .dotx uit met behoud van volgorde,
                         kopjes, opsommingen, tabellen en kop-/voetteksten
      extract_pdf.py     haalt tekst uit een PDF (standaardbibliotheek)
      maak_sjabloon.py   maakt sjablonen/brief.docx uit een bronbrief
    analyse/
      skelet.md          38 secties, met per sectie of hij altijd voorkomt
      variabelen.md      alle invulvariabelen, met de waarden uit de brieven
      teksten.yaml       141 tekstblokken met voorwaarde en bronvermelding
      vragen.md          antwoorden, inconsistenties en openstaande beslissingen
      _extract/          uitvoer van de scripts (niet in git)
    config/
      ondertekenaars.yaml   vier ondertekenaars plus de bedrijfsgegevens
    brieventool/
      expressies.py      veilige evaluatie van de voorwaarden uit teksten.yaml
      bibliotheek.py     laadt de tekstblokken en de ondertekenaars
      opmaak.py          bedragen, telwoorden, datums in Nederlandse notatie
      samenstellen.py    kiest de blokken en vult de plaatshouders in
      sjabloon.py        vult het Word-sjabloon in
      cli.py             opdrachtregel
    ontwerp/
      prototype.html     werkend prototype van de bediening, opent zonder server
      ververs_prototype.py  zet de actuele tekstblokken in het prototype
    sjablonen/
      brief.docx         het Word-sjabloon; gegenereerd, niet met de hand bewerken
    tests/               77 tests
    voorbeelden/         twee ingevulde offertes om mee te proberen

## Aan de slag

Een brief samenstellen en de tekst bekijken:

    python3 -m brieventool voorbeelden/particulier-wand-enkelvoud.yaml

Met `--blokken` zie je erbij welke tekstblokken zijn gebruikt. Met
`--docx uit/offerte.docx` schrijft hij een Word-bestand, zodra er een sjabloon is.

De tests draaien:

    python3 -m unittest discover -s tests -t .

De bronbrieven opnieuw uitlezen:

    python3 tools/extract_docx.py

Dat script gebruikt `python-docx` als dat geïnstalleerd is
(`pip install -r requirements.txt`) en valt anders terug op de
standaardbibliotheek — een `.docx` is een zip met XML, dus dat kan zonder externe
pakketten. De uitvoer is in beide gevallen gelijk.

## Het tekstenbestand centraal houden

De tool draait lokaal, maar `teksten.yaml` hoort op één plek te staan. Anders
lopen de teksten alsnog uit elkaar zodra meer mensen de tool gebruiken. Zet
daarom de omgevingsvariabele `BRIEVENTOOL_BIBLIOTHEEK` op een gedeelde map,
bijvoorbeeld een gesynchroniseerde OneDrive-map:

    set BRIEVENTOOL_BIBLIOTHEEK=C:\Users\<naam>\OneDrive - Schilt\Brieventool

Zonder die variabele leest de tool de bibliotheek uit de projectmap.

## Uitgangspunten

- Onze eigen formuleringen zijn letterlijk overgenomen; er is niets herschreven.
  Verbeteringen staan als suggestie in `analyse/vragen.md` §D, het origineel staat
  ongewijzigd in `teksten.yaml`.
- Elk blok in `teksten.yaml` heeft een `bron`-veld met het bestand waar de tekst
  vandaan komt, zodat elke zin terug te voeren is op een echte brief.
- Verschillen die alleen taalkundig zijn — enkelvoud versus meervoud, "de unit"
  versus "de units" — zijn enkelvoud- en meervoudvarianten van hetzelfde blok, geen
  losse blokken.
- Waar de brieven onderling verschillen zonder duidelijke reden staan beide
  varianten apart, met de vraag erbij in `analyse/vragen.md` §B.
