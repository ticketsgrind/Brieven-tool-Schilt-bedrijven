# ontwerp/

`prototype.html` is een werkend prototype van de bedieningskant: links de vragen,
rechts de brief die meteen meeverandert. Open het bestand in een browser; er is
niets voor nodig.

Het draait op de echte bibliotheek: de 136 tekstblokken uit `analyse/teksten.yaml`
staan erin, en de JavaScript spiegelt `brieventool/samenstellen.py` — dezelfde
voorwaarden, dezelfde keuzegroepen, dezelfde enkelvouds- en meervoudsregels. Wat
je in het prototype ziet, is dus wat de motor werkelijk produceert.

Bijwerken na een wijziging in teksten.yaml:

    python3 ontwerp/ververs_prototype.py

Wat het prototype nog niet doet: een Word-bestand schrijven, offertes bewaren,
en de technische specificaties uitschrijven (zie `analyse/vragen.md`, beslissing 1).
