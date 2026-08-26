# Brieven-tool Schilt Airconditioning

Eén sjabloon plus een bibliotheek van tekstblokken, in plaats van tientallen
losse Word-bestanden per variant. Via een formulier worden een paar keuzes
gemaakt (klanttype, model, aantal binnenunits, montagewijze, extra's), waarna er
een Word-bestand en een PDF uitrollen.

## Waar staat het nu

**Fase 1 — inventarisatie — is gestart maar nog niet uitgevoerd.** De map
`bronbrieven/` is leeg, en zonder de bestaande brieven valt er niets te
analyseren. Wat er nu staat is het gereedschap plus de vragen. Zie
[`analyse/vragen.md`](analyse/vragen.md) §0.

Er is nog geen applicatiecode: geen sjabloon, geen webformulier. Dat is fase 2.

## Indeling

    bronbrieven/         de bestaande offertebrieven als .docx  (nu leeg)
    tools/
      extract_docx.py    leest de brieven uit met behoud van volgorde,
                         kopjes, opsommingen, tabellen en kop-/voetteksten
    analyse/
      skelet.md          gemeenschappelijke structuur van een brief
      variabelen.md      alle invulvariabelen
      teksten.yaml       de tekstblokkenbibliotheek
      vragen.md          inconsistenties, open vragen, suggesties
      _extract/          uitvoer van extract_docx.py (niet in git)
    config/
      ondertekenaars.yaml   Nick, John en Ricardo; nieuwe collega = één blok erbij

## Aan de slag

1. Zet de `.docx`-brieven in `bronbrieven/`.
2. Lees ze uit:

       python3 tools/extract_docx.py

   Het script gebruikt `python-docx` als dat geïnstalleerd is
   (`pip install -r requirements.txt`) en valt anders terug op de
   standaardbibliotheek — een `.docx` is een zip met XML, dus dat kan zonder
   externe pakketten. De uitvoer is in beide gevallen gelijk.
3. Vul op basis van `analyse/_extract/` de analysebestanden.

## Uitgangspunten

- Onze eigen formuleringen worden letterlijk overgenomen. Commerciële en
  juridische zinnen zijn bewust zo gekozen; verbeteringen gaan als suggestie naar
  `analyse/vragen.md` en het origineel blijft staan.
- Verschillen die alleen taalkundig zijn — enkelvoud versus meervoud, "de unit"
  versus "de units", u versus jij — zijn variabelen binnen één blok, geen aparte
  blokken.
- Bij twijfel geen aanname, maar een vraag in `analyse/vragen.md`.
