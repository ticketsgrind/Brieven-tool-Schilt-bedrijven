# Vragen en openstaande punten — fase 1

## 0. Blokkerend: de bronbrieven ontbreken

De map `bronbrieven/` was leeg toen ik begon; de repository bevatte nog geen
enkele commit en er stond geen enkel `.docx`-bestand in de omgeving.

Daardoor kon ik stap 1 t/m 5 van de opdracht niet uitvoeren. Ik heb bewust
**niets** verzonnen voor `skelet.md`, `variabelen.md` en `teksten.yaml` — een
verzonnen garantietermijn of betalingstermijn komt straks in elke offerte terug,
en dat is precies wat je in de werkwijze wilde voorkomen.

Wat er nu wel staat is de infrastructuur om de analyse te doen zodra de brieven
er zijn, plus de punten die jij zelf al hebt aangedragen.

**Wat ik nodig heb:** de `.docx`-bestanden in `bronbrieven/`. Zet ze daar neer
en commit ze, of lever ze aan in de sessie. Daarna draai ik
`python3 tools/extract_docx.py` en volgt de echte analyse.

---

## 1. Vragen die jij zelf al hebt opgeworpen

Deze staan hier geparkeerd; ik beantwoord ze uit de brieven zodra die er zijn.

| # | Vraag | Herkomst |
|---|---|---|
| 1 | Zit er een vast patroon in `projectnummer` en `referentie`? Jaartal plus volgnummer, initialen van de ondertekenaar, iets anders? Als er een patroon in zit kunnen we het laten voorstellen in plaats van intypen. | aanvulling §1 |
| 2 | Is `totaalprijs` inclusief of exclusief btw? Vermoeden: inclusief bij particulier, exclusief bij zakelijk. Te controleren. | aanvulling §1 |
| 3 | Wat staat er nu tussen de aanhalingstekens in de betreft-regel — een adres, een projectnaam, of een ruimteaanduiding? | aanvulling §2 |
| 4 | Welke gegevens komen per regel terug in de aanbiedingsspecificatie? Vermoeden: ruimte/verdieping, merk, typeaanduiding, vermogen in kW, aantal. | aanvulling §3 |
| 5 | Verschilt de opmaak van de aanbiedingsspecificatie tussen één installatie en meerdere? Lopende tekst bij één regel, opsomming of tabel bij meerdere? | aanvulling §3 |
| 6 | Verschilt de afsluiting per ondertekenaar — andere functieomschrijving, wel of geen mobiel nummer? | aanvulling §5 |
| 7 | Zit er een handtekeningafbeelding in de brieven? Zo ja, dan lever je die apart aan. | aanvulling §5 |

Het uitleesscript meldt per brief welke afbeeldingen erin zitten, dus vraag 7
beantwoordt zichzelf zodra de brieven er staan.

---

## 2. Vragen van mijn kant, vooraf

Deze hoef je nu niet te beantwoorden — ze worden waarschijnlijk vanzelf duidelijk
uit de brieven. Blijven ze onbeantwoord, dan kom ik erop terug.

1. **Dekken de bronbrieven alle varianten die je noemt?** Je beschrijft
   klanttype × model × enkelvoud/meervoud × montagewijze. Als een combinatie niet
   in de bronbrieven voorkomt, moet ik die tekst niet verzinnen. Ik zet zulke
   gaten in dit bestand in plaats van ze op te vullen.

2. **Welke brief is leidend bij tegenstrijdigheden?** Als twee brieven een andere
   garantietermijn of betalingstermijn noemen, is de nieuwste dan automatisch de
   juiste, of moet dat per geval intern uitgezocht worden?

3. **Bevatten de brieven klantgegevens van echte klanten?** Zo ja, dan zijn het
   persoonsgegevens in een git-repository. Ik kan de geëxtraheerde teksten
   anonimiseren voordat ze in `analyse/` belanden. Zeg maar of dat moet.

4. **Is de btw altijd 21%?** Voor woningen ouder dan twee jaar geldt bij bepaalde
   werkzaamheden een verlaagd tarief. Als dat in de brieven voorkomt, wordt
   `btw_tarief` een keuze in plaats van een constante.

---

## 3. Suggesties — origineel blijft intact

Nog leeg. Zie ik straks in de brieven een formulering die beter kan, dan zet ik
de suggestie hier neer en laat ik de brontekst ongewijzigd, zoals afgesproken.
