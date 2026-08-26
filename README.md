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
    analyse/
      skelet.md          38 secties, met per sectie of hij altijd voorkomt
      variabelen.md      alle invulvariabelen, met de waarden uit de brieven
      teksten.yaml       141 tekstblokken met voorwaarde en bronvermelding
      vragen.md          antwoorden, inconsistenties en openstaande beslissingen
      _extract/          uitvoer van de scripts (niet in git)
    config/
      ondertekenaars.yaml   vier ondertekenaars plus de bedrijfsgegevens

## Aan de slag

    python3 tools/extract_docx.py

Het script gebruikt `python-docx` als dat geïnstalleerd is
(`pip install -r requirements.txt`) en valt anders terug op de
standaardbibliotheek — een `.docx` is een zip met XML, dus dat kan zonder externe
pakketten. De uitvoer is in beide gevallen gelijk.

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
