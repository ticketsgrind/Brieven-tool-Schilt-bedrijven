# bronbrieven/

Zet hier de bestaande offertebrieven neer als `.docx`. De bestandsnaam mag de
variant aangeven, bijvoorbeeld:

    wandmodel-enkelvoud-particulier.docx
    wandmodel-meervoud-bedrijf.docx
    vloermodel-enkelvoud-particulier.docx

Uitlezen:

    python3 tools/extract_docx.py

Dat schrijft per brief een leesbare `.md` en één gezamenlijke `_alles.json` naar
`analyse/_extract/`. Die uitvoer is de basis voor `analyse/skelet.md`,
`analyse/variabelen.md` en `analyse/teksten.yaml`.

**Let op — persoonsgegevens.** Staan er echte klantnamen en adressen in deze
brieven, houd er dan rekening mee dat ze in de git-geschiedenis terechtkomen
zodra je ze commit. Zie `analyse/vragen.md` §2.3.
