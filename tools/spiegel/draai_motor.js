/* Draait de spiegel uit ontwerp/prototype.html buiten de browser.
   Gebruik: node tools/spiegel/draai_motor.js <prototype.html> <offerte.json> [docx]
   Zonder "docx" komt de samengestelde brief als JSON op stdout; met "docx" komt
   het Word-bestand als ruwe bytes op stdout. Zo kan een test vergelijken of de
   spiegel dezelfde brief maakt als brieventool/samenstellen.py. */
const fs = require("fs");
const pad = require("path");

const bron = fs.readFileSync(process.argv[2], "utf8");
function stuk(naam) {
  const begin = bron.indexOf(`/*<${naam}>*/`), eind = bron.indexOf(`/*</${naam}>*/`);
  if (begin < 0 || eind < 0) throw new Error(`markering ${naam} ontbreekt`);
  return bron.slice(begin, eind);
}

const tijdelijk = pad.join(fs.mkdtempSync("/tmp/spiegel-"), "motor.js");
fs.writeFileSync(tijdelijk, stuk("motor") + stuk("word") +
  "\n;module.exports={A,stelSamen,maakDocument,maakWordBestand,ontbrekendeGegevens};");
const motor = require(tijdelijk);

const offerte = JSON.parse(fs.readFileSync(process.argv[3], "utf8"));
for (const sleutel of Object.keys(motor.A)) delete motor.A[sleutel];
Object.assign(motor.A, {eigenAlineas: {}}, offerte);

(async () => {
  const brief = motor.stelSamen();
  if (process.argv[4] === "docx") {
    process.stdout.write(Buffer.from(await motor.maakWordBestand(brief.secties)));
  } else {
    process.stdout.write(JSON.stringify({
      secties: brief.secties, gebruikt: brief.gebruikt,
      ontbreekt: motor.ontbrekendeGegevens(),
    }, (sleutel, waarde) => sleutel === "blok" || sleutel === "reden" ? undefined : waarde));
  }
})();
