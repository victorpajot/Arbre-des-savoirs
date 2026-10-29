// Assemble www/ à partir de ../web et ../data : la page web et le contenu restent la seule source.
const fs = require("fs"), path = require("path");
const racine = path.resolve(__dirname, ".."), www = path.join(__dirname, "www");
fs.rmSync(www, { recursive: true, force: true });
fs.mkdirSync(path.join(www, "data"), { recursive: true });
// Polices embarquées (polices/) à la place de Google Fonts : l'app ne fait aucune requête réseau.
const page = fs.readFileSync(path.join(racine, "web/index.html"), "utf8")
  .replace(/<link[^>]*fonts\.(googleapis|gstatic)\.com[^>]*>\s*/g, "");
if (/fonts\.(googleapis|gstatic)/.test(page)) throw new Error("Lien Google Fonts restant dans web/index.html");
fs.cpSync(path.join(__dirname, "polices"), path.join(www, "polices"), { recursive: true });
// Sans viewport-fit=cover, Capacitor 8 garde la page entre la barre d'état et la barre de navigation (Android 15+ plein écran).
fs.writeFileSync(path.join(www, "index.html"),
  '<!doctype html><html lang="fr"><head><meta charset="utf-8">' +
  '<meta name="viewport" content="width=device-width,initial-scale=1">' +
  '<link rel="stylesheet" href="polices/polices.css">' +
  "<style>:root{padding-top:env(safe-area-inset-top);padding-bottom:env(safe-area-inset-bottom)}body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style>" +
  "</head><body>" + page + "</body></html>");
fs.copyFileSync(path.join(racine, "web/moteur.js"), path.join(www, "moteur.js"));
for (const f of fs.readdirSync(path.join(racine, "data"))) {
  if (f.endsWith(".json")) fs.copyFileSync(path.join(racine, "data", f), path.join(www, "data", f));
}
console.log("www/ assemblé");
