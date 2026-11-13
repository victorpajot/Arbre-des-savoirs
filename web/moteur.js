/* Moteur du jeu : règles pures, sans affichage ni stockage.
 * Le même calcul doit être reproduit à l'identique sur mobile et dans Unreal :
 * toutes les valeurs (XP, seuils, intervalles) viennent de regles.json.
 * Une « partie » est un objet JSON simple, versionné par son champ `format`.
 */
(function (racine) {
  "use strict";

  var FORMAT_PARTIE = 4;
  var JOUR = 86400000;
  var MAX_JOURNAL = 200;
  var MAX_RECENTES = 6;
  var MAX_HISTORIQUE = 30;   // déplacements gardés sur le plateau
  var MAX_ENCHAINEMENT = 12; // cases spéciales enchaînées au plus en un déplacement
  var ECLAIR_MS = 2000;       // réponse fausse plus rapide que ça : « éclair »
  var QUIZ_ECLAIR_MS = 60000; // quiz raté plus vite que ça
  var ABSENCE_RETOUR = 14;    // jours sans visite qui comptent comme un retour

  // --- Langue ----------------------------------------------------------------
  // Le contenu est écrit en objets texte {"fr": …} (la langue source de son pack). Une autre langue se lit dans le
  // dictionnaire data/langues/<xx>.json (outils/langues.py) : « textes » pour le contenu, « interface » pour les
  // chaînes du code, écrites en français dans __("…").
  var LANGUE = "fr", DICO = {}, CATALOGUE = {};
  function choisirLangue(langue, fichier) {
    LANGUE = langue || "fr";
    DICO = (fichier && fichier.textes) || {};
    CATALOGUE = (fichier && fichier.interface) || {};
  }
  function langue() { return LANGUE; }
  // Le texte d'un objet {"fr": …} dans la langue du joueur ; à défaut, dans sa langue source.
  function TX(o) {
    if (!o) return "";
    if (typeof o === "string") return o;
    if (o[LANGUE] != null) return o[LANGUE];
    var src = o.fr != null ? o.fr : o[Object.keys(o)[0]];
    if (src == null) return "";
    return DICO[src] || CATALOGUE[src] || src;
  }
  // Les textes qui ne sont pas des objets {"fr"} : étiquettes et aria-label des schémas SVG, quelques champs simples
  // (outils/langues.py, CHAMPS_SIMPLES). Traduits une fois, au chargement : changer de langue relance le jeu.
  var CHAMPS_SIMPLES = { langue: 1, traducteur: 1, reference: 1, titre: 1 }, CLES_IGNOREES = { source: 1, url: 1, verification: 1, id: 1 };
  var RE_SVG = [/(<text\b[^>]*>)([^<]*)(<\/text>)/g, /(<tspan\b[^>]*>)([^<]*)(<\/tspan>)/g, /(aria-label=")([^"]*)(")/g];
  // Une étiquette se cherche d'abord sous « aria-label ␟ étiquette », propre à son schéma (outils/langues.py).
  function traduireSvg(svg) {
    var aria = (/aria-label="([^"]*)"/.exec(svg) || ["", ""])[1];
    RE_SVG.forEach(function (r) { svg = svg.replace(r, function (m, a, t, b) { return a + (DICO[aria + "\u241f" + t] || DICO[t] || t) + b; }); });
    return svg;
  }
  function traduireChaines(o) {
    if (LANGUE === "fr" && !Object.keys(DICO).length) return o;
    (function voir(x) {
      if (!x || typeof x !== "object") return;
      Object.keys(x).forEach(function (k) {
        var v = x[k];
        if (typeof v === "string") {
          if (v.indexOf("<svg") >= 0) x[k] = traduireSvg(v);
          else if (CHAMPS_SIMPLES[k] && DICO[v]) x[k] = DICO[v];
        } else if (!CLES_IGNOREES[k]) voir(v);
      });
    })(o);
    return o;
  }
  // Une chaîne du code, écrite en français ; {nom} est remplacé par params.nom.
  function __(s, params) {
    var t = LANGUE !== "fr" && CATALOGUE[s] || s;
    return params ? t.replace(/\{(\w+)\}/g, function (m, k) { return k in params ? params[k] : m; }) : t;
  }

  // --- Contenu ---------------------------------------------------------------

  // `extras` (facultatif) : { commentaires, objets, avatar, ia, plateau, frise, bibliotheque }, les fichiers du même nom.
  // Victor (2026-10-31) : une année à taper est juste à `quiz.tolerance_annees` (50) ans près, avant ou après.
  var ENONCE_ANNEE = /\bquelle ann[ée]e\b/i;
  function estQuestionAnnee(q) { return q.type === "numerique" && !q.atome && ENONCE_ANNEE.test((q.enonce && q.enonce.fr) || "") && !/\bâge\b/i.test(q.enonce.fr); }
  function indexerContenu(regles, skills, questions, succes, extras) {
    extras = extras || {};
    var TA = (regles.quiz && regles.quiz.tolerance_annees) || 0;
    if (TA) questions.questions.forEach(function (q) { if (estQuestionAnnee(q)) { q.annee = true; q.tolerance = Math.max(q.tolerance || 0, TA); } });
    var c = {
      regles: regles,
      stats: regles.stats,
      competences: skills.competences,
      figures: skills.figures || {},
      questions: questions.questions,
      succes: succes.succes,
      dessinsSucces: succes.dessins || {},
      objets: extras.objets ? extras.objets.objets : [],
      cabinet: extras.objets || null,
      avatar: extras.avatar || null,
      narrateur: extras.commentaires ? extras.commentaires.narrateur : null,
      apartes: extras.commentaires && extras.commentaires.apartes ? extras.commentaires.apartes : [],
      surnoms: extras.commentaires && extras.commentaires.surnoms ? extras.commentaires.surnoms : null,
      parSucces: {},
      ennemis: extras.ennemis ? extras.ennemis.ennemis : [],
      ennemiParId: {},
      mythes: extras.ennemis ? extras.ennemis.mythes : [],
      placement: extras.ennemis ? extras.ennemis.placement : null,
      reserve: extras.ennemis ? extras.ennemis.reserve : null,
      questionsDuel: extras.ennemis ? extras.ennemis.questions_par_duel : 5,
      ia: extras.ia || null,
      plateau: extras.plateau || null,
      evenements: extras.frise ? extras.frise.evenements : [],
      frise: extras.frise || null,
      livres: extras.bibliotheque ? extras.bibliotheque.livres : [],
      atomes: extras.atomes || null,
      donjons: extras.donjons || null,
      ile: extras.ile || null,
      parId: {},
      parStat: {},
      questionsPar: {},
      questionParId: {},
      commentairesPar: {},
    };
    if (extras.commentaires) extras.commentaires.commentaires.forEach(function (r) {
      (c.commentairesPar[r.contexte] = c.commentairesPar[r.contexte] || []).push(r);
    });
    c.stats.forEach(function (s) { c.parStat[s.id] = []; });
    c.succes.forEach(function (s) { c.parSucces[s.id] = s; });
    c.ennemis.forEach(function (e) { c.ennemiParId[e.id] = e; });
    c.competences.forEach(function (k) {
      c.parId[k.id] = k;
      (c.parStat[k.stat] = c.parStat[k.stat] || []).push(k);
    });
    Object.keys(c.parStat).forEach(function (s) {
      c.parStat[s].sort(function (a, b) { return a.rang - b.rang; });
    });
    c.questions.forEach(function (q) {
      (c.questionsPar[q.competence] = c.questionsPar[q.competence] || []).push(q);
      c.questionParId[q.id] = q;
    });
    // v34 (Victor) : les ratés des combats d'atomes vont au mur de la honte. Chaque élément y a ses trois questions,
    // rangées sous « Atomes et éléments », hors des quiz ordinaires.
    if (c.atomes) c.atomes.elements.forEach(function (e) {
      questionsMur(c.atomes, e).forEach(function (q) { c.questionParId[q.id] = q; });
    });
    return c;
  }

  // --- Packs (v35) ------------------------------------------------------------
  // Le contenu vient de packs (data/packs.json en est l'index). Un pack désactivé en jeu disparaît : son arbre, ses
  // questions, ses objets, ses répliques… La progression n'est pas touchée : tout revient quand on le réactive.

  // Les packs éteints : ceux demandés, plus ceux qui en dépendent. Le socle ne s'éteint jamais.
  // Un pack qui déclare « reglages »: { « allume »: false } est éteint tant qu'on ne l'a pas allumé (« +id » dans la liste).
  function packsEteints(index, demandes) {
    var off = {}, liste = (index && index.packs) || [], change = true;
    liste.forEach(function (m) { if (!allumeParDefaut(m) && (demandes || []).indexOf("+" + m.id) < 0) off[m.id] = true; });
    (demandes || []).forEach(function (id) { if (id.charAt(0) !== "+") off[id] = true; });
    delete off.socle;
    function propager() {
      change = true;
      while (change) {
        change = false;
        liste.forEach(function (m) {
          if (!off[m.id] && m.sorte !== "socle" && (m.requiert || []).some(function (r) { return off[r]; })) { off[m.id] = true; change = true; }
        });
      }
    }
    propager();
    // Victor (2026-11-09) : un domaine dit de quels jeux il se passe (« reglages »: { « sans »: [« dramaturgie »] }). Tant que
    // tous les domaines allumés s'en passent, ce jeu reste éteint ; le joueur le rallume comme un pack éteint par défaut (« +id »).
    packsEcartes(index, off).forEach(function (id) { if ((demandes || []).indexOf("+" + id) < 0) off[id] = true; });
    propager();
    return off;
  }
  // Les packs de jeu dont tous les domaines allumés se passent (`off` : les packs déjà éteints).
  function packsEcartes(index, off) {
    var liste = (index && index.packs) || [];
    var doms = liste.filter(function (m) { return m.sorte === "domaine" && !off[m.id]; });
    if (!doms.length) return [];
    return liste.filter(function (m) {
      return m.sorte === "jeu" && doms.every(function (d) { return ((d.reglages && d.reglages.sans) || []).indexOf(m.id) >= 0; });
    }).map(function (m) { return m.id; });
  }

  // `donnees` : { "regles.json": …, "skills.json": … } tels que chargés. Renvoie une copie sans les packs éteints.
  function filtrerPacks(donnees, index, demandes) {
    var off = packsEteints(index, demandes);
    if (!Object.keys(off).length) return donnees;
    var d = JSON.parse(JSON.stringify(donnees));
    // v36 : l'année de chaque case reste connue quand son pack s'éteint (conditions « case atteinte », téléportations).
    if (d["plateau.json"] && d["plateau.json"].cases) {
      var an = {}; d["plateau.json"].cases.forEach(function (k) { an[k.n] = k.annee; }); d["plateau.json"].annees = an;
    }
    var proprios = (index && index.proprietaires) || {};
    // Victor (2026-11-04) : un portrait peut appartenir à plusieurs domaines (champ domaines). Son domaine éteint, il reste
    // tant qu'un des autres est allumé, rangé sous ce domaine. Un savant ainsi gardé devient un simple portrait (pas de
    // condition de déblocage hors de son domaine).
    var garder = {}, migrants = [], av0 = d["avatar.json"];
    ["savants", "portraits"].forEach(function (cle) {
      var ou = "avatar.json/" + cle, pr = proprios[ou] || {};
      ((av0 && av0[cle]) || []).forEach(function (x) {
        var p = pr[String(x.id)]; if (!p || !off[p] || !x.domaines) return;
        var alt = x.domaines.filter(function (id) { return !off[id] && (index.packs || []).some(function (m) { return m.id === id; }); })[0];
        if (!alt) return;
        if (cle === "portraits") { (garder[ou] || (garder[ou] = {}))[String(x.id)] = 1; x.theme = alt; }
        else migrants.push({ id: x.id, nom: x.nom, annees: x.annees, bio: x.notice || x.bio, source: x.source, couleurs: x.couleurs, base: x.base, cheveux: x.cheveux, noms: x.noms, theme: alt });
      });
    });
    (index.packs || []).forEach(function (m) { if (off[m.id]) (m.fichiers || []).forEach(function (f) { d[f] = null; }); });
    // Un pack de jeu qui écrit dans un fichier du socle n'y possède que ses clés (« cles » de l'index) : éteint, elles partent.
    (index.packs || []).forEach(function (m) {
      if (off[m.id] && m.cles) Object.keys(m.cles).forEach(function (f) {
        m.cles[f].forEach(function (ch) {
          var parts = ch.split("/"), o = d[f];
          for (var i = 0; i < parts.length - 1 && o; i++) o = o[parts[i]];
          if (o) delete o[parts[parts.length - 1]];
        });
      });
    });
    function cleDe(x) { return x && (x.id !== undefined ? String(x.id) : x.n !== undefined ? String(x.n) : x.z !== undefined ? String(x.z) : x.comp !== undefined ? String(x.comp) : null); }
    Object.keys(proprios).forEach(function (ou) {
      var parts = ou.split("/"), o = d[parts[0]];
      for (var i = 1; i < parts.length - 1 && o; i++) o = o[parts[i]];
      var dernier = parts[parts.length - 1];
      if (!o || !Array.isArray(o[dernier])) return;
      o[dernier] = o[dernier].filter(function (x) { var p = proprios[ou][cleDe(x)]; return !(p && off[p]) || (garder[ou] && garder[ou][cleDe(x)]); });
    });
    if (migrants.length && d["avatar.json"]) {
      var pts = d["avatar.json"].portraits || (d["avatar.json"].portraits = []);
      migrants.forEach(function (x) { if (!pts.some(function (y) { return y.id === x.id; })) { if (!x.noms) delete x.noms; pts.push(x); } });
    }
    // Ce qui pointe encore vers un élément disparu est nettoyé : prérequis, cases, arbres de départ.
    var comps = {}, stats = {};
    if (d["skills.json"]) d["skills.json"].competences.forEach(function (k) { comps[k.id] = true; });
    if (d["regles.json"]) {
      d["regles.json"].stats.forEach(function (s) { stats[s.id] = true; });
      var R = d["regles.json"];
      R.arbres_fondamentaux = (R.arbres_fondamentaux || []).filter(function (s) { return stats[s]; });
      // Plus aucun arbre de départ : le premier arbre restant ouvre la partie, les autres s'ouvrent sur le parcours.
      if (!R.arbres_fondamentaux.length && R.stats.length) R.arbres_fondamentaux = [R.stats[0].id];
    }
    if (d["skills.json"]) d["skills.json"].competences.forEach(function (k) { k.prerequis = k.prerequis.filter(function (p) { return comps[p]; }); });
    var pl = d["plateau.json"];
    if (pl && pl.competences_cases) Object.keys(pl.competences_cases).forEach(function (n) {
      pl.competences_cases[n] = pl.competences_cases[n].filter(function (c) { return comps[c]; });
    });
    // Sans masques du jour (dramaturgie éteinte), le narrateur ne porte que ses masques de base, ceux qui ne se gagnent pas.
    var ia = d["ia.json"];
    if (ia && ia.masques && !ia.masques_jour) ia.masques = ia.masques.filter(function (m) { return !m.condition; });
    return d;
  }

  // --- Packs additionnels (v53) ------------------------------------------------
  // Un pack de domaine chargé par le joueur : un fichier « paquet » (outils/packs.py paquet), dont les fragments se
  // posent dans les données chargées comme le ferait l'assemblage. Nous ne garantissons ni leur contenu ni leur sécurité :
  // seuls les packs de domaine (des données, jamais de code) se chargent ainsi.
  var FORMAT_PAQUET = "arbre-des-savoirs/pack";
  // Où un pack de domaine a le droit d'écrire : les emplacements d'outils/packs.py (EMPLACEMENTS).
  var EMPLACEMENTS_PAQUET = ["regles.json/stats", "skills.json/competences", "skills.json/figures", "questions.json/questions", "succes.json/succes",
    "succes.json/dessins", "objets.json/objets", "avatar.json/savants", "avatar.json/portraits", "avatar.json/accessoires", "avatar.json/tenues_farce", "ia.json/masques",
    "bibliotheque.json/livres", "frise.json/evenements", "commentaires.json/commentaires", "commentaires.json/apartes", "ia.json/credits/piques",
    "plateau.json/cases", "plateau.json/competences_cases", "ennemis.json/mythes", "ia.json/credits/boutique/articles", "ile.json/installations"];
  function ajouterTextes(dico) { Object.keys(dico || {}).forEach(function (k) { if (DICO[k] == null) DICO[k] = dico[k]; }); }
  function cleElement(x) { return x && typeof x === "object" && (x.id !== undefined ? String(x.id) : x.n !== undefined ? String(x.n) : x.z !== undefined ? String(x.z) : x.comp !== undefined ? String(x.comp) : null); }
  function lieu(donnees, fichier, chemin, creer) {
    var o = donnees[fichier];
    if (!o) return null;
    for (var i = 0; i < chemin.length - 1; i++) { if (!o[chemin[i]]) { if (!creer) return null; o[chemin[i]] = {}; } o = o[chemin[i]]; }
    return o;
  }
  // Ce que le joueur doit savoir avant d'installer : { erreurs, compte, maj }. Une erreur empêche l'installation.
  function verifierPaquet(donnees, index, paquet) {
    var erreurs = [], compte = {}, m = paquet && paquet.manifeste;
    if (!paquet || paquet.format !== FORMAT_PAQUET || !m || !Array.isArray(paquet.fragments)) return { erreurs: ["format"], compte: compte };
    if (m.sorte !== "domaine") erreurs.push("sorte");
    if (!/^[a-z][a-z0-9-]*$/.test(String(m.id || "")) || !m.nom || !m.version) erreurs.push("manifeste");
    var existant = ((index && index.packs) || []).filter(function (x) { return x.id === m.id; })[0];
    if (existant && !existant.ajoute) erreurs.push("officiel");
    var manque = (m.requiert || []).filter(function (r) { return !((index && index.packs) || []).some(function (x) { return x.id === r; }); });
    if (manque.length) erreurs.push("requiert:" + manque.join(","));
    var proprios = (index && index.proprietaires) || {};
    paquet.fragments.forEach(function (f) {
      var ou = f.fichier + "/" + (f.chemin || []).join("/");
      if (EMPLACEMENTS_PAQUET.indexOf(ou) < 0) { erreurs.push("emplacement:" + ou); return; }
      var n = Array.isArray(f.elements) ? f.elements.length : Object.keys(f.elements || {}).length;
      compte[ou] = (compte[ou] || 0) + n;
      var parent = lieu(donnees, f.fichier, f.chemin, false), cible = parent && parent[f.chemin[f.chemin.length - 1]];
      if (!Array.isArray(f.elements) || !Array.isArray(cible)) return;
      var vus = {};
      cible.forEach(function (x) { var c = cleElement(x); if (c != null && (proprios[ou] || {})[c] !== m.id) vus[c] = true; });
      var doubles = f.elements.map(cleElement).filter(function (c) { return c != null && vus[c]; });
      if (doubles.length) erreurs.push("doublon:" + ou + ":" + doubles.slice(0, 3).join(","));
    });
    return { erreurs: erreurs, compte: compte, maj: existant ? existant.version : null };
  }
  // Pose le paquet dans les données (modifiées sur place) et l'inscrit dans l'index, comme un pack assemblé.
  function ajouterPaquet(donnees, index, paquet) {
    var m = paquet.manifeste, proprios = index.proprietaires || (index.proprietaires = {});
    function fusion(cible, v, ou) {
      if (Array.isArray(v)) {
        var p = proprios[ou] || (proprios[ou] = {});
        v.forEach(function (x) { var c = cleElement(x); if (c != null) p[c] = m.id; });
        Array.prototype.push.apply(cible, JSON.parse(JSON.stringify(v)));
        return;
      }
      Object.keys(v).forEach(function (k) {
        if (cible[k] === undefined) cible[k] = JSON.parse(JSON.stringify(v[k]));
        else if (Array.isArray(cible[k]) && Array.isArray(v[k])) Array.prototype.push.apply(cible[k], v[k]);
        else if (cible[k] && typeof cible[k] === "object" && v[k] && typeof v[k] === "object") fusion(cible[k], v[k], ou + "/" + k);
      });
    }
    paquet.fragments.forEach(function (f) {
      var parent = lieu(donnees, f.fichier, f.chemin, true); if (!parent) return;
      var k = f.chemin[f.chemin.length - 1];
      if (parent[k] === undefined) parent[k] = Array.isArray(f.elements) ? [] : {};
      fusion(parent[k], f.elements, f.fichier + "/" + f.chemin.join("/"));
    });
    var R = donnees["regles.json"];
    if (R) R.arbres_fondamentaux = (R.arbres_fondamentaux || []).concat(paquet.fondamentaux || []);
    var B = donnees["bibliotheque.json"];
    if (B && B.livres) B.livres.sort(function (a, b) { return a.annee - b.annee; });
    index.packs.push(Object.assign({}, m, { ajoute: true, sources: paquet.sources || null }));
    return donnees;
  }

  // Ce qu'une partie a en cours dans un jeu éteint (duel, atomes en attente) dort dans partie.veille et revient au
  // réveil du pack : un pack désactivé ne bloque pas le plateau et ne perd rien.
  function accorderPartie(contenu, partie) {
    var v = partie.veille || (partie.veille = {});
    function garer(cle, actif, vide) {
      var plein = Array.isArray(partie[cle]) ? partie[cle].length > 0 : !!partie[cle];
      if (!actif && plein) { v[cle] = partie[cle]; partie[cle] = vide; }
      else if (actif && v[cle] !== undefined) { if (!plein) partie[cle] = v[cle]; delete v[cle]; }
    }
    garer("duel", contenu.ennemis.length > 0, null);
    // La dramaturgie éteinte, ce qu'Alyca tenait en suspens dort aussi : son ultimatum et la peine au mur ne bloquent pas le jeu.
    garer("ultimatum", dramaturgie(contenu), null);
    garer("punition", dramaturgie(contenu), null);
    garer("farce", dramaturgie(contenu), null);
    garer("humeurPerso", dramaturgie(contenu), null);
    garer("objetIA", dramaturgie(contenu), null);
    garer("emplettes", dramaturgie(contenu), []);
    garer("sauvages", !!contenu.atomes, []);
    // Une révision forcée sur une compétence d'un pack éteint dort aussi : elle bloquerait le pion.
    var rv = partie.revision;
    if (rv && !contenu.parId[rv.comp]) { v.revision = rv; partie.revision = null; }
    else if (!rv && v.revision && contenu.parId[v.revision.comp]) { partie.revision = v.revision; delete v.revision; }
    accorderPlateau(contenu, partie);
    return partie;
  }
  // v36 : les cases viennent des packs. Une case dont le pack s'éteint quitte le tour en cours (elle reviendra dans un
  // prochain tour) ; le pion qui s'y tenait recule sur la dernière case encore là. La case d'Alyca ferme toujours la route.
  function accorderPlateau(contenu, partie) {
    var pl = partie.plateau;
    if (!pl || !contenu.plateau || !contenu.plateau.cases.length) return;
    if (pl.anneeMax == null && !pl.tours && pl.atteinte > 1) pl.anneeMax = anneeAtteinte(contenu, pl);
    var arr = arriveeN(contenu), present = function (n) { return !!caseN(contenu, n); };
    function nettoyer(l) { var o = l.filter(present); if (o[o.length - 1] !== arr) { o = o.filter(function (n) { return n !== arr; }); o.push(arr); } return o; }
    if (pl.parcoursSuivant && pl.parcoursSuivant.cases) pl.parcoursSuivant.cases = nettoyer(pl.parcoursSuivant.cases);
    if (!pl.route) { route(contenu, partie); return; }
    // Une route réduite à l'arrivée (tous les domaines éteints un moment) se redessine dès qu'un domaine revient.
    var seule = function (l) { return l.length < 2 && contenu.plateau.cases.length > 1; };
    if (pl.route.every(present) && pl.route[pl.route.length - 1] === arr && !seule(pl.route)) return;
    var vieille = pl.route, i = vieille.indexOf(pl.position), rt = nettoyer(vieille);
    if (pl.parcours && pl.parcours.cases) pl.parcours.cases = nettoyer(pl.parcours.cases);
    if (seule(rt)) { pl.parcours = null; pl.route = null; pl.redessiner = true; route(contenu, partie); return; }
    pl.route = rt;
    if (!present(pl.position)) {
      var j = i;
      while (j > 0 && !present(vieille[j])) j--;
      pl.position = present(vieille[j]) ? vieille[j] : rt[0];
    }
    pl.idx = rt.indexOf(pl.position);
    if (pl.idx < 0) { pl.idx = 0; pl.position = rt[0]; }
  }

  // Réglages de partie (Victor, 2026-10-30, fil « Basile ») : des entrées ouvertes, indépendantes du type de pack. Un pack
  // les propose dans son manifeste (« reglages »), la partie les garde dans options.reglages, le joueur les change dans
  // les réglages. Aucune n'est propre à un pack : un pack pour enfants n'est qu'un pack qui en déclare plusieurs.
  //   allume    : false = le pack est éteint par défaut (à allumer dans l'assistant ou les réglages)
  //   ton       : le ton d'Alyca ; ses répliques « ton.<ton>.<moment> » remplacent les siennes (ex. « enfant »)
  //   voix      : true = questions et réponses lues à voix haute
  //   texte     : « grand » = gros caractères, Oui/Non au lieu de Vrai/Faux
  //   ultimatum : false = Alyca ne lance pas d'ultimatum
  //   vol       : false = un ennemi vainqueur ne vole pas de crédits
  //   mur       : le nom du mur de la honte (« revisions »)
  var REGLAGES = ["ton", "voix", "texte", "ultimatum", "vol", "mur"];
  function reglage(partie, cle) { var r = partie && partie.options && partie.options.reglages; return r ? r[cle] : undefined; }
  // Le ton du narrateur : celui que la partie a choisi ; sinon, sans dramaturgie (pas de faveur), un ton sobre, qui dit
  // les choses sans se moquer. Avec la dramaturgie, null : c'est Alyca qui parle, sur son ton à elle.
  var TON_SOBRE = "sobre";
  function dramaturgie(contenu) { return !!(contenu && contenu.ia && contenu.ia.faveur); }
  function tonDe(contenu, partie) {
    var ton = reglage(partie, "ton");
    if (ton) return ton;
    return contenu.ia && !dramaturgie(contenu) && (contenu.commentairesPar["ton." + TON_SOBRE + ".defaut"] || []).length ? TON_SOBRE : null;
  }
  // Victor (2026-11-03) : allumer un pack allume aussi ce qu'il demande (récursivement) ; un donjon coché coche ses domaines.
  function allumerPack(index, demandes, id) {
    var liste = (index && index.packs) || [], out = (demandes || []).slice(), vus = {};
    (function allumer(x) {
      if (vus[x] || x === "socle") return; vus[x] = true;
      var m = liste.filter(function (y) { return y.id === x; })[0]; if (!m) return;
      out = out.filter(function (d) { return d !== x && d !== "+" + x; });
      (m.requiert || []).forEach(allumer);
      // Encore éteint une fois ce qu'il demande allumé : il l'est par défaut (« allume »: false) ou les domaines s'en passent (« sans »).
      if (packsEteints(index, out)[x]) out.push("+" + x);
    })(id);
    return out;
  }
  function allumeParDefaut(m) { return !(m && m.reglages && m.reglages.allume === false); }
  // Les réglages d'une nouvelle partie : ceux sur lesquels tous les domaines allumés s'accordent. Un domaine qui ne
  // déclare rien garde le jeu tel quel : un pack pour enfants allumé avec un domaine adulte ne change rien.
  function reglagesDesPacks(index, off) {
    var doms = ((index && index.packs) || []).filter(function (m) { return m.sorte === "domaine" && !off[m.id]; }), r = {};
    if (!doms.length) return r;
    REGLAGES.forEach(function (k) {
      var v = (doms[0].reglages || {})[k];
      if (v !== undefined && doms.every(function (m) { return (m.reglages || {})[k] === v; })) r[k] = v;
    });
    return r;
  }

  // Le pack d'un élément (« questions.json/questions », id) ; « socle » s'il n'en a pas d'autre.
  function packDe(index, ou, id) {
    var p = index && index.proprietaires && index.proprietaires[ou];
    return (p && p[String(id)]) || "socle";
  }

  // --- Temps -----------------------------------------------------------------

  function maintenant(partie) {
    return Date.now() + (partie.decalage || 0);
  }

  function debutJour(t) {
    var d = new Date(t);
    d.setHours(0, 0, 0, 0);
    return d.getTime();
  }

  function ajouterJours(t, n) {
    var d = new Date(debutJour(t));
    d.setDate(d.getDate() + n);
    return d.getTime();
  }

  function cleJour(t) {
    var d = new Date(t);
    var m = d.getMonth() + 1, j = d.getDate();
    return d.getFullYear() + "-" + (m < 10 ? "0" : "") + m + "-" + (j < 10 ? "0" : "") + j;
  }

  function joursEntre(a, b) {
    return Math.round((debutJour(b) - debutJour(a)) / JOUR);
  }

  // --- Partie ----------------------------------------------------------------

  function nouvellePartie(t) {
    return {
      format: FORMAT_PARTIE,
      cree: t,
      maj: t,
      decalage: 0,
      competences: {},
      succes: {},
      objets: {},
      accessoires: {},
      savants: {},
      personnes: {},
      avatar: { tete: null, visage: null, main: null, savant: null },
      apparence: null,
      pouvoirs: {},
      tenues: {},
      humeurPerso: null,
      compteurs: {
        quizParfaits: 0, quizRates: 0, rappelsReussis: 0, serieRappels: 0, perdues: 0, regagnees: 0,
        quizJoues: 0, quizEclairRates: 0, quizZero: 0, quizNuit: 0, quizAube: 0, chronoParfaits: 0,
        reponsesEclairFausses: 0, rappelsRetard: 0, retours: 0, modeTest: 0, parfaitsParStat: {},
        eurekas: 0, sortiesPrison: 0, reculs: 0, duelsGagnes: 0, duelsPerdus: 0, cadeaux: 0,
        atomesCaptures: 0, atomesEnfuis: 0,
      },
      jours: [],
      journal: [],
      repliques: {},
      evenements: {},
      livres: {},
      masque: null,
      masques: {},
      farce: null,
      gagnables: {},
      bestiaire: {},
      duel: null,
      cadeaux: { jour: null, donnes: {} },
      credits: { solde: 0, gagnes: 0, parSucces: {}, record: 0, jour: null, pots: 0 },
      ultimatum: null,
      objetIA: null,
      inventaire: {},
      tresorIA: {},
      emplettes: [],
      atomes: {},
      sauvages: [],
      donjons: {},
      proces: {},
      siecles: null,
      faveur: null,
      colere: null,
      masquesJour: null,
      butinAssure: false,
      oublis: [],
      plateau: nouveauPlateau(),
      derniereVisite: t,
      retour: null,
      options: { chrono: true },
    };
  }

  function nouveauPlateau() {
    // v7 : ennemis (case → id, posés au début de chaque tour) et cases spéciales déplacées par l'IA (case → règle ou null).
    // v15 : `visites` = cases où le pion s'est arrêté (les seules dévoilées) ; `arrets` = celles du tour en cours ;
    // `coups` = épreuves jouées dans ce tour, `meilleur` = le tour le plus court.
    return { position: 1, idx: 0, route: null, remanie: null, atteinte: 1, tours: 0, visites: { 1: 1 }, arrets: { 1: 1 }, coups: 0, meilleur: null,
      prison: 0, quarantaine: 0, historique: [], bonus: null, ennemis: null, speciaux: {} };
  }

  // Remet une partie lue (stockage, import) au format courant.
  // v1 → v2 : nouveaux compteurs, objets, accessoires et avatar ; la progression reste intacte.
  // v2 → v3 : plateau (départ à la case du feu), frise, bibliothèque, masque de l'IA, répliques retenues par contexte.
  // v3 → v4 : les rappels déjà réussis sont repayés au nouveau barème (XP croissante par étape) ; avatar savant.
  // v5 (même format) : le masque choisi par le joueur disparaît, la farce de l'IA apparaît.
  // v6 (même format) : butin en attente ; le savant incarné se déduit des succès.
  // v7 (même format) : bestiaire, duel en cours, cadeaux à l'IA ; les ennemis du plateau sont posés au premier besoin.
  // `contenu` (facultatif) fournit le barème ; sans lui, celui par défaut.
  function migrer(p, contenu) {
    if (!p || typeof p !== "object" || typeof p.format !== "number") return null;
    if (p.format > FORMAT_PARTIE) return null;
    var base = nouvellePartie(p.cree || Date.now());
    var out = Object.assign(base, p);
    out.compteurs = Object.assign(nouvellePartie(0).compteurs, p.compteurs || {});
    out.compteurs.parfaitsParStat = Object.assign({}, (p.compteurs && p.compteurs.parfaitsParStat) || {});
    out.competences = p.competences || {};
    out.succes = p.succes || {};
    out.objets = p.objets || {};
    out.accessoires = p.accessoires || {};
    out.savants = p.savants || {};
    out.personnes = p.personnes || {};
    out.avatar = Object.assign({ tete: null, visage: null, main: null, savant: null }, p.avatar || {});
    if (p.format < 4) {
      var c4 = contenu || { regles: { xp: { rappel_par_etape: [5, 10, 15, 20, 30, 40, 50], par_rappel_reussi: 5 } } };
      Object.keys(out.competences).forEach(function (id) {
        var e = out.competences[id];
        if (!e.maitrise || !e.palier) return;
        for (var i = 1; i <= e.palier; i++) e.xp = (e.xp || 0) + xpRappel(c4, i) - 5;
      });
    }
    out.jours = p.jours || [];
    out.journal = p.journal || [];
    out.repliques = Array.isArray(p.repliques) || !p.repliques ? {} : p.repliques;
    out.evenements = p.evenements || {};
    out.livres = p.livres || {};
    out.masque = p.masque || null;
    out.masques = p.masques || {};
    // v5 : l'IA choisit seule son masque ; l'ancien choix du joueur est oublié.
    delete out.masqueChoisi;
    out.farce = p.farce || null;
    out.alyca = p.alyca || null;
    // v25 : plus de farce qui remplace le personnage par un savant ; une ancienne en cours est levée.
    if (out.farce && out.farce.type === "savant") out.farce = null;
    // v6 : butin en attente (conditions remplies, pas encore tombé). Ce qui est déjà gagné reste acquis.
    out.gagnables = p.gagnables || {};
    // v7 : ennemis, duels et cadeaux à l'IA.
    out.bestiaire = p.bestiaire || {};
    out.duel = p.duel || null;
    // v21 : un duel perdu reste ouvert (revanche obligatoire), y compris dans les anciennes parties.
    if (out.duel && p.plateau && out.duel.case === p.plateau.position) out.duel.pret = true;
    out.cadeaux = Object.assign({ jour: null, donnes: {} }, p.cadeaux || {});
    out.objetIA = p.objetIA || null;
    out.ultimatum = p.ultimatum || null;
    // v16 : crédits. Une ancienne partie reçoit le tarif normal pour les succès déjà obtenus.
    out.credits = Object.assign({ solde: 0, gagnes: 0, parSucces: {}, record: 0, jour: null, pots: 0 }, p.credits || {});
    if (!p.credits && contenu && contenu.ia && contenu.ia.credits) {
      contenu.succes.forEach(function (sc) { if (out.succes[sc.id]) { var n = tarifSucces(contenu, sc); out.credits.solde += n; out.credits.gagnes += n; out.credits.parSucces[sc.id] = { n: n, humeur: "normal" }; } });
    }
    // v9 : tableau périodique (z → fiche) et atomes sauvages en attente de combat.
    out.atomes = p.atomes || {};
    out.sauvages = p.sauvages || [];
    // Donjons : pièces posées, bugs, allumage (vides dans une ancienne partie).
    out.donjons = p.donjons || {};
    out.proces = p.proces || {};
    // v34 : Chrono, le jeu des siècles (posé au premier besoin).
    out.siecles = p.siecles || null;
    // v10 : faveur de l'IA (posée au premier besoin) et jour de son dernier piège.
    out.faveur = p.faveur || null;
    out.colere = p.colere || null;
    // v11 : masques choisis par l'IA pour la journée, et butin promis par l'objet tenu.
    out.masquesJour = p.masquesJour || null;
    out.butinAssure = !!p.butinAssure;
    // v12 : questions ratées, épinglées au mur de la honte.
    out.oublis = p.oublis || [];
    out.plateau = Object.assign(nouveauPlateau(), p.plateau || {});
    out.derniereVisite = p.derniereVisite || p.maj || out.cree;
    out.options = Object.assign({ chrono: false }, p.options || {});
    out.format = FORMAT_PARTIE;
    return out;
  }

  function etatComp(partie, id) {
    return partie.competences[id] || null;
  }

  function estMaitrisee(partie, id) {
    var e = etatComp(partie, id);
    return !!(e && e.maitrise);
  }

  // Un arbre est ouvert s'il est fondamental, si le joueur y a déjà maîtrisé quelque chose (la première case
  // de l'arbre sur le parcours l'ouvre) ou si l'option de démo ouvre tout. Les succès « pionniers » qui
  // ouvraient les arbres ont été retirés (Victor, 2026-11-10) : les parties qui en ont gardent leurs arbres.
  var ANCIENS_PIONNIERS = { "pionnier-ciceron": "eloquence", "pionnier-lavoisier": "alchimie", "pionnier-galilee": "cosmos", "pionnier-bacon": "lucidite",
    "pionnier-faraday": "etincelle", "pionnier-william-james": "empathie", "pionnier-socrate": "sagesse", "pionnier-mersenne": "musique",
    "pionnier-informatique": "informatique", "pionnier-essaim": "essaim", "pionnier-mnemosyne": "mnemosyne" };
  function arbreOuvert(contenu, partie, stat) {
    // Mode Île par âges : ce sont les âges qui ouvrent les savoirs, plus les arbres.
    if (modeIle(partie) && agesPresents(contenu)) return true;
    var fond = contenu.regles.arbres_fondamentaux;
    if (!fond || fond.indexOf(stat) >= 0) return true;
    if (partie.options && partie.options.tousArbres) return true;
    for (var anc in ANCIENS_PIONNIERS) if (ANCIENS_PIONNIERS[anc] === stat && partie.succes[anc]) return true;
    // v15 : il faut l'avoir maîtrisée au moins une fois (un quiz raté sur une case d'arbre fermé n'ouvre rien).
    return (contenu.parStat[stat] || []).some(function (k) { var e = partie.competences[k.id]; return !!(e && (e.maitrise || e.maitriseDepuis || e.xp)); });
  }
  // v15 : sur une case d'arbre fermé, l'IA propose le premier quiz de cet arbre ; le réussir l'ouvre.
  function porteArbre(contenu, partie, stat) {
    if (arbreOuvert(contenu, partie, stat)) return null;
    return (contenu.parStat[stat] || []).filter(function (k) {
      return k.rang === 1 && k.prerequis.every(function (p) { return contenu.parId[p] && contenu.parId[p].stat !== stat ? debloque(contenu, partie, p) : true; });
    })[0] || null;
  }
  // Statut affiché d'une compétence.
  // verrouillee : prérequis manquants ; disponible : quiz jouable ;
  // maitrisee / a_reviser : acquise, rappel à venir ou dû ;
  // gelee (drapeau) : acquise mais un prérequis a été perdu, elle ne débloque plus rien.
  // fermee : l'arbre de la compétence n'est pas encore ouvert (v7).
  function statut(contenu, partie, id, t) {
    var k = contenu.parId[id];
    // Mode Île par âges : un savoir pas encore appris n'est proposé que si un besoin d'un âge ouvert le demande.
    if (modeIle(partie) && agesPresents(contenu) && !(partie.options && partie.options.tousArbres) && !estMaitrisee(partie, id) && !savoirOuvertIle(contenu, partie, id))
      return { etat: "verrouillee", gelee: false, age: ageDuSavoir(contenu, id) };
    if (!arbreOuvert(contenu, partie, k.stat)) return { etat: "fermee", gelee: false };
    var prerequisOk = k.prerequis.every(function (p) { return debloque(contenu, partie, p); });
    var e = etatComp(partie, id);
    if (e && e.maitrise) {
      return {
        etat: t >= e.prochainRappel ? "a_reviser" : "maitrisee",
        gelee: !prerequisOk,
        horsOrdre: !prerequisOk && !!e.horsOrdre,
        prochainRappel: e.prochainRappel,
        palier: e.palier,
      };
    }
    return { etat: prerequisOk ? "disponible" : "verrouillee", gelee: false, dejaPerdue: !!(e && e.perdue) };
  }

  function debloque(contenu, partie, id) {
    // Une compétence gelée ne compte pas comme prérequis acquis.
    var k = contenu.parId[id];
    return estMaitrisee(partie, id) && k.prerequis.every(function (p) { return debloque(contenu, partie, p); });
  }

  // --- XP et niveaux ---------------------------------------------------------

  function xpParStat(contenu, partie) {
    var xp = {};
    contenu.stats.forEach(function (s) { xp[s.id] = 0; });
    Object.keys(partie.competences).forEach(function (id) {
      var e = partie.competences[id], k = contenu.parId[id];
      if (k && e.maitrise) xp[k.stat] += e.xp || 0;
    });
    return xp;
  }

  function niveau(contenu, xp) {
    var p = contenu.regles.xp.paliers_niveau;
    var n = 0;
    while (n + 1 < p.length && xp >= p[n + 1]) n++;
    var max = n + 1 >= p.length;
    return { niveau: n, xp: xp, debut: p[n], suivant: max ? null : p[n + 1] };
  }

  function niveauGlobal(contenu, partie) {
    var xp = xpParStat(contenu, partie);
    return contenu.stats.reduce(function (s, st) { return s + niveau(contenu, xp[st.id]).niveau; }, 0);
  }

  // --- Questions -------------------------------------------------------------

  function melanger(liste, alea) {
    var a = liste.slice();
    for (var i = a.length - 1; i > 0; i--) {
      var j = Math.floor(alea() * (i + 1));
      var x = a[i]; a[i] = a[j]; a[j] = x;
    }
    return a;
  }

  function tirerQuestions(contenu, partie, id, n, alea) {
    alea = alea || Math.random;
    var e = etatComp(partie, id);
    var recentes = (e && e.recentes) || [];
    var toutes = melanger(contenu.questionsPar[id] || [], alea);
    var fraiches = toutes.filter(function (q) { return recentes.indexOf(q.id) < 0; });
    var vues = toutes.filter(function (q) { return recentes.indexOf(q.id) >= 0; });
    return fraiches.concat(vues).slice(0, n);
  }

  function lireNombre(texte) {
    if (typeof texte === "number") return texte;
    var s = String(texte || "").replace(/\s| | /g, "").replace(",", ".");
    if (!/^[-+]?\d*\.?\d+$/.test(s)) return NaN;
    return parseFloat(s);
  }

  // `reponse` : index du choix d'origine (qcm), booléen (vrai_faux) ou texte saisi (numérique).
  function corriger(question, reponse) {
    if (question.type === "qcm") return reponse === question.reponse;
    if (question.type === "vrai_faux") return reponse === question.reponse;
    if (question.type === "place") return Number(reponse) === question.reponse;
    var v = lireNombre(reponse);
    return !isNaN(v) && Math.abs(v - question.reponse) <= (question.tolerance || 0) + 1e-9;
  }

  // --- Actions ---------------------------------------------------------------

  // Bonus des bonnes réponses données avec le chrono activé.
  function bonusChrono(contenu, resultats) {
    return resultats.filter(function (x) { return x.correct && x.chrono; }).length * contenu.regles.chrono.bonus_xp_par_bonne_reponse;
  }

  // v12 : le mur de la honte. Chaque réponse fausse y est épinglée, avec la réponse donnée ; 30 jours de mémoire.
  var HONTE_JOURS = 30, HONTE_MAX = 300;
  function epinglerOublis(partie, comp, resultats, t, src) {
    var ratees = resultats.filter(function (x) { return !x.correct; });
    if (!ratees.length) return;
    var o = partie.oublis || (partie.oublis = []);
    ratees.forEach(function (x) { o.push({ t: t, q: x.id, comp: comp, rep: x.rep === undefined ? null : x.rep, src: src, efface: null, essais: 0 }); });
    partie.compteurs.hontes = (partie.compteurs.hontes || 0) + ratees.length;
    var limite = t - HONTE_JOURS * JOUR;
    partie.oublis = o.filter(function (e) { return e.t >= limite; }).slice(-HONTE_MAX);
  }
  // Le mur : ratées du jour (une par question, la plus récente) et des jours précédents. Chaque entrée garde son index.
  function murDeLaHonte(contenu, partie, t, joursAvant) {
    var aujourdhui = [], avant = [], vus = {};
    var o = partie.oublis || [];
    for (var i = o.length - 1; i >= 0; i--) {
      var e = o[i], j = joursEntre(e.t, t);
      if (!contenu.questionParId || !contenu.questionParId[e.q]) continue;
      var cle = j + "|" + e.q;
      if (vus[cle]) continue;
      vus[cle] = true;
      var x = { index: i, entree: e, question: contenu.questionParId[e.q], jours: j };
      if (j === 0) aujourdhui.push(x);
      else if (j <= (joursAvant == null ? 7 : joursAvant)) avant.push(x);
    }
    var aRetenter = avant.filter(function (x) { return !x.entree.efface; });
    // Une question ratée plusieurs jours de suite ne se retente qu'une fois : la plus récente.
    var dejaVue = {};
    aRetenter = aRetenter.filter(function (x) { if (dejaVue[x.entree.q]) return false; dejaVue[x.entree.q] = true; return true; });
    return { aujourdhui: aujourdhui, avant: avant, restantes: aujourdhui.filter(function (x) { return !x.entree.efface; }).length, aRetenter: aRetenter.length };
  }
  // Retenter une question du mur, à partir du lendemain : se souvenir après une nuit, c'est ça qui ancre.
  // Réussie : elle est effacée (réhabilitée), avec toutes ses épingles précédentes.
  function retenterOubli(contenu, partie, index, correct, t) {
    var e = partie.oublis && partie.oublis[index];
    if (!e || e.efface || joursEntre(e.t, t) < 1) return null;
    e.essais = (e.essais || 0) + 1;
    e.essai = t;
    if (correct) {
      partie.oublis.forEach(function (x) { if (x.q === e.q && !x.efface && x.t <= e.t) x.efface = t; });
      partie.compteurs.hontesEffacees = (partie.compteurs.hontesEffacees || 0) + 1;
    }
    var faveur = correct ? radoucirIA(contenu, partie, t) : null;
    // v30 (Victor) : enfermé, une question à retenter réussie retire aussi du temps à la peine.
    var peine = null;
    if (correct && partie.punition && partie.punition.restant > 0) {
      var ms = ((contenu.ia && contenu.ia.faveur && contenu.ia.faveur.mur_rattrapage) || 1) * 60000;
      peine = { gagne: ms, reste: purger(partie, ms) };
    }
    partie.maj = t;
    var rec = verifierRecompenses(contenu, partie, t);
    return { efface: !!correct, essais: e.essais, replique: replique(contenu, partie, [correct ? "honte_effacee" : "honte_ratee"]), nouveauxSucces: rec.succes, faveur: faveur, peine: peine };
  }
  // v29 : un rappel réussi au mur la radoucit d'un point, plafonné par jour (agacement.rappel_mur_jour).
  function radoucirIA(contenu, partie, t) {
    var A = contenu.ia && contenu.ia.credits && contenu.ia.credits.agacement, avant = faveurIA(contenu, partie, t);
    if (!A || !A.rappel_mur || !avant) return null;
    var j = cleJour(t), d = partie.radouci && partie.radouci.jour === j ? partie.radouci : (partie.radouci = { jour: j, n: 0 });
    var gain = Math.min(A.rappel_mur, (A.rappel_mur_jour || Infinity) - d.n, 100 - avant.valeur);
    if (gain <= 0) return { gain: 0, plafond: d.n >= (A.rappel_mur_jour || Infinity), avant: avant, apres: avant };
    d.n += gain;
    partie.faveur = { valeur: avant.valeur + gain, maj: t };
    return { gain: gain, avant: avant, apres: faveurIA(contenu, partie, t) };
  }

  function noter(partie, t, entree) {
    entree.t = t;
    partie.journal.push(entree);
    if (partie.journal.length > MAX_JOURNAL) partie.journal.splice(0, partie.journal.length - MAX_JOURNAL);
  }

  function marquerJour(partie, t) {
    var cle = cleJour(t);
    if (partie.jours.indexOf(cle) < 0) {
      partie.jours.push(cle);
      if (partie.jours.length > 400) partie.jours.shift();
    }
  }

  function retenirQuestions(e, ids) {
    e.recentes = ids.concat((e.recentes || []).filter(function (q) { return ids.indexOf(q) < 0; })).slice(0, MAX_RECENTES);
  }

  // Compteurs communs aux quiz et aux rappels : heure de jeu, réponses fausses données trop vite.
  function compterSession(partie, resultats, t) {
    var c = partie.compteurs, h = new Date(t).getHours();
    if (h >= 2 && h < 5) c.quizNuit++;
    else if (h >= 5 && h < 7) c.quizAube++;
    c.reponsesEclairFausses += resultats.filter(function (x) { return estEclair(x); }).length;
    return h >= 2 && h < 5;
  }

  // Une réponse fausse donnée en moins de deux secondes. `x` : {correct, ms}.
  function estEclair(x) {
    return !x.correct && typeof x.ms === "number" && x.ms < ECLAIR_MS;
  }

  // v15 : l'épreuve est-elle déjà perdue ? Alors on la coupe, sans dévoiler les questions restantes.
  // `mode` : quiz, rappel, duel (tout juste exigé) ou atome (`seuil` bonnes réponses).
  function epreuvePerdue(contenu, mode, bonnes, repondues, total, seuil) {
    var reste = total - repondues;
    if (mode === "duel") return bonnes < repondues;
    var besoin = mode === "quiz" ? Math.ceil(total * contenu.regles.quiz.seuil_maitrise - 1e-9)
      : mode === "rappel" ? contenu.regles.rappels.bonnes_reponses_min : seuil;
    return bonnes + reste < besoin;
  }

  // Termine un quiz d'apprentissage. `resultats` : [{id, correct, chrono, ms}] ;
  // `infos` (facultatif) : {duree} en ms, {total} si le quiz a été coupé avant la fin.
  var MASTERCLASS_APRES_ECHECS = 2;
  function aLecon(k) { return !!(k && k.masterclass && k.masterclass.chapitres && k.masterclass.chapitres.length); }
  // La masterclass imposée, si sa compétence existe encore (pack allumé) ; sinon rien.
  // Victor (2026-10-31) : le Pokédex des personnages. Une personne est rencontrée quand le jeu la montre (masterclass, quiz,
  // case) ; un savant débloqué par un succès compte aussi. Renvoie vrai la première fois.
  function rencontrer(partie, id, t) {
    if (!partie.personnes) partie.personnes = {};
    if (partie.personnes[id] != null || (partie.savants && partie.savants[id] != null)) return false;
    partie.personnes[id] = t == null ? Date.now() : t; return true;
  }
  function rencontre(partie, id) { return (partie.personnes && partie.personnes[id] != null) || (partie.savants && partie.savants[id] != null); }
  function masterclassImposee(contenu, partie) {
    var m = partie.masterclass; return m && aLecon(contenu.parId[m.id]) ? m : null;
  }
  // Lue jusqu'au dernier chapitre : la consigne tombe. Renvoie vrai si c'était bien celle-là.
  function masterclassLue(partie, id) {
    if (!partie.masterclass || partie.masterclass.id !== id) return false;
    delete partie.masterclass; return true;
  }
  function terminerQuiz(contenu, partie, id, resultats, t, infos) {
    var r = contenu.regles, c = partie.compteurs, k = contenu.parId[id];
    var photo = photoIle(contenu, partie, id, t);
    ouvrirLot(partie, t, k && k.stat); partie.lot.comp = id;
    var bonnes = resultats.filter(function (x) { return x.correct; }).length;
    var total = Math.max(resultats.length, (infos && infos.total) || 0);
    var reussi = bonnes / total >= r.quiz.seuil_maitrise - 1e-9;
    var parfait = bonnes === total;
    var e = partie.competences[id] || (partie.competences[id] = { maitrise: false });
    retenirQuestions(e, resultats.map(function (x) { return x.id; }));
    marquerJour(partie, t);
    var nuit = compterSession(partie, resultats, t);
    c.quizJoues++;
    if (parfait) {
      c.quizParfaits++;
      c.parfaitsParStat[k.stat] = (c.parfaitsParStat[k.stat] || 0) + 1;
      if (resultats.every(function (x) { return x.chrono; })) c.chronoParfaits++;
    }
    if (bonnes === 0) c.quizZero++;
    if (!reussi && infos && typeof infos.duree === "number" && infos.duree < QUIZ_ECLAIR_MS) c.quizEclairRates++;
    e.echecsSuite = reussi ? 0 : (e.echecsSuite || 0) + 1;
    // Victor (2026-10-30) : deux épreuves ratées de suite sur la même compétence, l'IA impose sa masterclass,
    // lue jusqu'au bout avant toute autre épreuve. Les erreurs de la dernière tentative y sont corrigées.
    if (!reussi && e.echecsSuite >= MASTERCLASS_APRES_ECHECS && aLecon(k))
      partie.masterclass = { id: id, depuis: t, rates: resultats.filter(function (x) { return !x.correct; }).map(function (x) { return { id: x.id, rep: x.rep }; }) };
    var xp = 0;
    if (reussi) {
      xp = bonnes * r.xp.par_bonne_reponse + r.xp.bonus_maitrise + bonusChrono(contenu, resultats);
      if (e.perdue) partie.compteurs.regagnees++;
      e.maitrise = true;
      e.maitriseDepuis = t;
      e.palier = 0;
      e.prochainRappel = ajouterJours(t, r.rappels.intervalles_jours[0]);
      e.xp = xp;
      e.horsOrdre = !k.prerequis.every(function (p) { return debloque(contenu, partie, p); });
    } else {
      partie.compteurs.quizRates++;
    }
    noter(partie, t, { type: "quiz", comp: id, bonnes: bonnes, total: total, xp: xp, source: "quiz" });
    epinglerOublis(partie, id, resultats, t, "quiz");
    partie.maj = t;
    var contextes = [];
    if (bonnes === 0) contextes.push("quiz_zero");
    if (nuit) contextes.push("nuit");
    if (reussi) contextes.push(parfait ? (k.rang === 1 ? "quiz_parfait_facile" : "quiz_parfait") : "quiz_reussi");
    else contextes.push(k.rang === 1 ? "quiz_rate_facile" : "quiz_rate");
    var chrono = resultats.length > 0 && resultats.every(function (x) { return x.chrono; });
    var jouer = !!(infos && infos.jouer);
    if (jouer) consommerArbre(partie, k.stat);
    var avant = verifierRecompenses(contenu, partie, t);
    if (reussi) ajouterButin(contenu, partie, avant, { type: "quiz", comp: id }, t, infos && infos.alea);
    var dep = jouerPlateau(contenu, partie, { type: "quiz", comp: id }, { reussi: reussi, parfait: parfait, chrono: chrono, jouer: jouer, uneCase: !!(infos && infos.uneCase) }, t);
    if (jouer) partie.depuisRappel = (partie.depuisRappel || 0) + 1;
    var ag = agacerIA(contenu, partie, resultats.length - bonnes, !reussi, t);
    lotExceptionnel(partie, dep);
    var apres = verifierRecompenses(contenu, partie, t), rec = fusionRec(avant, apres);
    if (rec.masque) contextes.splice(contextes.length - 1, 0, "masque");
    var fa = reussi ? null : tenterFarce(contenu, partie, t, infos && infos.alea, k.stat);
    return { issue: reussi ? "maitrisee" : "echec", bonnes: bonnes, total: total, xp: xp, prochainRappel: e.prochainRappel,
      nouveauxSucces: rec.succes, nouveauxObjets: rec.objets, nouveauxAccessoires: rec.accessoires, nouveauxSavants: rec.savants,
      nouveauxEvenements: rec.evenements, nouveauxLivres: rec.livres, masque: rec.masque, plateau: dep, contextes: contextes, farce: fa, jouer: jouer, agacement: ag, credits: rec.credits,
      avantPlateau: avant, apresPlateau: apres, ile: changementIle(contenu, partie, id, t, photo, reussi), gloire: suivreGloire(contenu, partie, id, t, reussi ? "acquis" : "rate", bonnes, total), theme: contenu.parId[id] ? contenu.parId[id].stat : null };
  }

  // XP d'un rappel réussi qui mène à l'étape `palier` (1 = premier rappel).
  function xpRappel(contenu, palier) {
    var t = contenu.regles.xp.rappel_par_etape;
    if (!t || !t.length) return contenu.regles.xp.par_rappel_reussi;
    return t[Math.min(Math.max(palier, 1), t.length) - 1];
  }

  // Termine un rappel. Réussi : l'intervalle suivant s'allonge. Raté : la compétence est perdue.
  // `infos` (facultatif) : {jouer, alea}, comme pour terminerQuiz.
  function terminerRappel(contenu, partie, id, resultats, t, infos) {
    var r = contenu.regles;
    var e = partie.competences[id];
    ouvrirLot(partie, t, contenu.parId[id] && contenu.parId[id].stat); partie.lot.comp = id;
    var photo = photoIle(contenu, partie, id, t);
    var bonnes = resultats.filter(function (x) { return x.correct; }).length;
    var total = Math.max(resultats.length, (infos && infos.total) || 0);
    var reussi = bonnes >= r.rappels.bonnes_reponses_min;
    var retard = Math.max(0, joursEntre(e.prochainRappel, t));
    // v8 : une révision forcée ne fait pas monter le palier, et la rater ne fait pas perdre la compétence :
    // son rappel devient dû, tout de suite.
    var rv = revisionEnCours(partie), revision = !!(rv && rv.comp === id);
    if (revision) partie.revision = null;
    // « Une case = un quiz » (Victor, 2026-10-31) : sur sa case, une compétence acquise se rejoue en rappel même pas encore dû.
    // Ce rappel anticipé ne fait pas monter le palier ni ne décale l'échéance ; raté, le rappel devient dû sans perdre la compétence.
    var anticipe = !revision && t < e.prochainRappel;
    var CCr = contenu.plateau && contenu.plateau.competences_cases, posR = partie.plateau && partie.plateau.position;
    var horsCase = !!(CCr && posR != null && (CCr[String(posR)] || []).indexOf(id) < 0);
    // Victor (2026-11-11) : pendant une série, on ne retourne pas sur le parcours : le pion ne bouge pas, même pour le rappel de sa case.
    if (partie.serie && partie.serie.ids[0] === id) horsCase = true;
    else if (partie.serieRompue) partie.serieRompue = null;
    retenirQuestions(e, resultats.map(function (x) { return x.id; }));
    marquerJour(partie, t);
    var nuit = compterSession(partie, resultats, t);
    if (retard >= 7) partie.compteurs.rappelsRetard++;
    var xp = 0, xpPerdue = 0;
    // Victor (2026-11-03) : le pouvoir « palais de mémoire » sauve un rappel raté ; il revient tout de suite, sans perte.
    var palais = !reussi && !revision && !anticipe && !!(infos && infos.palais) && utiliserPouvoir(contenu, partie, "palais", t);
    if ((revision || anticipe || palais) && !reussi) {
      e.prochainRappel = t;
      partie.compteurs.serieRappels = 0;
    } else if (reussi) {
      var iv = r.rappels.intervalles_jours;
      if (!revision && !anticipe) e.palier = (e.palier || 0) + 1;
      if (!anticipe) e.prochainRappel = ajouterJours(t, iv[Math.min(e.palier, iv.length - 1)]);
      xp = xpRappel(contenu, e.palier) + bonusChrono(contenu, resultats);
      e.xp = (e.xp || 0) + xp;
      partie.compteurs.rappelsReussis++;
      partie.compteurs.serieRappels++;
    } else {
      xpPerdue = e.xp || 0;
      e.maitrise = false;
      e.perdue = true;
      e.xp = 0;
      e.palier = 0;
      e.prochainRappel = null;
      e.maitriseDepuis = null;
      partie.compteurs.perdues++;
      partie.compteurs.serieRappels = 0;
    }
    noter(partie, t, { type: "rappel", comp: id, bonnes: bonnes, total: total, xp: reussi ? xp : -xpPerdue, source: revision ? "revision" : "rappel" });
    epinglerOublis(partie, id, resultats, t, revision ? "revision" : "rappel");
    partie.maj = t;
    var contextes = [];
    if (revision) contextes.push(reussi ? "revision_reussie" : "revision_ratee");
    else if (!reussi && !anticipe && !palais) contextes.push("rappel_perdu");
    if (nuit) contextes.push("nuit");
    if (!revision && reussi && retard >= 3) contextes.push("rappel_retard");
    if (!revision && reussi) contextes.push("rappel_reussi");
    var jouer = !!(infos && infos.jouer);
    if (jouer && contenu.parId[id]) consommerArbre(partie, contenu.parId[id].stat);
    var avant = verifierRecompenses(contenu, partie, t);
    if (reussi) ajouterButin(contenu, partie, avant, { type: "rappel", comp: id }, t, infos && infos.alea);
    // Un rappel qui n'est pas celui de la case (imposé, série) laisse le pion sur place : la case garde son quiz.
    var dep = revision && !reussi ? null : jouerPlateau(contenu, partie, { type: "rappel", comp: id }, { reussi: reussi && !horsCase, parfait: false, chrono: false, jouer: jouer, uneCase: !!(infos && infos.uneCase) }, t);
    if (jouer) partie.depuisRappel = anticipe ? (partie.depuisRappel || 0) + 1 : 0;
    var serie = null, se = partie.serie;
    if (se && se.ids[0] === id) {
      (se.faitsIds || (se.faitsIds = [])).push(se.ids.shift());
      if (!reussi) {
        // Victor (2026-11-11) : un raté coûte la prime, mais la série peut être reprise avec les rappels qui restent.
        partie.serie = null; partie.serieRompue = { t: t };
        var rp = serieReprenable(contenu, partie, t);
        serie = { fini: true, rate: true, total: se.total, faits: se.total - se.ids.length, reste: rp ? rp.n : 0, prime: rp ? rp.prime : 0 };
        if (!rp) partie.serieRompue = null;
      }
      else if (!se.ids.length) {
        partie.credits.solde += se.prime; partie.credits.gagnes += se.prime;
        serie = { fini: true, total: se.total, faits: se.total, credits: se.prime, ids: se.faitsIds.slice(), solde: partie.credits.solde }; partie.serie = null;
      } else serie = { fini: false, total: se.total, faits: se.total - se.ids.length, reste: se.ids.length, prime: se.prime };
    }
    var ag = agacerIA(contenu, partie, resultats.length - bonnes, !reussi, t);
    lotExceptionnel(partie, dep);
    var apres = verifierRecompenses(contenu, partie, t), rec = fusionRec(avant, apres);
    if (rec.masque) contextes.splice(contextes.length - 1, 0, "masque");
    var fa = reussi || revision || anticipe ? null : tenterFarce(contenu, partie, t, infos && infos.alea, contenu.parId[id] && contenu.parId[id].stat);
    return { revision: revision, issue: reussi ? "reussi" : revision ? "revision_ratee" : anticipe || palais ? "echec" : "perdue", anticipe: anticipe, palais: palais, horsCase: horsCase, serie: serie, bonnes: bonnes, total: total, xp: xp, xpPerdue: xpPerdue, prochainRappel: e.prochainRappel,
      retard: retard, nouveauxSucces: rec.succes, nouveauxObjets: rec.objets, nouveauxAccessoires: rec.accessoires, nouveauxSavants: rec.savants,
      nouveauxEvenements: rec.evenements, nouveauxLivres: rec.livres, masque: rec.masque, plateau: dep, contextes: contextes, farce: fa, jouer: jouer, agacement: ag, credits: rec.credits,
      avantPlateau: avant, apresPlateau: apres, ile: changementIle(contenu, partie, id, t, photo, reussi), gloire: suivreGloire(contenu, partie, id, t, reussi || revision || anticipe || palais ? null : "perdue", bonnes, total), theme: contenu.parId[id] ? contenu.parId[id].stat : null };
  }

  // À appeler à chaque ouverture de l'app : repère un retour après une longue absence.
  function noterVisite(contenu, partie, t) {
    var avant = partie.derniereVisite;
    partie.derniereVisite = t;
    if (avant && joursEntre(avant, t) >= ABSENCE_RETOUR) {
      partie.compteurs.retours++;
      partie.retour = t;
      return verifierRecompenses(contenu, partie, t);
    }
    return { succes: [], objets: [], accessoires: [], savants: [], evenements: [], livres: [], masque: null };
  }

  // Mode test : avance l'horloge du jeu de `jours` jours (0 = retour à l'heure réelle).
  function avancerHorloge(contenu, partie, jours) {
    if (jours) {
      partie.decalage = (partie.decalage || 0) + jours * JOUR;
      partie.compteurs.modeTest++;
    } else partie.decalage = 0;
    return verifierRecompenses(contenu, partie, maintenant(partie));
  }

  // --- Plateau ---------------------------------------------------------------
  // Un jeu de l'oie de 63 cases, du feu à l'IA. Pas de dé : chaque épreuve réussie vaut un
  // nombre de cases fixé par plateau.json. Les cases spéciales reprennent les règles de l'oie.

  // Bonus du jour : une stat, choisie une fois par jour parmi les plus délaissées.
  function bonusDuJour(contenu, partie, t) {
    var pl = partie.plateau, cle = cleJour(t);
    if (pl.bonus && pl.bonus.jour === cle) return pl.bonus.stat;
    var xp = xpParStat(contenu, partie);
    var jouables = contenu.stats.filter(function (s) {
      return contenu.parStat[s.id].some(function (k) { var st = statut(contenu, partie, k.id, t).etat; return st === "disponible" || st === "a_reviser"; });
    });
    if (!jouables.length) jouables = contenu.stats.slice();
    jouables.sort(function (a, b) { return xp[a.id] - xp[b.id]; });
    var candidats = jouables.slice(0, 3);
    var stat = candidats[Math.floor(debutJour(t) / JOUR) % candidats.length].id;
    pl.bonus = { jour: cle, stat: stat };
    return stat;
  }

  // Ce que rapporte une épreuve, tel qu'annoncé avant de la jouer. `epreuve` : {type: "quiz"|"rappel", comp}.
  function valeurEpreuve(contenu, partie, epreuve, t) {
    if (!contenu.plateau) return null;
    var r = contenu.plateau.regles, k = contenu.parId[epreuve.comp];
    // v6 : une épreuve vaut le rang de sa compétence, quiz comme rappel. v34 : une case Chrono, un nombre fixe de cases.
    var base = epreuve.type === "chrono" ? r.chrono.avance : r.valeurs.quiz_rang[String(k.rang)];
    var duJour = k && k.stat === bonusDuJour(contenu, partie, t) ? r.bonus.du_jour : 0;
    // v10 : comblée, l'IA ajoute une case ; furieuse, elle en retire une (jamais moins d'une).
    var fav = faveurIA(contenu, partie, t), faveur = fav ? fav.palier.avance : 0;
    // v11 : les masques du jour ajoutent ou retirent des cases, et durcissent ou adoucissent le rappel raté.
    var rj = reglesDuJour(contenu, partie, t), echec = epreuve.type === "rappel" ? r.echec.rappel : r.echec.quiz;
    if (epreuve.type === "rappel") echec = Math.round(echec * rj.echec);
    // Victor (2026-10-31) : une épreuve réussie fait avancer d'une seule case, ratée le pion reste. Plus de bonus d'avance.
    return { base: 1, duJour: 0, faveur: 0, masques: 0, total: 1, parfait: 0, chrono: 0, echec: 0 };
  }

  // v36 : chaque arbre apporte ses cases ; le numéro `n` d'une case est son identité (pas sa place dans la liste).
  function caseN(contenu, n) {
    var P = contenu.plateau; if (!P) return null;
    if (!P.parN) {
      var m = {}; P.cases.forEach(function (k) { m[k.n] = k; });
      Object.defineProperty(P, "parN", { value: m, enumerable: false, configurable: true });
    }
    return P.parN[n] || null;
  }
  // L'année d'une case, même si son pack est éteint (plateau.annees, posé par filtrerPacks).
  function anneeDe(contenu, n) {
    var k = caseN(contenu, n); if (k) return k.annee;
    var A = contenu.plateau && contenu.plateau.annees; return A && A[n] != null ? A[n] : null;
  }
  // La case d'arrivée (celle d'Alyca) ferme chaque tour ; à défaut, la plus récente.
  function arriveeN(contenu) {
    var P = contenu.plateau, a = P.cases.filter(function (k) { return k.arrivee; })[0];
    return a ? a.n : P.cases.slice().sort(parDate)[P.cases.length - 1].n;
  }
  function parDate(a, b) { return a.annee - b.annee || a.n - b.n; }
  // v36 (Victor) : le tour se compose de cases tirées dans tous les arbres allumés, rangées par date. La plus ancienne
  // ouvre toujours le tour ; les autres se répartissent entre les époques et les arbres, celles jamais vues d'abord.
  // Avec peu d'arbres allumés, le tour est plus court (choix de Victor) : jamais de case répétée ni hors sujet.
  function tirerCases(contenu, partie, longueur, g) {
    return tranche(contenu, partie, longueur).cases;
  }
  // Victor (2026-10-31) : les cases des arbres allumés, mêlées et rangées par date, coupées à `longueur` cases. Le tour
  // suivant reprend après la dernière case du tour précédent (pl.departTour) ; on ne revoit pas les premières.
  // `fin` : ce tour contient la dernière case de l'histoire, le boucler est une victoire.
  function tranche(contenu, partie, longueur) {
    var arr = arriveeN(contenu), pl = partie.plateau || {}, d = pl.departTour;
    var pool = contenu.plateau.cases.filter(function (k) { return k.n !== arr; }).sort(parDate);
    var i = 0;
    if (d) { while (i < pool.length && parDate(pool[i], d) <= 0) i++; if (i >= pool.length) i = 0; }
    // Victor (2026-11-08) : « Voir toutes les cases » dévoile les cases à venir mais garde la longueur du tour.
    var pris = pool.slice(i, i + Math.max(1, longueur));
    var dernier = pris[pris.length - 1];
    return { cases: pris.map(function (c) { return c.n; }).concat([arr]), fin: !dernier || pool.indexOf(dernier) === pool.length - 1,
      dernier: dernier ? { n: dernier.n, annee: dernier.annee } : null, debut: i, total: pool.length };
  }
  function casesParTour(contenu, partie) {
    var R = contenu.plateau.regles, v = partie.options && partie.options.casesTour;
    return (R.cases_par_tour_choix || []).indexOf(v) >= 0 ? v : R.cases_par_tour || 24;
  }
  // Une case est atteinte quand le pion s'y est arrêté (v15 : les cases survolées restent cachées ; le tirage des tours
  // suivants donne la priorité aux cases jamais vues). Une case dont le pack est éteint ne bloque rien : elle compte
  // comme atteinte dès que le pion a passé son année, ou fini un tour.
  // L'année la plus récente où le pion s'est arrêté pendant le premier tour. Sauvegardes d'avant v36 : la progression se
  // lisait au numéro de case (`atteinte`), alors chronologique sur les 63 cases d'origine.
  function anneeAtteinte(contenu, pl) {
    if (pl.anneeMax != null) return pl.anneeMax;
    var m = null;
    for (var n = 1; n <= Math.min(pl.atteinte || 1, 63); n++) { var a = anneeDe(contenu, n); if (a != null && (m == null || a > m)) m = a; }
    return m != null ? m : anneeDe(contenu, pl.position);
  }
  function caseAtteinte(contenu, partie, n) {
    var pl = partie.plateau;
    if ((pl.visites[n] || 0) > 0) return true;
    if (caseN(contenu, n)) return false;
    var a = anneeDe(contenu, n);
    var m = anneeAtteinte(contenu, pl);
    return pl.tours > 0 || (a != null && m != null && m >= a);
  }
  // v7 : la règle spéciale d'une case, en tenant compte des cases que l'IA a déplacées.
  function specialDe(contenu, partie, n) {
    var sp = partie.plateau.speciaux, x;
    // Victor (2026-10-31) : plus de case spéciale fixe ; seules comptent celles posées en jeu (événements, Alyca, cadeaux).
    if (sp && Object.prototype.hasOwnProperty.call(sp, n)) x = sp[n];
    // Pack atomes éteint : une case Mendeleïev redevient une case ordinaire.
    return x && x.type === "mendeleiev" && !contenu.atomes ? null : x;
  }
  // v34 : les cases Chrono du premier tour (plateau.json regles.chrono.cases), hors des cases elles-mêmes.
  function chronoDeBase(contenu, n) { var R = contenu.plateau.regles.chrono; return R && R.cases && R.cases.indexOf(n) >= 0 ? { type: "chrono" } : null; }
  // v7 : ennemis du plateau (case → id), posés au début de chaque tour.
  function ennemisPlateau(contenu, partie) {
    var pl = partie.plateau;
    if (!contenu.placement) return {};
    if (!pl.ennemis) pl.ennemis = placerEnnemis(contenu, partie);
    return pl.ennemis;
  }
  // v15 : au premier tour, le placement d'origine. Ensuite, l'IA choisit ses sept ennemis parmi tous (ceux que
  // le joueur n'a jamais affrontés d'abord, puis ceux qui l'ont battu), et les postes glissent de quelques cases.
  function placerEnnemis(contenu, partie) {
    var pl = partie.plateau, base = contenu.placement, tour = pl.tours || 0;
    if (!contenu.plateau) return Object.assign({}, base);
    var pc = pl.parcours;
    // L'ancien premier tour (les 63 cases dans l'ordre) garde le placement d'origine.
    if (!tour && !(pc && pc.cases)) return Object.assign({}, base);
    var graine = (partie.cree || 0) + "|" + tour;
    var postes = Object.keys(base).map(Number).sort(function (a, b) { return a - b; });
    // v21 : le parcours fixe le nombre d'ennemis ; leurs postes se répartissent le long de sa route.
    // v36 : tout se compte en places sur la route, les numéros de case ne disent plus l'ordre.
    var rt = route(contenu, partie), place = {}, surRoute = null;
    rt.forEach(function (n, i) { place[n] = i; });
    if (pc && pc.cases) {
      surRoute = place;
      var nE = pc.ennemis != null ? pc.ennemis : postes.length;
      postes = [];
      for (var q = 0; q < nE; q++) postes.push(rt[Math.round((q + 1) * (rt.length - 1) / (nE + 1))]);
    }
    var bete = partie.bestiaire || {};
    var choisis = contenu.ennemis.filter(function (e) { return e.id !== contenu.reserve; }).map(function (e) {
      var f = bete[e.id], vu = f && (f.victoires || f.defaites);
      return { id: e.id, score: (vu ? 0 : 1000) + (f ? f.defaites * 60 : 0) + hacher(graine + "|" + e.id) % 400 };
    }).sort(function (a, b) { return b.score - a.score; }).slice(0, postes.length).map(function (x) { return x.id; });
    choisis.sort(function (a, b) { return hacher(graine + "|ordre|" + a) - hacher(graine + "|ordre|" + b); });
    var decalage = (tour * 3) % 9 - 4, out = {};
    var libre = function (c) { return c != null && place[c] > 1 && place[c] < rt.length - 1 && !out[c] && !specialDe(contenu, partie, c) && (!surRoute || surRoute[c] != null); };
    var parId = {}; contenu.ennemis.forEach(function (e) { parId[e.id] = e; });
    postes.forEach(function (n, i) {
      // v18 : l'ennemi se poste sur une case de son thème, la plus proche de son poste ; sinon, près du poste.
      var th = themeDe(parId[choisis[i]]), ici = th ? contenu.plateau.cases.filter(function (k) { return k.stat === th && libre(k.n); }) : [];
      if (ici.length) {
        ici.sort(function (a, b) { return Math.abs(place[a.n] - place[n] - decalage) - Math.abs(place[b.n] - place[n] - decalage) || place[a.n] - place[b.n]; });
        out[ici[0].n] = choisis[i]; return;
      }
      var visee = place[n] + decalage;
      for (var d = 0; d < 8; d++) {
        var c = rt[visee + (d % 2 ? -1 : 1) * Math.ceil(d / 2)];
        if (libre(c)) { out[c] = choisis[i]; return; }
      }
    });
    return out;
  }

  // Applique le résultat d'une épreuve au pion. `issue` : {reussi, parfait, chrono, jouer}.
  // `jouer` : l'épreuve a été lancée par le bouton « Jouer », l'IA l'a choisie ; réussie, elle rapporte un bonus.
  function bornesBonusJouer(contenu, partie, t) {
    var B = contenu.plateau.regles.bonus, bMin = B.jouer || 0, bMax = B.jouer_max != null ? B.jouer_max : bMin;
    var fav = faveurIA(contenu, partie, t), furieuse = !!(fav && fav.palier.id === "furieuse");
    return { min: bMin, max: furieuse ? bMin : bMax, furieuse: furieuse };
  }
  // Victor (2026-11-12, « Deux modes au choix ») : en mode Île, il n'y a pas de parcours. Le pion ne bouge plus et les
  // épreuves ne rapportent rien sur le plateau : elles construisent l'île.
  function modeIle(partie) { return !!(partie && partie.mode === "ile"); }
  function jouerPlateau(contenu, partie, epreuve, issue, t) {
    if (modeIle(partie)) return null;
    if (!contenu.plateau) return null;
    var v = valeurEpreuve(contenu, partie, epreuve, t), pl = partie.plateau, c = partie.compteurs;
    // v15 : « avancer d'une seule case » : un pas, sans bonus, pour s'arrêter sur la case suivante et la dévoiler.
    var unPas = issue.reussi && issue.uneCase;
    // v19 : le bonus du bouton Jouer est tiré au hasard, entre bonus.jouer et bonus.jouer_max (0 à 4).
    // v20 : furieuse, l'IA ralentit le jeu : le tirage reste au minimum.
    // Victor (2026-10-31) : réussie, une case ; ratée, le pion reste. Plus de bonus Jouer.
    var bonusJouer = 0;
    var valeur = issue.reussi ? 1 : 0;
    var etapes = [];
    // v11 : l'objet tenu par l'avatar donne parfois un coup de pouce après une épreuve réussie.
    var tenu = issue.reussi && !unPas && partie.avatar && partie.avatar.main && (contenu.objets || []).filter(function (o) { return o.id === partie.avatar.main; })[0];
    if (tenu && tenu.bonus && tenu.bonus.type !== "case" && hacher(String(t) + "|" + tenu.id + "|" + partie.journal.length) % 100 < 100 * ((contenu.cabinet && contenu.cabinet.chance_bonus) || 0)) {
      var bo = tenu.bonus;
      if (bo.type === "butin") partie.butinAssure = true;
      else if (bo.type === "faveur") { var fv = faveurIA(contenu, partie, t); if (fv) partie.faveur = { valeur: Math.min(100, fv.valeur + bo.n), maj: t }; }
      etapes.push({ type: "bonus_objet", objet: tenu.id, bonus: bo.type, n: bo.n || 0 });
    }
    if (pl.prison > 0 && issue.parfait) {
      pl.prison--;
      etapes.push({ type: pl.prison ? "prison_reste" : "prison_liberation" });
      if (!pl.prison) c.sortiesPrison++;
    }
    pl.coups = (pl.coups || 0) + 1;
    var dep = deplacer(contenu, partie, valeur, t, epreuve.type);
    dep.etapes = etapes.concat(dep.etapes);
    dep.contextes = contextesPlateau(dep);
    dep.valeurs = v;
    dep.bonusJouer = bonusJouer; dep.jouer = !!(issue.reussi && issue.jouer && !unPas);
    dep.uneCase = !!unPas;
    return dep;
  }

  // La case où le trou de mémoire (ou un ennemi) renvoie le pion. `avant` et le résultat sont des places sur la route du tour.
  // Victor (2026-11-01, carte « Recul fixe ») : depuis qu'on avance case par case, plus aucune case n'est sautée, et
  // « la plus ancienne case jamais dévoilée » n'existait plus. Le trou de mémoire (et l'ennemi qui renvoie) fait
  // désormais reculer le pion de OUBLI_RECUL cases.
  var OUBLI_RECUL = 5;
  function caseOubliee(contenu, partie, avant) {
    route(contenu, partie);
    return avant > 0 ? Math.max(0, avant - OUBLI_RECUL) : null;
  }
  // v15 : la route du tour, de la case départ à l'arrivée. Sans retouche de l'IA, toutes les cases dans l'ordre.
  function route(contenu, partie) {
    var pl = partie.plateau;
    if (!pl.route) {
      // v36 : une partie neuve n'a pas encore de parcours : Alyca dessine le premier, comme les suivants.
      if (!(pl.parcours && pl.parcours.cases)) {
        // Une sauvegarde d'avant v36, au-delà du premier tour, garde toutes les cases dans l'ordre jusqu'au parcours suivant.
        if (!contenu.plateau.parcours || (pl.tours && !pl.redessiner)) {
          var arr = arriveeN(contenu);
          pl.route = contenu.plateau.cases.slice().sort(parDate).map(function (k) { return k.n; }).filter(function (n) { return n !== arr; }).concat([arr]);
          return route(contenu, partie);
        }
        delete pl.redessiner;
        pl.parcours = dessinerParcours(contenu, partie, partie.cree || 0);
        pl.speciaux = Object.assign({}, pl.parcours.speciaux); pl.ennemis = null;
        if (!pl.tours && !pl.coups) {
          var r0 = pl.parcours.cases[0];
          pl.position = r0; pl.idx = 0; pl.visites = {}; pl.visites[r0] = 1; pl.arrets = {}; pl.arrets[r0] = 1;
          pl.anneeMax = anneeDe(contenu, r0);
        }
      }
      pl.route = pl.parcours.cases.slice();
    }
    if (pl.idx == null || pl.route[pl.idx] !== pl.position) {
      pl.idx = pl.route.indexOf(pl.position);
      if (pl.idx < 0) { pl.idx = 0; pl.position = pl.route[0]; }
    }
    return pl.route;
  }
  // Place, derrière `ici`, où renvoie une téléportation vers la case `vers` (à défaut, la dernière case plus ancienne).
  // v36 : si la case visée n'est pas sur la route du tour, la dernière case qui ne lui est pas postérieure.
  function placeVers(contenu, rt, ici, vers) {
    for (var j = ici - 1; j >= 0; j--) if (rt[j] === vers) return j;
    var a = anneeDe(contenu, vers);
    for (j = ici - 1; j >= 0; j--) if (a == null || anneeDe(contenu, rt[j]) <= a) return j;
    return 0;
  }
  // Les cases de la route entre les places ici + a et ici + b (sans l'arrivée).
  function devantPion(contenu, partie, a, b) {
    var rt = route(contenu, partie), i = partie.plateau.idx, out = [];
    for (var j = i + a; j <= Math.min(i + b, rt.length - 2); j++) out.push(rt[j]);
    return out;
  }
  // v15 : exceptionnellement (une fois sur douze, au plus une fois par tour), l'IA retouche la route :
  // après un quiz parfait, elle retire une ou deux cases ordinaires devant le pion ; après un échec,
  // elle remet juste devant lui une ou deux cases qu'il a survolées sans s'y arrêter.
  var REMANIE_CHANCE = 12;
  function remanierRoute(contenu, partie, issue, t, alea) {
    var pl = partie.plateau;
    if (!contenu.plateau || pl.remanie === pl.tours || !(issue.parfait || !issue.reussi)) return null;
    if (alea ? alea() >= 1 / REMANIE_CHANCE : hacher(String(t) + "|route|" + partie.journal.length) % REMANIE_CHANCE) return null;
    var rt = route(contenu, partie), i = pl.idx, en = ennemisPlateau(contenu, partie), g = String(t) + "|" + i;
    function ordinaire(n) { return !specialDe(contenu, partie, n) && !en[n]; }
    var nb = 1 + hacher(g + "|nb") % 2, cases = [];
    if (issue.parfait) {
      var places = [];
      for (var j = i + 2; j <= Math.min(i + 9, rt.length - 2); j++) if (ordinaire(rt[j])) places.push(j);
      places.sort(function (a, b) { return hacher(g + "|" + a) - hacher(g + "|" + b); });
      places = places.slice(0, nb).sort(function (a, b) { return b - a; });
      places.forEach(function (j) { cases.unshift(rt[j]); rt.splice(j, 1); });
      if (!cases.length) return null;
      cases.sort(function (a, b) { return a - b; });
      pl.remanie = pl.tours;
      return { type: "raccourci", cases: cases, longueur: rt.length };
    }
    var devant = rt.slice(i + 1), vues = {};
    for (j = 1; j < i; j++) {
      var n = rt[j];
      if (!pl.visites[n] && ordinaire(n) && devant.indexOf(n) < 0 && !vues[n]) { vues[n] = 1; cases.push(n); }
    }
    cases = cases.slice(0, nb);
    if (!cases.length) return null;
    rt.splice.apply(rt, [i + 1, 0].concat(cases));
    pl.remanie = pl.tours;
    return { type: "detour", cases: cases, longueur: rt.length };
  }
  function routeTour(contenu, partie) { return route(contenu, partie); }

  // --- Parcours (v21) ----------------------------------------------------------
  // Chaque tour bouclé, l'IA dessine le suivant selon son humeur : une forme, une longueur (des époques sautées),
  // et ses ennemis, atomes, pièges et cases cadeau. Le joueur choisit ensuite : refaire un tour, ou (plus tard) le donjon.
  var TYPES_PIEGES = ["recul", "teleport", "oubli", "revision", "quarantaine", "prison", "retour_epoque"];
  function dessinerParcours(contenu, partie, t) {
    var PC = contenu.plateau.parcours, R = contenu.plateau.regles, pl = partie.plateau;
    var fav = faveurIA(contenu, partie, t), palier = fav ? fav.palier.id : "contente", H = PC.humeurs[palier] || PC.humeurs.contente;
    var g = (partie.cree || 0) + "|parcours|" + pl.tours, avant = (pl.parcours && pl.parcours.forme) || "serpentin";
    var formes = PC.formes.filter(function (f) { return f.humeurs.indexOf(palier) >= 0 && f.id !== avant; });
    if (!formes.length) formes = PC.formes.filter(function (f) { return f.id !== avant; });
    // Le premier tour garde le serpentin d'origine.
    var forme = !pl.parcours && !pl.tours ? PC.formes.filter(function (f) { return f.id === "serpentin"; })[0] || formes[0] : formes[tirage(g + "|forme", formes.length)];
    var longueur = casesParTour(contenu, partie);
    var base = function (n) { return (caseN(contenu, n) || {}).special || chronoDeBase(contenu, n); };
    var melange = function (l, cle) { return l.slice().sort(function (a, b) { return hacher(g + cle + a) - hacher(g + cle + b); }); };
    // Victor (2026-10-31) : les cases suivent la chronologie, coupées au réglage « Cases par tour ». Plus de case
    // spéciale fixe ni d'ennemi posté : à chaque pas, un événement peut surgir sur la case suivante (tirerEvenement).
    var tr = tranche(contenu, partie, longueur), cases = tr.cases, speciaux = {};
    cases.forEach(function (x) { if (base(x)) speciaux[x] = null; });
    var tours = pl.tours + 1, ennemis = 0, nAtomes = 0, nPieges = 0, nCadeaux = 0, nChrono = 0;
    // Sans le pack ennemis, Alyca ne promet pas d'ennemis sur la route.
    var mots = (PC.mots[palier] || []).filter(function (m) { return contenu.ennemis.length || !m.ennemis; });
    return { tour: tours, forme: forme.id, palier: palier, cases: cases, longueur: cases.length, ennemis: ennemis,
      atomes: nAtomes, pieges: nPieges, cadeaux: nCadeaux, chrono: nChrono, speciaux: speciaux, fin: tr.fin, dernier: tr.dernier, debut: tr.debut, total: tr.total,
      mot: mots.length ? mots[tirage(g + "|mot", mots.length)] : null, dessine: t };
  }
  function appliquerParcours(contenu, partie) {
    var pl = partie.plateau, p = pl.parcoursSuivant; if (!p) return null;
    pl.parcours = p; pl.parcoursSuivant = null;
    pl.route = null; pl.speciaux = Object.assign({}, p.speciaux); pl.ennemis = null;
    pl.idx = 0; pl.position = p.cases[0];
    route(contenu, partie);
    return p;
  }
  // Le choix de fin de tour : « tour » (refaire un tour sur le nouveau parcours) ou « donjon » : un détour par le donjon
  // ouvert (le premier pas fini, sinon le premier) ; le nouveau tour attend le retour, déjà dessiné.
  function choisirSuite(contenu, partie, choix, t) {
    var dj = null;
    if (choix === "donjon") {
      var ouverts = entreesDonjons(contenu, partie);
      if (!ouverts.length) return { ok: false, raison: "ferme" };
      dj = ouverts.filter(function (d) { return !d.fini; })[0] || ouverts[0];
    }
    var p = appliquerParcours(contenu, partie);
    if (!p) return { ok: false, raison: "aucun" };
    partie.maj = t;
    return dj ? { ok: true, parcours: p, donjon: dj.id, sorte: dj.sorte, entree: dj.sorte === "proces" ? entrerProces(contenu, partie, dj.id, t) : entrerDonjon(contenu, partie, dj.id, t) } : { ok: true, parcours: p };
  }
  // --- Donjons (Victor, 2026-10-31) -------------------------------------------
  // Un donjon fait construire une invention, atelier par atelier. Chaque atelier fait d'abord manipuler l'idée d'un
  // inventeur (l'épreuve), puis la vérifie par des questions : un quiz ordinaire si la compétence n'est pas encore
  // maîtrisée, sinon un contrôle de quelques questions qui ne change rien à la progression. Réussi, il pose ses pièces.
  // État : partie.donjons[id] = { poses: { piece: t }, manips: { atelier: t }, bug, bugsChasses, allume, entre }.
  // Un rappel raté met en panne les pièces de sa compétence (déduit, rien à stocker) jusqu'au rappel réussi.
  // --- L'île (Victor, 2026-11-10) -----------------------------------------------
  // L'île est la somme de ce que le joueur sait encore : chaque arbre y a son quartier, chaque compétence maîtrisée y pose
  // une installation précise et utile, et des habitants viennent s'y installer. Rien n'est enregistré : l'état de l'île
  // se déduit des compétences de la partie. Un rappel dû met l'installation en alerte, un rappel très en retard en panne,
  // une compétence perdue la laisse à l'abandon. Sans le pack de jeu « ile » (contenu.ile.regles), il n'y a pas d'île.
  function ilePresente(contenu) { return !!(contenu && contenu.ile && contenu.ile.regles); }
  // « friche » : jamais apprise ; « marche » ; « alerte » : rappel dû ; « panne » : rappel en retard ; « abandon » : perdue.
  function etatInstallation(contenu, partie, id, t) {
    var e = partie.competences[id], R = contenu.ile.regles;
    if (e && e.maitrise) {
      if (e.prochainRappel == null || t < e.prochainRappel) return "marche";
      return joursEntre(e.prochainRappel, t) >= (R.panne_jours || 2) ? "panne" : "alerte";
    }
    return e && e.perdue ? "abandon" : "friche";
  }
  function habitantsDe(contenu, rang, etat) {
    var H = contenu.ile.regles.habitants, plein = H.installation + H.par_rang * rang;
    return etat === "marche" ? plein : etat === "alerte" ? Math.round(plein * H.alerte) : etat === "panne" || etat === "veille" ? Math.round(plein * H.panne) : 0;
  }
  // Les quartiers sont des lieux (port, ville, zones…), pas des matières : chaque compétence pose son installation dans
  // le quartier où elle sert, quel que soit son arbre. Une compétence sans installation écrite pose son emblème dans un
  // quartier tiré de son nom (toujours le même).
  function hacher(s) { var h = 2166136261; for (var i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); } return h >>> 0; }
  function planIle(contenu) {
    if (contenu._planIle) return contenu._planIle;
    var Q = contenu.ile.quartiers || [], connus = {}, ecrites = {}, plan = { parQuartier: {}, quartierDe: {} };
    Q.forEach(function (q) { connus[q.id] = true; plan.parQuartier[q.id] = []; });
    (contenu.ile.installations || []).forEach(function (x) { if (connus[x.quartier]) ecrites[x.comp] = x; });
    // Sans installation écrite, une compétence se pose dans le quartier de son arbre (quartiers[].arbres) : l'électricité
    // à la centrale, la chimie aux fours… Un arbre qu'aucun quartier ne réclame est réparti par hachage.
    var parArbre = {};
    Q.forEach(function (q) { (q.arbres || []).forEach(function (st) { if (!parArbre[st]) parArbre[st] = q.id; }); });
    if (Q.length) contenu.competences.forEach(function (k) {
      var x = ecrites[k.id], q = x ? x.quartier : parArbre[k.stat] || Q[hacher(k.id) % Q.length].id;
      plan.quartierDe[k.id] = q;
      plan.parQuartier[q].push({ comp: k.id, stat: k.stat, rang: k.rang, nom: x ? x.nom : k.nom, usage: x ? x.usage : null, dessin: (x && x.dessin) || k.embleme || null, propre: !!x });
    });
    Q.forEach(function (q) { plan.parQuartier[q.id].sort(function (u, v) { return u.rang - v.rang; }); });
    contenu._planIle = plan;
    return plan;
  }
  // L'année d'une chose datée du Chrono, d'après sa clé (« frise:id », « livre:id », « savant:id », « objet:id »).
  function anneeChrono(contenu, cle) {
    if (!contenu._anneesChrono) {
      var A = contenu._anneesChrono = {};
      (contenu.evenements || []).forEach(function (e) { if (e.annee != null) A["frise:" + e.id] = { annee: e.annee, titre: e.titre }; });
      (contenu.livres || []).forEach(function (l) { if (l.annee != null) A["livre:" + l.id] = { annee: l.annee, titre: l.titre }; });
      (contenu.objets || []).forEach(function (o) { if (o.annee != null) A["objet:" + o.id] = { annee: o.annee, titre: o.nom }; });
      (contenu.avatar && contenu.avatar.savants || []).forEach(function (v) { var a = lireAnnees(v.annees); if (a) A["savant:" + v.id] = { annee: a.debut, titre: v.nom }; });
    }
    return contenu._anneesChrono[cle] || null;
  }
  // Victor (2026-11-10) : le Chrono bâtit les monuments de l'île. Un par époque du plateau : il se dresse quand
  // `regles.monument.dates` choses de cette époque ont été datées juste au moins une fois, et porte leurs noms.
  function monumentsIle(contenu, partie) {
    var L = contenu.ile.monuments || [], ep = contenu.plateau && contenu.plateau.epoques;
    if (!L.length || !ep || !reglesChrono(contenu)) return [];
    var R = contenu.ile.regles.monument || {}, seuil = R.dates || 3, fiches = (partie.siecles && partie.siecles.fiches) || {};
    var par = {};
    Object.keys(fiches).forEach(function (cle) {
      if (!fiches[cle].justes) return;
      var a = anneeChrono(contenu, cle); if (!a) return;
      var e = ep.filter(function (x) { return (x.debut == null || a.annee >= x.debut) && (x.fin == null || a.annee <= x.fin); })[0];
      if (e) (par[e.id] || (par[e.id] = [])).push({ cle: cle, titre: a.titre, annee: a.annee });
    });
    return L.map(function (m) {
      var e = ep.filter(function (x) { return x.id === m.epoque; })[0]; if (!e) return null;
      var dates = (par[m.epoque] || []).sort(function (a, b) { return a.annee - b.annee; });
      return { epoque: m.epoque, nomEpoque: e.nom, quartier: m.quartier, nom: m.nom, usage: m.usage, dates: dates, seuil: seuil, bati: dates.length >= seuil, habitants: R.habitants || 30 };
    }).filter(Boolean);
  }
  // Victor (2026-11-11) : des monuments « à la gloire des sciences ». Quand on joue `regles.gloire.jours` jours d'affilée,
  // les habitants en dressent un pour le dernier fait marquant de la période : la dernière compétence acquise (une stèle
  // à sa gloire) ou le dernier échec (une colonne brisée, qu'ils relèvent si le savoir est regagné). Plus la série de
  // jours est longue, plus le monument est grand. partie.gloire = { dernier, serie, serieBati, fait, liste }.
  function reglesGloire(contenu) { return (ilePresente(contenu) && contenu.ile.regles.gloire) || null; }
  function suivreGloire(contenu, partie, id, t, genre, bonnes, total) {
    var R = reglesGloire(contenu); if (!R) return null;
    var G = partie.gloire || (partie.gloire = { dernier: null, serie: 0, serieBati: 0, fait: null, liste: [] });
    var ecart = G.dernier == null ? null : joursEntre(G.dernier, t);
    if (ecart == null || ecart > 1 || ecart < 0) { G.serie = 1; G.serieBati = 0; }
    else if (ecart === 1) G.serie++;
    G.dernier = t;
    if (genre) G.fait = { genre: genre, comp: id, t: t, bonnes: bonnes, total: total };
    if (!G.fait || G.serie - (G.serieBati || 0) < R.jours) return null;
    var f = G.fait, type = f.genre === "acquis" ? "gloire" : "lecon";
    var m = { id: type + ":" + f.comp, type: type, comp: f.comp, t: t, serie: G.serie, genre: f.genre, fait: f.t, bonnes: f.bonnes, total: f.total };
    G.liste = (G.liste || []).filter(function (x) { return x.id !== m.id; });
    // Un vrai monument du monde, s'il en reste un : celui de ce savoir d'abord, sinon un autre du même arbre.
    var pris = {}, cf = contenu.parId[f.comp]; G.liste.forEach(function (x) { if (x.reel) pris[x.reel] = true; });
    var libres = ((contenu.ile.gloires || [])).filter(function (g) { return !pris[g.id] && contenu.parId[g.comp]; });
    var reel = libres.filter(function (g) { return g.comp === f.comp; })[0] || (cf && libres.filter(function (g) { return contenu.parId[g.comp].stat === cf.stat; })[0]);
    if (reel) m.reel = reel.id;
    G.liste.push(m);
    if (G.liste.length > (R.max || 40)) G.liste.splice(0, G.liste.length - (R.max || 40));
    G.serieBati = G.serie; G.fait = null;
    return gloiresIle(contenu, partie).filter(function (x) { return x.id === m.id; })[0] || null;
  }
  function gloiresIle(contenu, partie) {
    var R = reglesGloire(contenu); if (!R || !partie.gloire) return [];
    var plan = planIle(contenu), P2 = R.paliers || [];
    return (partie.gloire.liste || []).map(function (m) {
      var c = contenu.parId[m.comp], q = plan.quartierDe[m.comp]; if (!c || !q) return null;
      var su = estMaitrisee(partie, m.comp), e = partie.competences[m.comp];
      var releve = m.type === "lecon" && su && e && e.maitriseDepuis > m.fait;
      var forme = "stele"; P2.forEach(function (p) { if (m.serie >= p.jours) forme = p.forme; });
      var reel = m.reel ? (contenu.ile.gloires || []).filter(function (g) { return g.id === m.reel; })[0] || null : null;
      return { reel: reel, id: m.id, type: m.type, comp: m.comp, nomComp: c.nom, stat: c.stat, quartier: q, t: m.t, serie: m.serie, genre: m.genre, fait: m.fait, bonnes: m.bonnes, total: m.total,
        forme: forme, releve: releve, actif: m.type === "gloire" ? su : releve, habitants: R.habitants || 10 };
    }).filter(Boolean);
  }
  // Ce qu'un atome capturé apporte à l'île : les chantiers dont il est un matériau.
  function chantiersDe(contenu, partie, z, t) {
    if (!ilePresente(contenu)) return [];
    var out = [];
    ile(contenu, partie, t).quartiers.forEach(function (q) {
      q.options.forEach(function (o) { var m = o.materiaux.filter(function (x) { return x.z === z; })[0]; if (m) out.push({ quartier: q.id, nomQuartier: q.nom, couleur: q.couleur, nom: o.nom, raison: m.raison, ouverte: o.ouverte, pret: o.pret, installations: o.installations, marche: q.marche }); });
    });
    return out;
  }
  // Les atomes que les chantiers attendent encore.
  function materiauxAttendus(contenu, partie) {
    var z = {};
    if (ilePresente(contenu) && contenu.atomes) (contenu.ile.quartiers || []).forEach(function (q) { (q.options || []).forEach(function (o) { (o.materiaux || []).forEach(function (m) { if (!estCapture(partie, m.z)) z[m.z] = true; }); }); });
    return z;
  }
  // Les places : ce que les installations en marche peuvent accueillir. C'est la capacité de charge de l'île.
  function placesIle(contenu, partie, t) {
    if (!ilePresente(contenu)) return null;
    var H = contenu.ile.regles.habitants, total = 0, capacite = 0, plan = planIle(contenu), ouverts = {};
    var oj = partie.ile && partie.ile.jour === cleJour(t) ? partie.ile : null;
    var mons = monumentsIle(contenu, partie), gloires = gloiresIle(contenu, partie), pam = placesAmenagements(contenu, partie);
    var parAges = modeIle(partie) && !!agesPresents(contenu);
    var RQ = contenu.ile.regles.quartier, verrouQ = !!(parAges && RQ && agesIle(contenu, partie).courant >= (RQ.age_min == null ? 2 : RQ.age_min));
    // Victor (2026-11-12) : à partir du village, un aménagement ne se bâtit que dans son quartier (plus de pêcherie au
    // village). Ceux bâtis ailleurs avant cette règle rejoignent le leur, qui s'ouvre sans frais.
    if (verrouQ && partie.ressources && partie.ressources.batis) partie.ressources.batis.forEach(function (b) {
      var am = amenagementDe(contenu, b.id); if (!am || !am.quartier || b.q === am.quartier) return;
      b.q = am.quartier; partie.quartiers = partie.quartiers || {}; if (!partie.quartiers[am.quartier]) partie.quartiers[am.quartier] = t;
    });
    if (verrouQ) pam = placesAmenagements(contenu, partie);
    var rangAge = parAges ? agesIle(contenu, partie).courant : 99;
    var pamHab = 0;
    var quartiers = (contenu.ile.quartiers || []).map(function (q) {
      var hab = 0, cap = 0, marche = 0, posees = 0, ouvert = false;
      // Un quartier vide peut s'ouvrir pour y bâtir : il suffit qu'un aménagement à lui soit à la portée du joueur.
      var voulu = verrouQ && (contenu.ile.amenagements || []).some(function (am) {
        if (am.quartier !== q.id || (am.age || 0) > rangAge) return false;
        var rq = (am.savoirs || []).filter(function (x) { return contenu.parId[x]; });
        return !rq.length || rq.some(function (x) { return estMaitrisee(partie, x); }); });
      var choisi = verrouQ && !!(partie.quartiers || {})[q.id];
      var inst = plan.parQuartier[q.id].map(function (x) {
        var etat = etatInstallation(contenu, partie, x.comp, t);
        // En veille : l'objectif de la veille n'a pas été tenu, l'IA économe a baissé son courant pour la journée.
        if (oj && oj.veille === x.comp && etat === "marche") etat = "veille";
        var h = habitantsDe(contenu, x.rang, etat);
        hab += h; cap += H.installation + H.par_rang * x.rang;
        if (etat === "marche" || etat === "alerte") marche++;
        if (etat !== "friche") posees++;
        if (!(x.stat in ouverts)) ouverts[x.stat] = arbreOuvert(contenu, partie, x.stat);
        if (ouverts[x.stat]) ouvert = true;
        return { comp: x.comp, stat: x.stat, rang: x.rang, nom: x.nom, usage: x.usage, dessin: x.dessin, propre: x.propre, etat: etat, places: h, habitants: h };
      });
      // Les options du quartier s'ouvrent par paliers d'installations qui tournent ; chacune attire du monde.
      // Victor (2026-11-10) : certains chantiers demandent aussi des matériaux, des atomes précis à capturer au jeu
      // de Mendeleïev. Les chantiers s'ouvrent dans l'ordre : pas de bibliothèque avant l'école.
      var precedente = true;
      var options = (q.options || []).map(function (o) {
        var pret = marche >= o.installations;
        var mats = contenu.atomes ? (o.materiaux || []).map(function (m) {
          var e = contenu.atomes.elements.filter(function (x) { return x.z === m.z; })[0];
          return e ? { z: m.z, nom: e.nom, symbole: e.symbole, raison: m.raison || null, capture: estCapture(partie, m.z) } : null;
        }).filter(Boolean) : [];
        var ok = precedente && pret && mats.every(function (m) { return m.capture; });
        precedente = ok;
        if (ok) hab += H.option; cap += H.option;
        return { nom: o.nom, usage: o.usage, installations: o.installations, ouverte: ok, pret: pret, materiaux: mats };
      });
      // Les monuments du quartier : bâtis quand assez de dates de leur époque ont été retrouvées au Chrono.
      var monuments = mons.filter(function (m) { return m.quartier === q.id; });
      monuments.forEach(function (m) { cap += m.habitants; if (m.bati) hab += m.habitants; });
      var gq = gloires.filter(function (m) { return m.quartier === q.id; });
      gq.forEach(function (m) { cap += m.habitants; if (m.actif) hab += m.habitants; });
      // Les habitants ne viennent pas sur un chantier (Victor, 2026-11-10 : « il faut créer un lieu propice pour eux ») :
      // un quartier n'est habitable qu'une fois son premier palier ouvert. Avant, ses installations tournent à vide.
      // Île par âges (2026-11-12) : on s'installe dès qu'un premier savoir y tourne, le campement tient autour du feu.
      var habitable = !options.length || options[0].ouverte || (parAges && marche >= 1);
      // Victor (2026-11-12) : à partir du village, un nouveau quartier ne s'ouvre pas tout seul. Le premier savoir qui
      // s'y pose le laisse « à ouvrir » : une question, ou des crédits (questionQuartier, ouvrirQuartier). Le quartier
      // du feu, lui, est là depuis le campement.
      var aOuvrir = verrouQ && (posees > 0 || voulu) && !(partie.quartiers || {})[q.id] && !inst.some(function (x) { return x.comp === "ile.feu"; });
      if (aOuvrir) habitable = false;
      if (!habitable) { hab = 0; inst.forEach(function (x) { x.places = x.habitants = 0; }); }
      // Les maisons bâties avec les ressources (Victor, 2026-11-12) ajoutent leurs places au quartier qui les accueille.
      var pa = pam.parQuartier[q.id] || 0; if (pa) { cap += pa; if (habitable) { hab += pa; pamHab += pa; } }
      total += hab; capacite += cap;
      // Le lieu grandit par stades (Victor, 2026-11-10 : « d'abord la place du marché du village », pas la ville d'emblée) :
      // son nom est celui du stade atteint, un par option ouverte.
      var stade = options.filter(function (o) { return o.ouverte; }).length, noms = q.stades || [];
      return { gloires: gq, monuments: monuments, habitable: habitable, manque: habitable ? 0 : options[0].installations - marche, id: q.id, stade: stade, nomFinal: q.nom, nom: noms[stade] || q.nom, couleur: q.couleur, description: q.description, centre: !!q.centre, position: q.position || null, decor: q.decor || null, fonde: (posees > 0 || choisi) && !aOuvrir, aOuvrir: aOuvrir, ouvert: ouvert || posees > 0, installations: inst,
        options: options, posees: posees, marche: marche, role: (q.demographie || {}).role || null, places: hab, habitants: hab, capacite: cap };
    });
    // Victor (2026-11-12) : « le jeu n'est pas assez dur, rendre nécessaires les évolutions et les aménagements ».
    // Trois freins à la population, le plus bas l'emporte : ce que les savoirs attirent, les toits (abris, maisons,
    // plus quelques dormeurs à la belle étoile) et ce que l'âge de l'île peut porter (un campement n'est pas une ville).
    var L = parAges && contenu.ile.regles.limites, limites = null;
    if (L) {
      var Gl = agesIle(contenu, partie), ag = Gl.ages[Math.min(Gl.courant, Gl.ages.length - 1)], plafond = ag && ag.plafond != null ? ag.plafond : null;
      // Les parties d'avant cette règle gardent un toit de fortune pour ceux qui étaient déjà là.
      var pp = partie.population;
      if (partie.toitsAcquis == null && pp) partie.toitsAcquis = Math.max(0, pp.e + pp.a + pp.v - (L.toits_base || 0) - pam.total);
      var attire = total - pamHab, toits = (L.toits_base || 0) + pam.total + (partie.toitsAcquis || 0), places = Math.max(0, Math.min(attire, toits, plafond == null ? Infinity : plafond));
      limites = { savoirs: attire, toits: toits, plafond: plafond, places: places, frein: places === attire && attire <= toits ? "savoirs" : places === toits ? "toits" : "plafond" };
      return { quartiers: quartiers, places: places, placesQuartiers: total, limites: limites, habitants: places, capacite: capacite, exil: 0, monuments: mons, gloires: gloires };
    }
    return { quartiers: quartiers, places: total, placesQuartiers: total, limites: null, habitants: total, capacite: capacite, exil: 0, monuments: mons, gloires: gloires };
  }
  // --- La démographie de l'île (Victor, 2026-11-10) -------------------------------
  // « Une matrice de Leslie couplée à une limite de capacité de charge (Verhulst) avec des limites de Lotka-Volterra, le
  // tout lié aux aménagements » ; « un côté fourmilière que l'on regarde vivre » ; « plus on ajoute d'aménagement, moins
  // il y a de risques de décès ». La population est donc un état qui vit, un pas par jour :
  // - Leslie : trois classes d'âge (enfants e, adultes a, anciens v), chacune avec sa survie ; les adultes font les
  //   naissances, les enfants grandissent, les adultes vieillissent ;
  // - Verhulst : les naissances s'éteignent à mesure que l'île approche de ses places (la capacité de charge), et ce
  //   qui dépasse s'en va ;
  // - Lotka-Volterra : les faux savoirs (p) sont le prédateur. Ils égarent des habitants et s'en nourrissent ; l'agora
  //   et le campus les font dépérir, un duel gagné les fait reculer.
  // Chaque quartier règle un coefficient (regles.demographie, quartiers[].demographie {role, demi}) : son niveau vaut
  // x / (1 + x), où x = installations en marche / demi. Tout est entier et tiré du jour : pas de hasard à sauvegarder.
  var ROLES_ILE = ["naissances", "arrivees", "enfants", "adultes", "anciens", "defense"];
  function niveauxIle(contenu, brut) {
    var x = {}; ROLES_ILE.forEach(function (r) { x[r] = 0; });
    brut.quartiers.forEach(function (q) {
      var d = (contenu.ile.quartiers.filter(function (c) { return c.id === q.id; })[0] || {}).demographie;
      if (d && d.role in x && q.habitable) x[d.role] += q.marche / (d.demi || 4);
    });
    var n = {}; ROLES_ILE.forEach(function (r) { n[r] = x[r] / (1 + x[r]); });
    return n;
  }
  // Arrondi entier sans hasard : la partie décimale décide, d'après le jour et l'étiquette, si l'on arrondit au-dessus.
  function arrondiJour(x, graine) {
    if (!(x > 0)) return 0;
    var bas = Math.floor(x); return bas + (hacher(graine) % 1000 < (x - bas) * 1000 ? 1 : 0);
  }
  function retirer(pop, n, graine) {
    // Retire n habitants, à proportion des classes d'âge.
    var N = pop.e + pop.a + pop.v; n = Math.min(n, N); if (n <= 0) return 0;
    var de = Math.min(pop.e, arrondiJour(n * pop.e / N, graine + "e")), dv = Math.min(pop.v, arrondiJour(n * pop.v / N, graine + "v")), da = Math.min(pop.a, n - de - dv);
    pop.e -= de; pop.v -= dv; pop.a -= da;
    var reste = n - de - dv - da; ["a", "v", "e"].forEach(function (c) { var k = Math.min(pop[c], reste); pop[c] -= k; reste -= k; });
    return n;
  }
  function accueillir(pop, n, D) {
    // Ceux qui arrivent : des familles, donc des adultes et quelques enfants.
    var e = Math.floor(n * (D.arrivants_enfants == null ? 0.25 : D.arrivants_enfants)); pop.e += e; pop.a += n - e;
  }
  // Au-delà de ce seuil d'habitants, les faux savoirs trouvent de quoi proliférer : c'est ce que les défenses protègent.
  function seuilParasites(D, niv) { return Math.round((D.parasites.declin + D.parasites.defense * niv.defense) / (D.parasites.gain * D.parasites.prise)); }
  function pasDemographie(D, pop, K, niv, graine, vivres, plus) {
    // vivres : 1 à sa faim, moins quand la nourriture manque, un peu plus dans l'abondance (ressources de l'île).
    // plus : effets des aménagements (santé, attrait) et mortalité de famine (Victor, 2026-11-12 : effondrement possible).
    if (vivres == null) vivres = 1;
    plus = plus || {};
    var J = { naissances: 0, arrivees: 0, enfants: 0, adultes: 0, anciens: 0, egares: 0, departs: 0, famine: 0, cueillette: 0 };
    function mort(c) { return D.mortalite[c] * (1 - D.protection * niv[c]) * (1 - (plus.sante || 0)); }
    if (vivres < 1 && plus.famine) J.famine = retirer(pop, arrondiJour((pop.e + pop.a + pop.v) * plus.famine * (1 - vivres), graine + "fam"), graine + "famr");
    // La faim a emporté les derniers : l'île est vide, personne n'arrive aujourd'hui.
    if (J.famine > 0 && pop.e + pop.a + pop.v === 0) { J.effondre = 1; return J; }
    if (plus.cueillette) { J.cueillette = Math.min(pop.a, arrondiJour(pop.a * plus.cueillette * (1 - (plus.sante || 0)), graine + "cu")); pop.a -= J.cueillette; }
    // Leslie : les décès de chaque classe, puis les passages d'une classe à la suivante.
    var de = Math.min(pop.e, arrondiJour(pop.e * mort("enfants"), graine + "de")), da = Math.min(pop.a, arrondiJour(pop.a * mort("adultes"), graine + "da")), dv = Math.min(pop.v, arrondiJour(pop.v * mort("anciens"), graine + "dv"));
    pop.e -= de; pop.a -= da; pop.v -= dv; J.enfants = de; J.adultes = da; J.anciens = dv;
    var N = pop.e + pop.a + pop.v;
    // Lotka-Volterra : chaque faux savoir égare des habitants à proportion de leur nombre, et s'en nourrit.
    var P = D.parasites, prises = Math.min(Math.floor(N * P.plafond), arrondiJour(P.prise * pop.p * N, graine + "p"));
    J.egares = retirer(pop, prises, graine + "pr");
    pop.p = Math.max(0, pop.p + P.gain * J.egares - (P.declin + P.defense * niv.defense) * pop.p);
    N = pop.e + pop.a + pop.v;
    if (pop.p < 1) pop.p = N > seuilParasites(D, niv) ? 1 : 0;
    var grandis = Math.min(pop.e, arrondiJour(pop.e * D.grandir, graine + "g")), vieillis = Math.min(pop.a, arrondiJour(pop.a * D.vieillir, graine + "h"));
    pop.e -= grandis; pop.a += grandis - vieillis; pop.v += vieillis;
    // Verhulst : les naissances ralentissent à mesure que les places manquent.
    if (K > 0 && N < K) {
      J.naissances = arrondiJour(vivres * (1 + (plus.attrait || 0)) * D.fecondite * (1 + niv.naissances) * pop.a * (1 - N / K), graine + "n"); pop.e += J.naissances;
      N = pop.e + pop.a + pop.v;
      J.arrivees = N === 0 ? Math.min(K, D.pionniers) : Math.min(K - N, arrondiJour(Math.min(1, vivres) * (1 + (plus.attrait || 0)) * (D.arrivees.base + D.arrivees.port * niv.arrivees) * (K - N), graine + "ar"));
      if (J.arrivees > 0) accueillir(pop, J.arrivees, D);
    } else if (N > K) J.departs = retirer(pop, K <= 0 ? N : Math.max(1, arrondiJour(D.departs * (N - K), graine + "dp")), graine + "dpr");
    return J;
  }
  // Fait vivre l'île jusqu'à aujourd'hui : un pas par jour écoulé, plafonné pour ne pas punir une longue absence.
  function vivreIle(contenu, partie, t, brut) {
    var D = contenu.ile.regles.demographie, K = brut.places, pop = partie.population, jour = cleJour(t);
    if (!pop) {
      // Première visite (ou partie d'avant la démographie) : l'île est peuplée comme elle l'était, moins les exilés.
      var n0 = Math.max(0, K - (partie.exil || 0)), e0 = Math.round(n0 * 0.22), v0 = Math.round(n0 * 0.2);
      pop = partie.population = { jour: jour, t: t, e: e0, a: n0 - e0 - v0, v: v0, p: 0, journal: null };
    }
    initRessources(contenu, partie, pop);
    if (pop.jour !== jour) {
      var niv = niveauxIle(contenu, brut), pas = Math.max(1, Math.min(D.rattrapage || 7, joursEntre(pop.t, t)));
      var J = { jours: pas, naissances: 0, arrivees: 0, enfants: 0, adultes: 0, anciens: 0, egares: 0, departs: 0, famine: 0, cueillette: 0, effondre: 0 };
      var S = initRessources(contenu, partie, pop), avant = pop.e + pop.a + pop.v;
      // Les aléas ne frappent que d'un jour sur l'autre : jamais pendant une absence.
      if (S && joursEntre(pop.t, t) === 1) frapperAlea(contenu, partie, t);
      if (joursEntre(pop.t, t) === 1) troublesIle(contenu, partie, pop, t);
      if (S) S.journalJour = { jours: pas, prod: {}, conso: {}, manque: 0, perdu: 0, famine: 0, nature: {} };
      var RR = reglesRessources(contenu) || {};
      for (var i = 0; i < pas; i++) {
        var f = S ? pasRessources(contenu, partie, pop, jour + "|" + i + "|", K) : 1;
        if (S && f < 1) S.journalJour.famine++;
        var ef = (S && S.effets) || {};
        var j = pasDemographie(D, pop, K, niv, jour + "|" + i + "|", f, { sante: ef.sante, attrait: ef.attrait, famine: S ? RR.famine_mort : 0, cueillette: (RR.cueillette_risque || 0) * (ef.cueillette || 0) }); for (var c in j) J[c] += j[c];
      }
      // Effondrement : l'île s'est vidée par la faim. Les aménagements tombent en ruine, sauf le foyer ; les savoirs restent.
      if (S && avant > 0 && J.effondre) {
        var gardes = S.batis.filter(function (b) { return b.id === "foyer"; });
        S.effondrement = { jour: jour, perdus: S.batis.length - gardes.length, habitants: avant };
        S.batis = gardes;
      }
      if (S) { S.journal = S.journalJour; S.journalJour = null; }
      pop.jour = jour; pop.t = t; pop.journal = J;
    }
    return pop;
  }
  function ile(contenu, partie, t) {
    var I = placesIle(contenu, partie, t);
    if (!I) return null;
    if (!contenu.ile.regles.demographie) {
      // Sans règles de démographie (pack d'avant) : les habitants sont les places, moins ceux qu'un piège a fait fuir.
      var ex = Math.min(partie.exil || 0, I.places), part0 = I.places ? (I.places - ex) / I.places : 0, tot = 0;
      I.quartiers.forEach(function (q) { q.installations.forEach(function (x) { x.habitants = Math.round(x.places * part0); }); q.habitants = Math.round(q.places * part0); tot += q.habitants; });
      I.habitants = tot; I.exil = ex; return I;
    }
    var D = contenu.ile.regles.demographie, pop = vivreIle(contenu, partie, t, I), N = pop.e + pop.a + pop.v, part = I.placesQuartiers > 0 ? N / I.placesQuartiers : 0;
    I.quartiers.forEach(function (q) {
      q.installations.forEach(function (x) { x.habitants = Math.round(x.places * part); });
      q.habitants = Math.round(q.places * part);
    });
    var niv = niveauxIle(contenu, I);
    I.habitants = N; I.exil = Math.min(partie.exil || 0, Math.max(0, I.places - N));
    I.ressources = ressourcesIle(contenu, partie, t, I);
    I.ages = agesIle(contenu, partie);
    if (I.ages && I.ages.courant > (partie.ageIle || 0)) partie.ageIle = I.ages.courant;
    I.alea = { annonce: annonceAlea(contenu, partie, t), dernier: (partie.aleas && partie.aleas.dernier) || null };
    I.troubles = partie.troubles && partie.troubles.jour === cleJour(t) ? partie.troubles.faits : [];
    I.population = { enfants: pop.e, adultes: pop.a, anciens: pop.v, parasites: Math.round(pop.p), journal: pop.journal, niveaux: niv, seuilParasites: seuilParasites(D, niv),
      mortalite: { enfants: D.mortalite.enfants * (1 - D.protection * niv.enfants), adultes: D.mortalite.adultes * (1 - D.protection * niv.adultes), anciens: D.mortalite.anciens * (1 - D.protection * niv.anciens) } };
    return I;
  }
  // Un duel gagné contre un faux savoir : ceux de l'île reculent.
  function chasserParasites(contenu, partie) {
    var D = ilePresente(contenu) && contenu.ile.regles.demographie, pop = partie.population;
    if (!D || !pop || pop.p < 1) return 0;
    var avant = Math.round(pop.p); pop.p = Math.max(0, pop.p * D.parasites.duel - 1);
    return avant - Math.round(pop.p);
  }
  // --- Les ressources de l'île (Victor, 2026-11-12) ----------------------------------
  // « Simuler une gestion des ressources (nourriture, matériaux…) : avec les crédits on construit des aménagements
  // (ferme, mine…) et la population y travaille pour continuer à croître. » Chaque jour : les adultes actifs prennent
  // les postes des aménagements (nourriture d'abord), ceux-ci produisent, l'île mange. Quand la nourriture manque, les
  // naissances et les arrivées ralentissent d'autant ; quand les réserves sont pleines, elles s'accélèrent un peu.
  // Les maisons ajoutent des places. Tout est entier et tiré du jour, comme la démographie.
  function reglesRessources(contenu) { return ilePresente(contenu) && contenu.ile.regles.ressources && contenu.ile.amenagements ? contenu.ile.regles.ressources : null; }
  function amenagementDe(contenu, id) { return (contenu.ile.amenagements || []).filter(function (a) { return a.id === id; })[0] || null; }
  function amenagementsBatis(contenu, partie) {
    var n = {}; (contenu.ile.amenagements || []).forEach(function (a) { n[a.id] = 0; });
    ((partie.ressources && partie.ressources.batis) || []).forEach(function (b) { if (b.id in n) n[b.id]++; });
    return n;
  }
  // Ce que l'île mange et produit en un jour, pour une population donnée. Les postes sont pourvus dans l'ordre de la liste.
  function economieJour(contenu, partie, pop, K) {
    var R = reglesRessources(contenu), A = contenu.ile.amenagements, n = amenagementsBatis(contenu, partie);
    var N = pop.e + pop.a + pop.v, libres = Math.floor(pop.a * (R.actifs == null ? 0.6 : R.actifs)), prod = {}, postes = {}, total = 0, pourvus = 0;
    (contenu.ile.ressources || []).forEach(function (r) { prod[r.id] = 0; });
    // Un monde fini (Victor, 2026-11-12) : la forêt et les poissons portent la cueillette ; épuisés, elle s'éteint.
    var S = partie.ressources || {}, nat = S.nature || null, effort = S.effort || {}, reste = {}, pris = {}, vit = 1;
    natureIle(contenu).forEach(function (x) { reste[x.id] = nat ? Math.max(0, nat[x.id] || 0) : Infinity; pris[x.id] = 0; });
    if (nat && natureIle(contenu).length) {
      var pf = R.cueillette_foret == null ? 0.6 : R.cueillette_foret, pp = R.cueillette_poisson == null ? 0.4 : R.cueillette_poisson;
      vit = pf * partNature(contenu, nat, "foret") + pp * partNature(contenu, nat, "poisson");
    }
    // La cueillette, la chasse et la pêche à pied nourrissent une part des places de l'île, sans aménagement.
    // Victor (2026-11-12, « durcir ») : en mode Île, la cueillette nourrit un nombre fixe de bouches, pas une part de l'île.
    var cueilli = (R.cueillette_bouches != null && partie.mode === "ile" ? R.cueillette_bouches : (R.cueillette || 0) * (K || 0)) * (R.mange || 0.1) * vit;
    prod.nourriture = (prod.nourriture || 0) + cueilli;
    // Les bonus (moulin, forge) : chacun sert un nombre d'aménagements, pourvu que ses propres postes le soient.
    var bonus = {};
    A.forEach(function (a) {
      // L'effort réglé par le joueur (0 à 1) : la part des postes de cet aménagement qu'on laisse pourvoir.
      var ef = effort[a.id] == null ? 1 : Math.max(0, Math.min(1, effort[a.id]));
      var places = n[a.id] * (a.ouvriers || 0), voulus = Math.round(places * ef), prisP = Math.min(libres, voulus);
      libres -= prisP; total += places; pourvus += prisP; postes[a.id] = { postes: places, pourvus: prisP, effort: ef };
      if (a.bonus && n[a.id]) { var actifs = a.ouvriers ? prisP / a.ouvriers : n[a.id]; a.bonus.cibles.forEach(function (c) { bonus[c] = bonus[c] || []; bonus[c].push({ part: a.bonus.part, sert: actifs * (a.bonus.sert || 99) }); }); }
    });
    A.forEach(function (a) {
      if (!a.produit) return;
      var p = postes[a.id], q = p.pourvus;
      Object.keys(a.produit).forEach(function (r) {
        var base = q * a.produit[r], plus = 0;
        (bonus[a.id] || []).forEach(function (b) { plus += base * b.part * Math.min(1, n[a.id] ? b.sert / n[a.id] : 0); });
        var sorti = base + plus;
        // Ce que l'aménagement puise dans la nature ne peut pas dépasser ce qu'il en reste.
        if (a.preleve && a.preleve in reste) { sorti = Math.min(sorti, reste[a.preleve]); reste[a.preleve] -= sorti; pris[a.preleve] += sorti; }
        prod[r] = (prod[r] || 0) + sorti;
      });
    });
    var conso = { nourriture: N * (R.mange || 0.1) };
    // Santé (hutte du soigneur), attrait (place, veillée), repousse (réserve de pêche), guet : effets des aménagements bâtis.
    var eff = { sante: 0, attrait: 0, guet: 0, visiteurs: 0, repousse: {} };
    // Victor (2026-11-12) : la cueillette est risquée (chutes, bêtes, baies). Plus l'île en dépend pour manger, plus
    // elle y perd d'adultes ; les fermes et les pêcheries font baisser cette part.
    eff.cueillette = partie.mode === "ile" && R.cueillette_risque && prod.nourriture > 0 ? Math.min(1, cueilli / Math.max(prod.nourriture, conso.nourriture)) : 0;
    A.forEach(function (a) {
      if (!n[a.id]) return;
      var marche = a.ouvriers ? postes[a.id].pourvus / a.ouvriers : n[a.id];
      if (a.sante) eff.sante += a.sante * marche; if (a.attrait) eff.attrait += a.attrait * marche; if (a.guet) eff.guet += a.guet * marche;
      if (a.visiteurs) eff.visiteurs += a.visiteurs * n[a.id];
      Object.keys(a.repousse || {}).forEach(function (x) { eff.repousse[x] = (eff.repousse[x] || 0) + a.repousse[x] * marche; });
    });
    eff.sante = Math.min(0.6, eff.sante); eff.attrait = Math.min(1, eff.attrait); eff.guet = Math.min(0.45, eff.guet);
    return { prod: prod, conso: conso, postes: postes, total: total, pourvus: pourvus, actifs: Math.floor(pop.a * (R.actifs == null ? 0.6 : R.actifs)), pris: pris, effets: eff, vitalite: vit };
  }
  function capaciteGrenier(contenu, partie) {
    var R = reglesRessources(contenu), n = amenagementsBatis(contenu, partie), cap = R.grenier || 100;
    (contenu.ile.amenagements || []).forEach(function (a) { if (a.stock) cap += n[a.id] * a.stock; });
    return cap;
  }
  // Un jour de travail : renvoie le facteur qui règle naissances et arrivées (0 = famine, 1 = à sa faim, plus = abondance).
  function pasRessources(contenu, partie, pop, graine, K) {
    var R = reglesRessources(contenu), S = partie.ressources, E = economieJour(contenu, partie, pop, K), J = S.journalJour;
    Object.keys(E.prod).forEach(function (r) {
      var v = arrondiJour(E.prod[r], graine + "r" + r);
      S.stocks[r] = (S.stocks[r] || 0) + v; J.prod[r] = (J.prod[r] || 0) + v;
    });
    var faim = arrondiJour(E.conso.nourriture, graine + "mange"), dispo = S.stocks.nourriture || 0, manges = Math.min(dispo, faim);
    S.stocks.nourriture = dispo - manges; J.conso.nourriture = (J.conso.nourriture || 0) + manges; J.manque += faim - manges;
    var cap = capaciteGrenier(contenu, partie);
    if (S.stocks.nourriture > cap) { J.perdu += S.stocks.nourriture - cap; S.stocks.nourriture = cap; }
    var f = faim > 0 ? manges / faim : 1;
    // Peu d'habitants : la ration du jour s'arrondit parfois à zéro. Sans rien dans les greniers, c'est tout de même la faim.
    if (faim === 0 && E.conso.nourriture > 0 && dispo <= 0) f = 0;
    if (f >= 1 && faim > 0 && S.stocks.nourriture >= faim * (R.abondance_jours || 7)) f = 1 + (R.abondance || 0.25);
    // La nature : ce qu'on y a pris en sort, puis elle repousse (Verhulst : au mieux à mi-hauteur, nulle à zéro, avec
    // un mince retour venu d'ailleurs pour qu'une ressource rasée finisse par revenir).
    if (S.nature) natureIle(contenu).forEach(function (x) {
      var st = Math.max(0, (S.nature[x.id] || 0) - (E.pris[x.id] || 0));
      var r = x.repousse * (1 + (E.effets.repousse[x.id] || 0)), pousse = r * st * (1 - st / x.max) + (st < x.max ? (x.retour || 0) : 0);
      S.nature[x.id] = Math.min(x.max, st + pousse);
      if (J.nature) { var jn = J.nature[x.id] = J.nature[x.id] || { pris: 0, pousse: 0 }; jn.pris += E.pris[x.id] || 0; jn.pousse += pousse; }
    });
    S.effets = E.effets;
    return f;
  }
  function initRessources(contenu, partie, pop) {
    var R = reglesRessources(contenu); if (!R) return null;
    if (!partie.ressources) {
      // Au premier jour, les greniers ont de quoi tenir quelques jours : le temps de bâtir une ferme.
      var N = pop ? pop.e + pop.a + pop.v : 0, st = {};
      (contenu.ile.ressources || []).forEach(function (r) { st[r.id] = 0; });
      st.nourriture = Math.round(N * (R.mange || 0.1) * (R.reserve_jours || 10));
      Object.keys(R.depart || {}).forEach(function (r) { st[r] = (st[r] || 0) + R.depart[r]; });
      partie.ressources = { stocks: st, batis: [], journal: null, journalJour: null };
    }
    var S0 = partie.ressources;
    if (!S0.nature && natureIle(contenu).length) { S0.nature = {}; natureIle(contenu).forEach(function (x) { S0.nature[x.id] = x.depart; }); }
    if (!S0.effort) S0.effort = {};
    return partie.ressources;
  }
  // Construire un aménagement : crédits et matériaux. Il se pose dans son quartier s'il est habitable, sinon dans le
  // quartier habitable le plus peuplé ; il faut au moins un quartier habitable, et parfois un savoir maîtrisé.
  function etatAmenagement(contenu, partie, id, t) {
    var a = amenagementDe(contenu, id), S = partie.ressources, I = ile(contenu, partie, t);
    if (!a || !S || !I) return null;
    var manque = [];
    Object.keys(a.cout || {}).forEach(function (r) {
      var a2 = r === "credits" ? partie.credits.solde : (S.stocks[r] || 0);
      if (a2 < a.cout[r]) manque.push({ r: r, il_faut: a.cout[r], a: a2 });
    });
    // Il faut maîtriser l'un des savoirs de l'aménagement (ceux que le contenu connaît) ; on nomme le premier qui manque.
    var requis = (a.savoirs || (a.savoir ? [a.savoir] : [])).filter(function (x) { return contenu.parId[x]; });
    var savoir = requis.length && !requis.some(function (x) { return estMaitrisee(partie, x); }) ? requis[0] : null;
    var habitables = I.quartiers.filter(function (q) { return q.habitable && q.posees > 0; });
    var ici = habitables.filter(function (q) { return q.id === a.quartier; })[0] || habitables.sort(function (x, y) { return y.habitants - x.habitants; })[0] || null;
    // À partir du village, chaque aménagement a son quartier : il faut l'avoir ouvert (Victor, 2026-11-12).
    var RQ = contenu.ile.regles.quartier, strict = partie.mode === "ile" && RQ && agesPresents(contenu) && agesIle(contenu, partie).courant >= (RQ.age_min == null ? 2 : RQ.age_min), ferme = null;
    if (strict && a.quartier) { var qa = I.quartiers.filter(function (q) { return q.id === a.quartier; })[0]; ici = qa && qa.fonde ? qa : null; if (!ici && qa) ferme = { id: qa.id, aOuvrir: !!qa.aOuvrir }; }
    // Victor (2026-11-12) : le campement ne bâtit rien de durable ; fermes, maisons et ateliers attendent le village.
    var G = partie.mode === "ile" ? agesIle(contenu, partie) : null, age = G && a.age && G.courant < a.age ? a.age : null;
    return { id: id, possible: !manque.length && !savoir && !!ici && age == null, age: age, manque: manque, savoir: savoir, savoirs: savoir ? requis : [], quartier: ici ? ici.id : null, ferme: ferme, chezSoi: !!(ici && ici.id === a.quartier) };
  }
  function construireIle(contenu, partie, id, t) {
    if (!reglesRessources(contenu)) return null;
    ile(contenu, partie, t);
    var e = etatAmenagement(contenu, partie, id, t); if (!e || !e.possible) return e;
    var a = amenagementDe(contenu, id), S = partie.ressources;
    Object.keys(a.cout || {}).forEach(function (r) { if (r === "credits") partie.credits.solde -= a.cout[r]; else S.stocks[r] -= a.cout[r]; });
    S.batis.push({ id: id, q: e.quartier, t: t });
    partie.maj = t;
    return { ok: true, id: id, quartier: e.quartier, n: amenagementsBatis(contenu, partie)[id] };
  }
  // Le tableau des ressources pour l'écran : stocks, ce que rapporte et coûte une journée, postes, aménagements bâtis.
  function ressourcesIle(contenu, partie, t, I) {
    var R = reglesRessources(contenu); if (!R || !partie.population) return null;
    var S = initRessources(contenu, partie, partie.population), pop = partie.population, E = economieJour(contenu, partie, pop, I.places), n = amenagementsBatis(contenu, partie);
    var parQ = {}; S.batis.forEach(function (b) { (parQ[b.q] = parQ[b.q] || {})[b.id] = (parQ[b.q][b.id] || 0) + 1; });
    var faim = E.conso.nourriture, net = (E.prod.nourriture || 0) - faim;
    return { stocks: S.stocks, prod: E.prod, conso: E.conso, postes: E.postes, actifs: E.actifs, total: E.total, pourvus: E.pourvus, batis: n, parQuartier: parQ, grenier: capaciteGrenier(contenu, partie),
      journal: S.journal, net: net, jours: net < 0 ? Math.floor((S.stocks.nourriture || 0) / -net) : null, famine: net < 0 && !(S.stocks.nourriture > 0), places: placesAmenagements(contenu, partie),
      effets: E.effets, effort: S.effort || {}, effondrement: S.effondrement || null, nature: etatNature(contenu, partie, E) };
  }
  function placesAmenagements(contenu, partie) {
    var out = { total: 0, parQuartier: {} };
    if (!reglesRessources(contenu) || !partie.ressources) return out;
    partie.ressources.batis.forEach(function (b) { var a = amenagementDe(contenu, b.id); if (a && a.places) { out.total += a.places; out.parQuartier[b.q] = (out.parQuartier[b.q] || 0) + a.places; } });
    return out;
  }

  // --- Les âges de l'île (Victor, 2026-11-12) ------------------------------------------
  // « La première compétence, c'est la maîtrise du feu » ; puis des âges (campement, village, cité…) qui posent des
  // besoins. Un besoin est couvert dès qu'un de ses savoirs est maîtrisé ; tous couverts, l'âge suivant s'ouvre, avec
  // le rang suivant des arbres. En mode Île, un savoir n'est proposé que si un besoin d'un âge ouvert le demande.
  function agesPresents(contenu) { return ilePresente(contenu) && contenu.ile.ages && contenu.ile.ages.length ? contenu.ile.ages : null; }
  function ageDuSavoir(contenu, id) {
    if (!contenu._ageDe) {
      var m = contenu._ageDe = {};
      (agesPresents(contenu) || []).forEach(function (a, i) { (a.besoins || []).forEach(function (b) { (b.savoirs || []).forEach(function (x) { if (!(x in m)) m[x] = i; }); }); });
    }
    return id in contenu._ageDe ? contenu._ageDe[id] : null;
  }
  function agesIle(contenu, partie) {
    var A = agesPresents(contenu); if (!A) return null;
    var courant = 0, ouvert = true, amen = contenu.ile.amenagements || [];
    var ages = A.map(function (a, i) {
      var besoins = (a.besoins || []).map(function (b) {
        var savoirs = (b.savoirs || []).filter(function (id) { return contenu.parId[id]; });
        var acquis = savoirs.filter(function (id) { return estMaitrisee(partie, id); });
        // Ce que le besoin débloque : les aménagements qui demandent l'un de ses savoirs.
        var ouvre = amen.filter(function (x) { return (x.age || 0) <= a.rang && (x.savoirs || (x.savoir ? [x.savoir] : [])).some(function (s) { return savoirs.indexOf(s) >= 0; }); }).map(function (x) { return x.id; });
        return { id: b.id, nom: b.nom, texte: b.texte || null, savoirs: savoirs, acquis: acquis, couvert: acquis.length > 0 || !savoirs.length, amenagements: ouvre, optionnel: !!b.optionnel, risque: b.risque || null, alerte: b.alerte || null };
      });
      // Victor (2026-11-12) : un besoin optionnel ne bloque pas l'âge suivant. Mais on le propose avant de passer : tant
      // qu'il en reste un, le passage attend la décision du joueur (passerAge), et le négliger a un prix (troublesIle).
      var requis = besoins.filter(function (b) { return !b.optionnel; }), negliges = besoins.filter(function (b) { return b.optionnel && !b.couvert; });
      var avenir = !besoins.length, tenu = !avenir && requis.every(function (b) { return b.couvert; });
      // Victor (2026-11-13) : une épreuve unique peut garder la porte de l'âge suivant (« Faire du feu » avant le
      // campement). Une partie qui a déjà dépassé cet âge ne la doit pas.
      var ep = a.epreuve && !(partie.epreuves || {})[a.epreuve] && !((partie.ageIle || 0) > i) ? a.epreuve : null;
      var complet = tenu && !ep && (!negliges.length || !!(partie.agesPasses || {})[a.id]);
      if (ouvert) courant = i;
      var o = { id: a.id, epreuve: tenu ? ep : null, rang: a.rang, plafond: a.plafond == null ? null : a.plafond, nom: a.nom, description: a.description || null, besoins: besoins, requis: requis.length, couverts: requis.filter(function (b) { return b.couvert; }).length, complet: complet, pret: tenu && !complet && !ep, negliges: negliges, avenir: avenir, ouvert: ouvert };
      ouvert = ouvert && complet;
      return o;
    });
    // Un âge atteint le reste : un savoir perdu laisse un besoin à rétablir, il ne referme pas l'âge.
    courant = Math.max(courant, Math.min(partie.ageIle || 0, ages.length - 1));
    ages.forEach(function (a, i) { a.ouvert = i <= courant; });
    return { ages: ages, courant: courant, age: ages[courant], suivant: ages[courant + 1] || null };
  }
  // Passer à l'âge suivant en laissant des besoins optionnels de côté : le choix du joueur, une fois pour toutes.
  function passerAge(contenu, partie, t) {
    var G = agesIle(contenu, partie); if (!G || !G.age.pret) return null;
    partie.agesPasses = partie.agesPasses || {}; partie.agesPasses[G.age.id] = t; partie.maj = t;
    return agesIle(contenu, partie);
  }
  // Les épreuves uniques de l'île : jouées une fois, elles ouvrent une porte (partie.epreuves[id] = date). Rejouables
  // pour le plaisir, sans rien changer.
  function epreuveIle(contenu, id) { return ((contenu.ile || {}).epreuves || []).filter(function (e) { return e.id === id; })[0] || null; }
  // La quête d'une épreuve : des objets à ramasser sur la carte avant de pouvoir la jouer (partie.quetes[id][objet] = date).
  function queteIle(contenu, partie, id) {
    var e = epreuveIle(contenu, id), q = e && e.quete; if (!q) return null;
    var pris = (partie.quetes || {})[id] || {};
    var objets = q.objets.map(function (o) { return { id: o.id, nom: o.nom, trouve: o.trouve || null, position: o.position, pris: !!pris[o.id] }; });
    var reste = objets.filter(function (o) { return !o.pris; }).length;
    return { id: id, nom: q.nom, texte: q.texte, objets: objets, reste: reste, complete: reste === 0 };
  }
  function ramasserIle(contenu, partie, id, objet, t) {
    var q = queteIle(contenu, partie, id), o = q && q.objets.filter(function (x) { return x.id === objet; })[0];
    if (!o || o.pris) return null;
    partie.quetes = partie.quetes || {}; partie.quetes[id] = partie.quetes[id] || {}; partie.quetes[id][objet] = t; partie.maj = t;
    return { objet: o, quete: queteIle(contenu, partie, id) };
  }
  function epreuveFaite(partie, id) { return !!(partie.epreuves || {})[id]; }
  function reussirEpreuve(contenu, partie, id, t) {
    if (!epreuveIle(contenu, id)) return null;
    partie.epreuves = partie.epreuves || {};
    var premiere = !partie.epreuves[id]; if (premiere) { partie.epreuves[id] = t; partie.maj = t; }
    return { premiere: premiere, ages: agesIle(contenu, partie) };
  }
  // Les besoins optionnels négligés d'un âge déjà passé : chaque jour, une chance d'oubli (le rappel d'un savoir
  // maîtrisé devient dû tout de suite) ou d'émeute (une part des habitants y laisse la vie). Jamais pendant une absence.
  function troublesIle(contenu, partie, pop, t) {
    var R = contenu.ile.regles.troubles, G = R && modeIle(partie) && agesIle(contenu, partie); if (!G) return null;
    var cle = cleJour(t), out = [], de = function (x) { return hacher(x + "|" + cle + "|" + (partie.cree || 0)) / 4294967296; };
    G.ages.forEach(function (a, i) {
      if (i >= G.courant) return;
      a.negliges.forEach(function (b) {
        if (b.risque === "oubli" && de("oubli" + b.id) < (R.oubli || 0)) {
          var ids = Object.keys(partie.competences).filter(function (k) { var e = partie.competences[k]; return e && e.maitrise && contenu.parId[k] && e.prochainRappel > t; }).sort();
          if (ids.length) { var k = ids[hacher("oublie|" + cle) % ids.length]; partie.competences[k].prochainRappel = t; out.push({ type: "oubli", besoin: b.id, comp: k }); }
        }
        if (b.risque === "troubles" && de("emeute" + b.id) < (R.emeute || 0)) {
          var N = pop.e + pop.a + pop.v, n = Math.min(N, Math.max(R.min || 0, Math.round(N * (R.part || 0))));
          if (n > 0) { retirer(pop, n, cle + "|emeute"); out.push({ type: hacher("putsch|" + cle) % 3 ? "emeute" : "putsch", besoin: b.id, morts: n }); }
        }
      });
    });
    if (out.length) partie.troubles = { jour: cle, faits: out };
    return out;
  }
  function savoirOuvertIle(contenu, partie, id) {
    var i = ageDuSavoir(contenu, id); if (i == null) return false;
    return i <= agesIle(contenu, partie).courant;
  }
  // L'épreuve que l'île propose : un rappel dû d'abord, sinon le premier savoir libre d'un besoin encore à couvrir.
  function choixIle(contenu, partie, t) {
    var dus = rappelsDus(contenu, partie, t);
    if (dus.length) return { comp: dus[0], type: "rappel", raison: "rappel", stat: null, kase: null };
    var G = agesIle(contenu, partie), trouve = null;
    G.ages.forEach(function (a) {
      if (!a.ouvert || trouve) return;
      a.besoins.forEach(function (b) {
        if (trouve || b.couvert) return;
        var id = b.savoirs.filter(function (x) { return statut(contenu, partie, x, t).etat === "disponible"; })[0];
        if (id) trouve = { comp: contenu.parId[id], type: "quiz", raison: "besoin", besoin: b.id, stat: contenu.parId[id].stat, kase: null };
      });
    });
    if (trouve) return trouve;
    var dispo = disponibles(contenu, partie, t);
    return dispo.length ? { comp: dispo[0], type: "quiz", raison: "libre", stat: dispo[0].stat, kase: null } : null;
  }
  // --- Un monde fini (Victor, 2026-11-12) ----------------------------------------------
  // « L'île comprend des ressources : arbres, poisson, pétrole, métaux. Elles ne sont pas illimitées. » La forêt et les
  // poissons se renouvellent si on leur en laisse le temps ; le joueur règle l'effort de chaque aménagement.
  function natureIle(contenu) { return (ilePresente(contenu) && contenu.ile.nature) || []; }
  function partNature(contenu, nat, id) {
    var x = natureIle(contenu).filter(function (n) { return n.id === id; })[0];
    return x ? Math.max(0, Math.min(1, (nat[id] || 0) / x.max)) : 1;
  }
  function etatNature(contenu, partie, E) {
    var S = partie.ressources; if (!S || !S.nature) return [];
    return natureIle(contenu).map(function (x) {
      var st = S.nature[x.id] || 0, pris = E.pris[x.id] || 0, apres = Math.max(0, st - pris);
      var r = x.repousse * (1 + (E.effets.repousse[x.id] || 0)), pousse = r * apres * (1 - apres / x.max) + (apres < x.max ? (x.retour || 0) : 0);
      var net = pousse - pris;
      // Le plus qu'on puisse prendre chaque jour sans fin : la repousse à mi-hauteur. Au-delà, le stock finira par tomber.
      var durable = r * x.max / 4 + (x.retour || 0), soutenable = pris <= durable + 1e-9;
      return { id: x.id, nom: x.nom, usage: x.usage || null, icone: x.icone || "", couleur: x.couleur || null, stock: st, max: x.max, part: st / x.max, pris: pris, pousse: pousse, net: net,
        durable: durable, soutenable: soutenable, jours: soutenable ? null : Math.floor(st / (pris - durable)),
        etat: st <= 0 ? "epuise" : st / x.max < 0.25 ? "rouge" : !soutenable ? "orange" : "vert", chantier: etatChantier(contenu, partie, x) };
    });
  }
  // Régler l'effort d'un aménagement (0 à 1) : moins de bras, moins de prélèvement.
  // Chantier exceptionnel (Victor, 2026-11-13) : une fois par jour et par ressource naturelle, toute l'île s'y met et
  // prend d'un coup une part du plafond (grande coupe, grande pêche). Le gain est immédiat ; le risque, c'est de vider
  // ce qui restait : une forêt rasée ou des bancs épuisés mettent très longtemps à revenir, et la cueillette en dépend.
  function etatChantier(contenu, partie, x) {
    var S = partie.ressources, c = x.chantier; if (!c || !S || !S.nature) return null;
    var st = Math.max(0, S.nature[x.id] || 0), pris = Math.min(st, Math.round(x.max * c.part)), gain = Math.round(pris * c.rendement);
    var place = c.donne === "nourriture" ? Math.max(0, capaciteGrenier(contenu, partie) - (S.stocks.nourriture || 0)) : Infinity;
    var fait = !!(S.chantiers && partie.population && S.chantiers[x.id] === partie.population.jour);
    return { nom: c.nom, texte: c.texte || null, donne: c.donne, pris: pris, gain: Math.min(gain, Math.floor(place)), perdu: Math.max(0, gain - Math.floor(place)), apres: (st - pris) / x.max, vide: st - pris <= 0, fait: fait, possible: !fait && pris > 0 };
  }
  function chantierExceptionnel(contenu, partie, id, t) {
    if (!reglesRessources(contenu)) return null;
    ile(contenu, partie, t);
    var S = partie.ressources, x = natureIle(contenu).filter(function (n) { return n.id === id; })[0]; if (!S || !S.nature || !x || !x.chantier) return null;
    var jour = cleJour(t); if (S.chantierJour !== jour) { S.chantierJour = jour; S.chantiers = {}; }
    var e = etatChantier(contenu, partie, x); if (!e.possible) return { ok: false, fait: e.fait };
    S.nature[id] = Math.max(0, (S.nature[id] || 0) - e.pris);
    S.stocks[e.donne] = (S.stocks[e.donne] || 0) + e.gain;
    S.chantiers[id] = jour; partie.maj = t;
    return { ok: true, id: id, donne: e.donne, gain: e.gain, pris: e.pris, vide: e.vide, apres: e.apres };
  }
  function reglerEffort(contenu, partie, id, valeur, t) {
    if (!reglesRessources(contenu) || !amenagementDe(contenu, id)) return null;
    ile(contenu, partie, t);
    var S = partie.ressources; if (!S) return null;
    S.effort = S.effort || {}; S.effort[id] = Math.max(0, Math.min(1, Math.round(valeur * 4) / 4));
    partie.maj = t;
    return S.effort[id];
  }
  // --- Les aléas du climat (Victor, 2026-11-12) -----------------------------------------
  // « Des aléas climatiques qui peuvent faire perdre des aménagements », que des savoirs météo permettent d'anticiper.
  // L'aléa d'un jour se tire de la date et de la partie : pas de hasard à sauvegarder. Avec le savoir, une part des
  // aléas est annoncée la veille ; une question du savoir réussie met l'île à l'abri. Sinon un aménagement est perdu.
  function reglesAleas(contenu) { return ilePresente(contenu) && contenu.ile.aleas && contenu.ile.aleas.length && contenu.ile.regles.aleas ? contenu.ile.regles.aleas : null; }
  function aleaDuJour(contenu, partie, cle) {
    var R = reglesAleas(contenu); if (!R) return null;
    var L = contenu.ile.aleas, A = partie.aleas;
    if (A && A.force && A.force.jour === cle) return L.filter(function (x) { return x.id === A.force.id; })[0] || L[0];
    var G = agesIle(contenu, partie);
    if (G && G.courant < (R.age_min || 0)) return null;
    var h = hacher("alea|" + (partie.cree || 0) + "|" + cle);
    if (h % 1000 >= (R.chance || 0) * 1000) return null;
    return L[(h >>> 10) % L.length];
  }
  function savoirAlea(contenu, partie, a, t) {
    return (a.savoirs || []).filter(function (x) { var e = contenu.parId[x] && etatInstallation(contenu, partie, x, t); return e === "marche" || e === "alerte"; })[0] || null;
  }
  function annonceAlea(contenu, partie, t) {
    var R = reglesAleas(contenu); if (!R || !partie.ressources) return null;
    var demain = cleJour(t + JOUR), a = aleaDuJour(contenu, partie, demain); if (!a) return null;
    var sv = savoirAlea(contenu, partie, a, t); if (!sv) return null;
    var A = partie.aleas || {}, force = A.force && A.force.jour === demain, guet = (partie.ressources.effets || {}).guet || 0;
    if (!force && hacher("annonce|" + (partie.cree || 0) + "|" + demain) % 100 >= ((R.fiabilite || 0) + guet) * 100) return null;
    var n = amenagementsBatis(contenu, partie);
    return { id: a.id, nom: a.nom, icone: a.icone || "", texte: a.annonce || null, jour: demain, savoir: sv, cibles: a.cibles.filter(function (c) { return n[c] > 0; }),
      pret: A.pret === demain, essaye: A.essai === demain };
  }
  // La réponse à la question de préparation : une seule tentative par annonce.
  function preparerAlea(contenu, partie, correct, t) {
    var an = annonceAlea(contenu, partie, t); if (!an || an.pret || an.essaye) return null;
    partie.aleas = partie.aleas || {};
    partie.aleas.essai = an.jour; if (correct) partie.aleas.pret = an.jour;
    partie.maj = t;
    return { pret: !!correct, id: an.id };
  }
  function frapperAlea(contenu, partie, t) {
    var cle = cleJour(t), a = aleaDuJour(contenu, partie, cle); if (!a) return null;
    var A = partie.aleas = partie.aleas || {}, S = partie.ressources, out = { jour: cle, id: a.id };
    if (A.pret === cle) out.evite = true;
    else {
      var cibles = S.batis.map(function (b, i) { return a.cibles.indexOf(b.id) >= 0 ? i : -1; }).filter(function (i) { return i >= 0; });
      if (!cibles.length) out.rien = true;
      else { var k = cibles[hacher("cible|" + cle + "|" + (partie.cree || 0)) % cibles.length]; out.perdu = S.batis[k].id; out.quartier = S.batis[k].q; S.batis.splice(k, 1); }
    }
    A.dernier = out; if (A.force && A.force.jour === cle) A.force = null;
    return out;
  }
  // Mode test : annoncer un aléa pour demain.
  function forcerAlea(contenu, partie, id, t) {
    if (!reglesAleas(contenu)) return null;
    partie.aleas = partie.aleas || {}; partie.aleas.force = { jour: cleJour(t + JOUR), id: id }; partie.maj = t;
    return partie.aleas.force;
  }
  // --- Les savants promeneurs (Victor, 2026-11-12) ------------------------------------
  // Les personnages rencontrés se promènent sur l'île ; chacun pose une question de son thème. Juste : des crédits.
  // Une question par savant et par jour ; l'interface choisit qui se promène et quelle question il pose.
  function visitesIle(partie, t) {
    var j = cleJour(t);
    if (!partie.visites || partie.visites.jour !== j) partie.visites = { jour: j, faits: {} };
    return partie.visites;
  }
  function repondreVisiteur(contenu, partie, id, correct, t) {
    if (!ilePresente(contenu)) return null;
    var V = visitesIle(partie, t); if (id in V.faits) return { deja: true };
    var R = contenu.ile.regles.visiteurs || {}, n = correct ? (R.credits || 10) : 0;
    V.faits[id] = !!correct;
    if (n) { partie.credits.solde += n; partie.credits.gagnes += n; }
    partie.maj = t;
    return { credits: n, juste: !!correct };
  }
  // Ouvrir un quartier (Victor, 2026-11-12, carte « Crédits, question en rabais ») : il coûte des crédits ; une bonne
  // réponse à sa question, posée une seule fois et tirée des savoirs qui s'y sont posés, divise le prix.
  function questionQuartier(contenu, partie, id, t) {
    if (!ilePresente(contenu)) return null;
    var q = ile(contenu, partie, t).quartiers.filter(function (x) { return x.id === id; })[0]; if (!q || !q.aOuvrir) return null;
    var R = contenu.ile.regles.quartier || {}, plein = R.credits || 0, essai = (partie.quartiersEssais || {})[id] || null, qs = [];
    var prix = essai === "juste" ? Math.round(plein * (R.rabais == null ? 0.5 : R.rabais)) : plein;
    q.installations.forEach(function (x) { if (x.etat !== "friche") qs = qs.concat(contenu.questionsPar[x.comp] || []); });
    // Quartier encore vide, ouvert pour y bâtir : la question vient des savoirs qui permettent ses aménagements.
    if (!qs.length) (contenu.ile.amenagements || []).forEach(function (am) { if (am.quartier === id) (am.savoirs || []).forEach(function (x) { if (estMaitrisee(partie, x)) qs = qs.concat(contenu.questionsPar[x] || []); }); });
    return { quartier: id, nom: q.nomFinal, couleur: q.couleur, question: !essai && qs.length ? qs[hacher("quartier|" + id) % qs.length] : null, essai: essai, plein: plein, credits: prix, payable: partie.credits.solde >= prix };
  }
  function ouvrirQuartier(contenu, partie, id, moyen, correct, t) {
    var e = questionQuartier(contenu, partie, id, t); if (!e) return null;
    if (moyen === "credits") {
      if (!e.payable) return { ouvert: false, refus: "credits" };
      partie.quartiers = partie.quartiers || {};
      partie.credits.solde -= e.credits; partie.quartiers[id] = t; partie.maj = t;
      return { ouvert: true, credits: e.credits };
    }
    if (!e.question) return { ouvert: false, refus: "deja" };
    partie.quartiersEssais = partie.quartiersEssais || {}; partie.quartiersEssais[id] = correct ? "juste" : "faux"; partie.maj = t;
    return { ouvert: false, juste: !!correct, credits: questionQuartier(contenu, partie, id, t).credits };
  }
  // --- Mode Île (Victor, 2026-11-12) : ce que le plateau faisait surgir, l'île le propose ---------------------
  // Un chantier attend un atome : on part le chercher. L'atome se présente comme un atome sauvage, sans case à rendre.
  function chercherMateriau(contenu, partie, z, t) {
    if (!modeIle(partie) || !contenu.atomes || estCapture(partie, z) || !elementZ(contenu, z)) return null;
    partie.sauvages = (partie.sauvages || []).filter(function (x) { return x.z !== z; });
    partie.sauvages.unshift({ z: z, case: partie.plateau.position, reste: 0, ile: true, t: t });
    partie.maj = t;
    return atomeSauvage(contenu, partie);
  }
  // Des faux savoirs rôdent : un de leurs champions vient se battre, une fois par jour.
  function defiIle(contenu, partie, t) {
    if (!modeIle(partie) || !contenu.ennemis || !contenu.ennemis.length || partie.duel) return null;
    if (partie.defiIle === cleJour(t)) return null;
    var e = contenu.ennemis[hacher(cleJour(t) + "|defi") % contenu.ennemis.length];
    partie.duel = { ennemi: e.id, case: partie.plateau.position, reste: 0, pret: true, depuis: t, ile: true };
    partie.defiIle = cleJour(t); partie.maj = t;
    return partie.duel;
  }
  // Piège déclenché : une part des habitants quitte l'île. Renvoie combien sont partis (0 si l'île est vide).
  function exodeIle(contenu, partie, t) {
    if (!ilePresente(contenu)) return null;
    var R = contenu.ile.regles.piege || {}, I = ile(contenu, partie, t);
    if (I.habitants <= 0) return null;
    var n = Math.min(I.habitants, Math.max(R.min || 5, Math.round(I.habitants * (R.part || 0.2))));
    if (partie.population && contenu.ile.regles.demographie) retirer(partie.population, n, cleJour(t) + "|exode|" + (partie.exil || 0));
    partie.exil = (partie.exil || 0) + n;
    return { partis: n, habitants: ile(contenu, partie, t).habitants, retour: R.retour || 8 };
  }
  function quartierIle(contenu, partie, id, t) {
    var qid = planIle(contenu).quartierDe[id];
    return ile(contenu, partie, t).quartiers.filter(function (x) { return x.id === qid; })[0] || null;
  }
  // L'objectif du jour (Victor, 2026-11-10 : « il faudrait un objectif par jour »). Chaque matin, l'IA économe annonce
  // un délestage pour le soir sur un quartier. L'île ne demande jamais autre chose que le plateau (Victor, 2026-11-10 :
  // une nouvelle partie proposait « machines simples » alors que le pion était sur l'os d'Ishango) : le quartier visé est
  // celui de l'épreuve que le jeu propose, et l'objectif est de la réussir aujourd'hui. Tenu : des crédits, et la veille
  // de la veille est levée. Manqué : le lendemain, la plus belle installation du quartier passe en veille pour la
  // journée (la moitié de ses habitants s'en va), sans rien faire perdre à la compétence.
  function epreuveDuJour(contenu, partie, t) {
    var c = choixIA(contenu, partie, t);
    return c && c.comp && planIle(contenu).quartierDe[c.comp.id] ? { comp: c.comp.id, type: c.type, quartier: planIle(contenu).quartierDe[c.comp.id] } : null;
  }
  function objectifIle(contenu, partie, t) {
    if (!ilePresente(contenu) || !contenu.ile.regles.objectif) return null;
    var jour = cleJour(t), o = partie.ile, R = contenu.ile.regles.objectif;
    if (!o || o.jour !== jour) {
      var veille = null;
      if (o && o.type && !o.fait) {
        var qv = ile(contenu, partie, t).quartiers.filter(function (x) { return x.id === o.cible; })[0];
        var debout = qv ? qv.installations.filter(function (x) { return x.etat === "marche"; }).sort(function (a, b) { return b.rang - a.rang; }) : [];
        if (debout.length) veille = debout[0].comp;
      }
      var ep = epreuveDuJour(contenu, partie, t);
      partie.ile = o = { jour: jour, type: ep ? "epreuve" : null, cible: ep ? ep.quartier : null, fait: false, veille: veille };
    }
    var q = (contenu.ile.quartiers || []).filter(function (x) { return x.id === o.cible; })[0];
    if (!o.type || !q) return { jour: jour, type: null, veille: o.veille, reussi: false };
    var fonde = ile(contenu, partie, t).quartiers.some(function (x) { return x.id === q.id && x.fonde; });
    var vu = ile(contenu, partie, t).quartiers.filter(function (x) { return x.id === q.id; })[0];
    return { jour: jour, type: o.type, quartier: q.id, nom: vu.nom, couleur: q.couleur, fonde: fonde, besoin: 1, fait: o.fait ? 1 : 0, reussi: o.fait, credits: R.credits, veille: o.veille,
      prochain: o.fait ? null : epreuveDuJour(contenu, partie, t) };
  }
  // Une épreuve réussie aujourd'hui tient l'objectif : la prime tombe une fois, la veille est levée.
  function tenirObjectif(contenu, partie, t) {
    var ob = objectifIle(contenu, partie, t), o = partie.ile;
    if (!ob || !ob.type || o.fait) return false;
    o.fait = true; o.veille = null;
    partie.credits.solde += contenu.ile.regles.objectif.credits; partie.credits.gagnes += contenu.ile.regles.objectif.credits;
    return true;
  }
  // Ce qu'une épreuve a changé sur l'île : l'installation de la compétence jouée, les options de son quartier et le
  // nombre d'habitants, avant et après.
  function photoIle(contenu, partie, id, t) {
    if (!ilePresente(contenu) || !contenu.parId[id]) return null;
    var q = quartierIle(contenu, partie, id, t);
    if (!q) return null;
    objectifIle(contenu, partie, t);
    return { posees: q.posees, nom: q.nom, etat: etatInstallation(contenu, partie, id, t), habitants: ile(contenu, partie, t).habitants, places: ile(contenu, partie, t).places, options: q.options.filter(function (o) { return o.ouverte; }).length };
  }
  function changementIle(contenu, partie, id, t, avant, reussi) {
    if (!avant) return null;
    // Une épreuve réussie fait revenir une partie de ceux qu'un piège avait fait fuir.
    var revenus = 0;
    var D = contenu.ile.regles.demographie, pop = partie.population;
    if (reussi && partie.exil > 0) { revenus = Math.min(partie.exil, (contenu.ile.regles.piege || {}).retour || 8); partie.exil -= revenus; if (D && pop) accueillir(pop, revenus, D); }
    var tenu = reussi ? tenirObjectif(contenu, partie, t) : false;
    // Une installation de plus, ce sont des places : une partie se remplit tout de suite, attirée par la nouveauté ; le
    // reste viendra par les naissances et les bateaux, jour après jour.
    var attires = 0;
    if (D && pop && reussi) {
      var libres = placesIle(contenu, partie, t).places - (pop.e + pop.a + pop.v);
      attires = Math.max(0, Math.min(libres, Math.round((placesIle(contenu, partie, t).places - avant.places) * D.attrait)));
      if (attires > 0) accueillir(pop, attires, D);
    }
    // Une installation perdue, ce sont des places en moins : une partie de ceux qui y vivaient s'en va aussitôt.
    if (D && pop && !reussi) {
      var trop = (pop.e + pop.a + pop.v) - placesIle(contenu, partie, t).places;
      if (trop > 0 && placesIle(contenu, partie, t).places < avant.places) retirer(pop, Math.max(1, Math.round(trop * D.attrait)), cleJour(t) + "|perte|" + id);
    }
    var apres = photoIle(contenu, partie, id, t);
    if (!tenu && apres.etat === avant.etat && apres.habitants === avant.habitants) return null;
    var q = quartierIle(contenu, partie, id, t);
    var inst = q.installations.filter(function (x) { return x.comp === id; })[0];
    // L'option que l'épreuve vient d'ouvrir (ou de fermer) dans le quartier.
    var option = apres.options > avant.options ? q.options[apres.options - 1] : apres.options < avant.options ? q.options[avant.options - 1] : null;
    return { comp: id, quartier: q.id, objectif: tenu ? objectifIle(contenu, partie, t) : null, fondation: avant.posees === 0 && q.posees > 0, stadeAvant: avant.nom, option: option, optionOuverte: apres.options > avant.options, installation: inst, avant: avant.etat, apres: apres.etat, habitantsAvant: avant.habitants, revenus: revenus, attires: attires, exil: partie.exil || 0, habitants: apres.habitants };
  }
  function listeDonjons(contenu) { return (contenu.donjons && contenu.donjons.donjons) || []; }
  function donjonDe(contenu, id) { return listeDonjons(contenu).filter(function (d) { return d.id === id; })[0] || null; }
  function compterDonjons(partie, f) {
    var d = partie.donjons || {};
    return Object.keys(d).reduce(function (s, id) { return s + f(d[id]); }, 0);
  }
  // Un arbre réussi : toutes ses compétences maîtrisées en même temps.
  function arbreReussi(contenu, partie, stat) {
    var ks = contenu.parStat[stat] || [];
    return ks.length > 0 && ks.every(function (k) { return estMaitrisee(partie, k.id); });
  }
  // Victor (2026-11-08) : un donjon s'ouvre dès qu'on a réussi la dernière case de chacun de ses arbres (la plus récente de
  // l'arbre sur le plateau, sa compétence acquise, même hors ordre). Sans plateau, l'arbre entier réussi.
  function derniereCase(contenu, stat) {
    var P = contenu.plateau; if (!P || !P.cases) return null;
    var cs = P.cases.filter(function (k) { return k.stat === stat && (P.competences_cases[k.n] || []).length; });
    return cs.length ? cs.sort(parDate)[cs.length - 1] : null;
  }
  function arbreFini(contenu, partie, stat) {
    var k = derniereCase(contenu, stat);
    if (!k) return arbreReussi(contenu, partie, stat);
    return contenu.plateau.competences_cases[k.n].every(function (id) { return estMaitrisee(partie, id); });
  }
  // Ouvert quand ses arbres d'origine sont réussis, ou d'office si la nouvelle partie l'a choisi (réglage de test).
  function donjonOuvert(contenu, partie, id) {
    var dj = donjonDe(contenu, id); if (!dj) return false;
    var choisis = (partie.options && partie.options.donjons) || [];
    if (choisis.indexOf(id) >= 0) return true;
    var arbres = dj.arbres.filter(function (s) { return contenu.parStat[s]; });
    return arbres.length > 0 && arbres.every(function (s) { return arbreFini(contenu, partie, s); });
  }
  function donjonsOuverts(contenu, partie) { return listeDonjons(contenu).filter(function (d) { return donjonOuvert(contenu, partie, d.id); }); }
  function etatDonjon(partie, id) {
    partie.donjons = partie.donjons || {};
    return partie.donjons[id] || (partie.donjons[id] = { poses: {}, manips: {}, bug: null, bugsChasses: 0, allume: null, entre: null });
  }
  function atelierPose(etat, at) { return at.composants.every(function (c) { return etat.poses[c.id] != null; }); }
  // Le premier atelier dont les pièces ne sont pas toutes posées : c'est là qu'on reprend.
  function atelierCourant(contenu, partie, id) {
    var dj = donjonDe(contenu, id); if (!dj) return null;
    var e = etatDonjon(partie, id);
    return dj.ateliers.filter(function (a) { return !atelierPose(e, a); })[0] || null;
  }
  // Pièces en panne : posées, mais une compétence de leur atelier a été perdue à un rappel raté.
  function piecesEnPanne(contenu, partie, id) {
    var dj = donjonDe(contenu, id); if (!dj) return [];
    var e = etatDonjon(partie, id), out = [];
    dj.ateliers.forEach(function (a) {
      if (!atelierPose(e, a)) return;
      var perdues = a.competences.filter(function (c) { var s = partie.competences[c]; return !!(s && s.perdue && !s.maitrise); });
      if (perdues.length) a.composants.forEach(function (c) { out.push({ piece: c, atelier: a, competences: perdues }); });
    });
    return out;
  }
  // Le tableau de bord du donjon : ce que l'interface affiche sur le plan de la machine.
  function bilanDonjon(contenu, partie, id) {
    var dj = donjonDe(contenu, id); if (!dj) return null;
    var e = etatDonjon(partie, id), pannes = piecesEnPanne(contenu, partie, id), enPanne = {};
    pannes.forEach(function (p) { enPanne[p.piece.id] = true; });
    var pieces = [];
    dj.ateliers.forEach(function (a) { a.composants.forEach(function (c) { pieces.push({ id: c.id, piece: c, atelier: a.id, posee: e.poses[c.id] != null, panne: !!enPanne[c.id] }); }); });
    var cour = atelierCourant(contenu, partie, id);
    return { donjon: dj, ouvert: donjonOuvert(contenu, partie, id), pieces: pieces, posees: pieces.filter(function (p) { return p.posee; }).length,
      total: pieces.length, atelier: cour, manipFaite: !!(cour && e.manips[cour.id]), bug: e.bug, pannes: pannes, allume: e.allume,
      pret: !cour && !e.bug && !pannes.length && !e.allume };
  }
  function entrerDonjon(contenu, partie, id, t) {
    if (!donjonOuvert(contenu, partie, id)) return { ok: false, raison: "ferme" };
    var e = etatDonjon(partie, id), premiere = !e.entre;
    if (premiere) e.entre = t;
    partie.maj = t;
    return { ok: true, premiere: premiere, bilan: bilanDonjon(contenu, partie, id) };
  }
  // L'épreuve de l'atelier en cours, tirée parmi ses variantes. Un bug à chasser passe avant tout.
  function epreuveAtelier(contenu, partie, id, alea) {
    if (!donjonOuvert(contenu, partie, id)) return { ok: false, raison: "ferme" };
    var e = etatDonjon(partie, id), a = atelierCourant(contenu, partie, id);
    if (e.bug) return { ok: false, raison: "bug" };
    if (!a) return { ok: false, raison: "fini" };
    var inst = a.epreuve.instances, i = Math.floor((alea || Math.random)() * inst.length);
    return { ok: true, atelier: a, n: i, instance: inst[i], type: a.epreuve.type, epreuve: a.epreuve };
  }
  // Réponses comparées sans tenir compte des espaces, de la casse ni du type (« 32 » vaut 32, [1, 0] vaut ["1", "0"]).
  function memeReponse(a, b) {
    if (Array.isArray(a) || Array.isArray(b)) {
      if (!Array.isArray(a) || !Array.isArray(b) || a.length !== b.length) return false;
      return a.every(function (x, i) { return memeReponse(x, b[i]); });
    }
    if (typeof a === "number" || typeof b === "number") { var x = lireNombre(a), y = lireNombre(b); return !isNaN(x) && !isNaN(y) && Math.abs(x - y) < 1e-9; }
    return String(a).replace(/\s+/g, " ").trim().toLowerCase() === String(b).replace(/\s+/g, " ").trim().toLowerCase();
  }
  function verifierEpreuve(contenu, partie, id, n, reponse, t) {
    var a = atelierCourant(contenu, partie, id); if (!a) return { ok: false, raison: "fini" };
    var inst = a.epreuve.instances[n]; if (!inst) return { ok: false, raison: "instance" };
    var juste = memeReponse(reponse, inst.attendu), e = etatDonjon(partie, id);
    if (juste) e.manips[a.id] = t;
    partie.maj = t;
    return { ok: true, juste: juste, attendu: inst.attendu };
  }
  // Après la manipulation, les questions de l'atelier : « quiz » sur la première compétence pas encore maîtrisée
  // (l'interface lance le quiz ordinaire, puis appelle finirAtelier), sinon « controle » : quelques questions tirées.
  function questionsAtelier(contenu, partie, id, alea) {
    var dj = donjonDe(contenu, id), a = atelierCourant(contenu, partie, id); if (!a) return null;
    var nouvelle = a.competences.filter(function (c) { return contenu.parId[c] && !estMaitrisee(partie, c); })[0];
    if (nouvelle) return { mode: "quiz", competence: nouvelle, atelier: a };
    var qs = [];
    a.competences.forEach(function (c) { qs = qs.concat(tirerQuestions(contenu, partie, c, dj.questions_atelier, alea)); });
    return { mode: "controle", atelier: a, questions: melanger(qs, alea || Math.random).slice(0, dj.questions_atelier), seuil: dj.reussite_atelier };
  }
  // Fin de l'atelier. `resultats` : ceux du contrôle (mode « controle ») ; en mode « quiz », le quiz ordinaire est déjà
  // terminé (terminerQuiz) et l'atelier est réussi si la compétence est désormais maîtrisée.
  function finirAtelier(contenu, partie, id, resultats, t, alea) {
    var dj = donjonDe(contenu, id), e = etatDonjon(partie, id), a = atelierCourant(contenu, partie, id);
    if (!a) return { ok: false, raison: "fini" };
    if (!e.manips[a.id]) return { ok: false, raison: "manipulation" };
    var reussi = resultats ? resultats.filter(function (x) { return x.correct; }).length >= dj.reussite_atelier
      : a.competences.every(function (c) { return !contenu.parId[c] || estMaitrisee(partie, c); });
    partie.maj = t;
    if (!reussi) { delete e.manips[a.id]; return { ok: true, reussi: false, atelier: a, contexte: "atelier_rate" }; }
    a.composants.forEach(function (c) { e.poses[c.id] = t; });
    var suivant = atelierCourant(contenu, partie, id), bug = null;
    // Un bug se glisse parfois entre deux ateliers (jamais après le dernier) ; il faudra le chasser avant de continuer.
    if (suivant && (alea || Math.random)() < dj.bug.chance) {
      var faits = dj.ateliers.filter(function (x) { return atelierPose(e, x); });
      var cible = faits[Math.floor((alea || Math.random)() * faits.length)];
      var nom = Math.floor((alea || Math.random)() * dj.bug.noms.length);
      bug = e.bug = { nom: nom, atelier: cible.id, competences: cible.competences.filter(function (c) { return contenu.parId[c]; }), depuis: t, q: null };
    }
    var nouveaux = verifierSucces(contenu, partie, t);
    return { ok: true, reussi: true, atelier: a, poses: a.composants, suivant: suivant, bug: bug, succes: nouveaux,
      contexte: bug ? "bug" : "atelier_reussi" };
  }
  // Le bug se chasse par une question sur l'atelier qu'il grignote ; la question reste la même jusqu'à la réponse.
  function questionBug(contenu, partie, id, alea) {
    var e = etatDonjon(partie, id), b = e.bug; if (!b) return null;
    if (b.q && contenu.questionParId[b.q]) return contenu.questionParId[b.q];
    var qs = []; b.competences.forEach(function (c) { qs = qs.concat(contenu.questionsPar[c] || []); });
    if (!qs.length) { e.bug = null; return null; }
    var q = qs[Math.floor((alea || Math.random)() * qs.length)];
    b.q = q.id;
    return q;
  }
  function chasserBug(contenu, partie, id, correct, t) {
    var e = etatDonjon(partie, id); if (!e.bug) return { ok: false, raison: "aucun" };
    partie.maj = t;
    if (!correct) { e.bug.q = null; return { ok: true, chasse: false, contexte: "bug_rate" }; }
    e.bug = null; e.bugsChasses = (e.bugsChasses || 0) + 1;
    return { ok: true, chasse: true, contexte: "bug_chasse", succes: verifierSucces(contenu, partie, t) };
  }
  // L'allumage : toutes les pièces posées, aucun bug, aucune panne.
  function allumer(contenu, partie, id, t) {
    var b = bilanDonjon(contenu, partie, id); if (!b) return { ok: false, raison: "inconnu" };
    if (b.allume) return { ok: false, raison: "deja" };
    if (b.atelier) return { ok: false, raison: "pieces" };
    if (b.bug) return { ok: false, raison: "bug" };
    if (b.pannes.length) return { ok: false, raison: "panne", pannes: b.pannes };
    etatDonjon(partie, id).allume = t;
    partie.maj = t;
    return { ok: true, texte: b.donjon.allumage.texte, contexte: "allumage", succes: verifierSucces(contenu, partie, t) };
  }
  // Une réplique d'Alyca, cheffe de chantier, pour un moment du donjon.
  function repliqueDonjon(contenu, id, moment, alea) {
    var dj = donjonDe(contenu, id), l = dj && dj.repliques[moment]; if (!l || !l.length) return null;
    return l[Math.floor((alea || Math.random)() * l.length)];
  }

  // --- Le Procès (Victor, 2026-11-02) : donjon de rhétorique ------------------------------------------------------
  // Huit salles préparent une plaidoirie (choix, tri, ordre, audience) ; chacune rapporte des points. Au bout, le
  // verdict : acquittée si le total atteint le seuil. Perdu, on fait appel : tout recommence, rien n'est retenu contre vous.
  // État : partie.proces[id] = { salle, points: { salle: n }, essais, perdus, acquitte, entre, dernier }.
  function listeProces(contenu) { return (contenu.donjons && contenu.donjons.proces) || []; }
  function procesDe(contenu, id) { return listeProces(contenu).filter(function (d) { return d.id === id; })[0] || null; }
  function procesOuvert(contenu, partie, id) {
    var pr = procesDe(contenu, id); if (!pr) return false;
    if (((partie.options && partie.options.donjons) || []).indexOf(id) >= 0) return true;
    var arbres = pr.arbres.filter(function (s) { return contenu.parStat[s]; });
    return arbres.length > 0 && arbres.every(function (s) { return arbreFini(contenu, partie, s); });
  }
  function etatProces(partie, id) {
    partie.proces = partie.proces || {};
    return partie.proces[id] || (partie.proces[id] = { salle: 0, points: {}, essais: 0, perdus: 0, acquitte: null, entre: null, dernier: null });
  }
  // Procès v2 (Victor, 2026-11-03) : la fin de l'audience reprend la péroraison et la dernière phrase préparées
  // (`reprend`), après celles de l'adversaire ; leurs options y valent `points_audience`.
  function optionsEchange(pr, x) {
    if (!x.reprend) return x.options;
    var s = pr && pr.salles.filter(function (y) { return y.id === x.reprend; })[0];
    return s ? s.options.map(function (o) { return { texte: o.texte, figure: o.figure, points: o.points_audience != null ? o.points_audience : o.points, retour: o.retour_audience || o.retour, plus: o.plus, moins: o.moins }; }) : [];
  }
  // Victor (2026-11-03) : les parties à ranger suivent le type de plan choisi (`selon`, `variantes`).
  function itemsSalle(pr, s, choix) {
    if (!s.selon || !s.variantes) return s.items;
    var i = choix ? choix[s.selon] : null;
    return (i != null && s.variantes[i]) || s.items;
  }
  function maxSalle(s, pr, choix) {
    var meilleur = function (opts) { return Math.max.apply(null, opts.map(function (o) { return o.points; })); };
    if (s.type === "choix") return meilleur(s.options);
    if (s.type === "multi") return s.choisir;
    if (s.type === "ordre") return itemsSalle(pr, s, choix).length;
    return s.echanges.reduce(function (n, e) { return n + meilleur(optionsEchange(pr, e)); }, 0);
  }
  function salleProces(contenu, partie, id) {
    var pr = procesDe(contenu, id); if (!pr) return null;
    return pr.salles[etatProces(partie, id).salle] || null;
  }
  function entrerProces(contenu, partie, id, t) {
    if (!procesOuvert(contenu, partie, id)) return { ok: false, raison: "ferme" };
    var e = etatProces(partie, id), premiere = !e.entre;
    if (premiere) e.entre = t;
    partie.maj = t;
    return { ok: true, premiere: premiere, proces: procesDe(contenu, id), etat: e };
  }
  // `reponse` : un index (choix), des index (multi : autant que `choisir` ; ordre : les items dans l'ordre donné ;
  // audience : une option par échange). Renvoie les points, le maximum et le retour du mentor pour chaque choix.
  function repondreSalle(contenu, partie, id, reponse, t) {
    var s = salleProces(contenu, partie, id); if (!s) return { ok: false, raison: "fini" };
    var pr = procesDe(contenu, id), e0 = etatProces(partie, id), items = s.type === "ordre" ? itemsSalle(pr, s, e0.choix) : null, pts = 0, retours = [], max = maxSalle(s, pr, e0.choix);
    if (s.type === "choix") {
      var o = s.options[reponse]; if (!o) return { ok: false, raison: "reponse" };
      pts = o.points; retours.push(o.retour);
    } else if (s.type === "multi") {
      if (!Array.isArray(reponse) || reponse.length !== s.choisir || reponse.some(function (i, k) { return !s.options[i] || reponse.indexOf(i) !== k; })) return { ok: false, raison: "reponse" };
      reponse.forEach(function (i) { pts += s.options[i].points; retours.push(s.options[i].retour); });
    } else if (s.type === "ordre") {
      if (!Array.isArray(reponse) || reponse.length !== items.length || reponse.slice().sort().join() !== items.map(function (_, i) { return i; }).sort().join()) return { ok: false, raison: "reponse" };
      reponse.forEach(function (i, k) { if (i === k) pts++; });
    } else {
      if (!Array.isArray(reponse) || reponse.length !== s.echanges.length || reponse.some(function (i, k) { return !optionsEchange(pr, s.echanges[k])[i]; })) return { ok: false, raison: "reponse" };
      reponse.forEach(function (i, k) { var x = optionsEchange(pr, s.echanges[k])[i]; pts += x.points; retours.push(x.retour); });
    }
    var e = etatProces(partie, id);
    e.points[s.id] = pts; e.salle++;
    // Les choix gardés : la clôture de l'audience propose d'abord la péroraison et la phrase préparées.
    e.choix = e.choix || {}; e.choix[s.id] = reponse;
    partie.maj = t;
    return { ok: true, salle: s, points: pts, max: max, retours: retours, reponse: reponse, items: items, lecon: s.lecon, suivante: salleProces(contenu, partie, id) };
  }
  function scoreProces(contenu, partie, id) {
    var pr = procesDe(contenu, id), e = etatProces(partie, id), total = 0, max = 0;
    pr.salles.forEach(function (s) { total += e.points[s.id] || 0; max += maxSalle(s, pr, e.choix); });
    return { total: total, max: max, seuil: Math.ceil(pr.seuil * max - 1e-9) };
  }
  // Toutes les salles passées : le jury rend son verdict ; la partie suivante (l'appel) repart de la première salle.
  function verdictProces(contenu, partie, id, t) {
    var pr = procesDe(contenu, id); if (!pr) return { ok: false, raison: "inconnu" };
    var e = etatProces(partie, id);
    if (e.salle < pr.salles.length) return { ok: false, raison: "salles" };
    var sc = scoreProces(contenu, partie, id), acquitte = sc.total >= sc.seuil;
    e.essais++;
    if (acquitte) { if (!e.acquitte) e.acquitte = t; } else e.perdus++;
    var votes = votesJury(pr, e.points, acquitte, e.choix);
    e.dernier = { total: sc.total, max: sc.max, seuil: sc.seuil, acquitte: acquitte, t: t, points: e.points, votes: votes };
    e.salle = 0; e.points = {}; e.choix = {};
    partie.maj = t;
    return { ok: true, acquitte: acquitte, total: sc.total, max: sc.max, seuil: sc.seuil, vrai: pr.vrai, contexte: acquitte ? "acquitte" : "condamne", votes: votes, succes: verifierSucces(contenu, partie, t) };
  }
  // Chaque juré pèse les salles qui comptent pour lui (6 sur 10 suffisent) ; le verdict, lui, suit le total : on fait
  // basculer les jurés les plus proches pour qu'il y ait une majorité (4 sur 6) dans le sens du verdict.
  function votesJury(pr, points, acquitte, choix) {
    var jury = pr.jury || []; if (!jury.length) return [];
    var parId = {}; pr.salles.forEach(function (s) { parId[s.id] = s; });
    var v = jury.map(function (j) {
      var a = 0, m = 0;
      j.salles.forEach(function (sid) { var s = parId[sid]; if (!s) return; a += points[sid] || 0; m += maxSalle(s, pr, choix); });
      var r = m ? a / m : 0;
      return { id: j.id, ratio: r, acquitte: r >= 0.6 };
    });
    var besoin = Math.floor(jury.length / 2) + 1, oui = function () { return v.filter(function (x) { return x.acquitte; }).length; };
    var tri = v.slice().sort(function (a, b) { return acquitte ? b.ratio - a.ratio : a.ratio - b.ratio; });
    tri.forEach(function (x) {
      if (acquitte && oui() < besoin && !x.acquitte) x.acquitte = true;
      if (!acquitte && oui() >= besoin && x.acquitte) x.acquitte = false;
    });
    return v.map(function (x) { return { id: x.id, acquitte: x.acquitte }; });
  }
  function repliqueProces(contenu, id, moment, alea) {
    var pr = procesDe(contenu, id), l = pr && pr.repliques[moment]; if (!l || !l.length) return null;
    return l[Math.floor((alea || Math.random)() * l.length)];
  }
  // Les donjons ouverts, toutes sortes confondues : { sorte: "construction" | "proces", id, nom, fini }.
  function entreesDonjons(contenu, partie) {
    var out = [];
    donjonsOuverts(contenu, partie).forEach(function (d) { out.push({ sorte: "construction", id: d.id, nom: d.nom, fini: !!(partie.donjons && partie.donjons[d.id] && partie.donjons[d.id].allume) }); });
    listeProces(contenu).forEach(function (d) { if (procesOuvert(contenu, partie, d.id)) out.push({ sorte: "proces", id: d.id, nom: d.nom, fini: !!(partie.proces && partie.proces[d.id] && partie.proces[d.id].acquitte) }); });
    return out;
  }
  function formeParcours(contenu, id) { return contenu.plateau && contenu.plateau.parcours ? contenu.plateau.parcours.formes.filter(function (f) { return f.id === id; })[0] || null : null; }
  function caseDecouverte(partie, n) { return toutesCases(partie) || !!(partie.plateau.visites[n] || partie.plateau.position === n); }
  function toutesCases(partie) { return !!(partie.options && partie.options.toutesCases); }
  // Réglage temporaire « Voir toutes les cases » : redessine le tour en cours (toutes les cases dévoilées, ou de nouveau
  // un tirage), le pion garde sa case si elle reste sur la route, sinon il repart de la première.
  function voirToutesCases(contenu, partie, oui) {
    partie.options = partie.options || {}; partie.options.toutesCases = !!oui;
    var pl = partie.plateau; if (!contenu.plateau || !contenu.plateau.parcours) return;
    var p = dessinerParcours(contenu, partie, partie.cree || 0);
    if (pl.parcours) { p.forme = pl.parcours.forme; p.tour = pl.parcours.tour; }
    pl.parcours = p; pl.parcoursSuivant = null; pl.route = null; pl.speciaux = Object.assign({}, p.speciaux); pl.ennemis = null;
    if (p.cases.indexOf(pl.position) < 0) { pl.position = p.cases[0]; pl.visites[pl.position] = (pl.visites[pl.position] || 0) + 1; }
    pl.idx = null; route(contenu, partie);
  }

  function contextesPlateau(dep) {
    var vus = {}, out = [];
    dep.etapes.forEach(function (e) {
      var ctx = { prison_liberation: "prison_liberation", prison: "prison", bloque_prison: "prison", eureka: "eureka", recul: "piege",
        retour_epoque: "retour_epoque", teleport: "teleport", oubli: "oubli", renvoi: "oubli", raccourci: "route_raccourcie", detour: "route_detour", cadeau: "cadeau_case", revision: "revision", bloque_revision: "revision", quarantaine: "quarantaine", bloque_quarantaine: "quarantaine", piege: "piege_question", bloque_piege: "piege_question", tour_fini: "tour_fini", ennemi: "ennemi", duel_attente: "ennemi", atome: "atome_apparait", chrono: "chrono_case" }[e.type];
      if (ctx && !vus[ctx]) { vus[ctx] = 1; out.unshift(ctx); }
    });
    if (dep.a !== dep.de && dep.valeur > 0) out.push("plateau_avance");
    return out;
  }

  // v8 : case « révision forcée ». L'IA choisit la compétence maîtrisée dont le rappel est le plus lointain :
  // celle qu'on croyait rangée pour longtemps. Le pion reste bloqué jusqu'à la révision.
  function compARevisier(contenu, partie, t) {
    var m = contenu.competences.filter(function (k) { return estMaitrisee(partie, k.id); });
    if (!m.length) return null;
    return m.sort(function (a, b) { return partie.competences[b.id].prochainRappel - partie.competences[a.id].prochainRappel; })[0];
  }
  function revisionEnCours(partie) {
    var r = partie.revision;
    if (r && !estMaitrisee(partie, r.comp)) { partie.revision = null; return null; }
    return r || null;
  }

  // Victor (2026-10-31) : à chaque pas, Alyca tire parfois un événement qu'elle pose sur la case suivante : un ennemi
  // (il la garde, vaincu le pion y entre), un atome sauvage, une partie de Chrono ou un piège. Chaque type demande son
  // pack (ennemis, atomes, frise) ; l'humeur règle la fréquence et le mélange (plateau.json regles.evenements).
  function evenementsPossibles(contenu, partie, t, rj) {
    var R = contenu.plateau.regles, out = [];
    if (contenu.ennemis && contenu.ennemis.length && contenu.placement && !(rj && rj.ennemis === "absents")) out.push("ennemi");
    if (contenu.atomes && (partie.sauvages || []).length < contenu.atomes.regles.attente_max) out.push("atome");
    if (R.chrono && chronoPossible(contenu, partie)) out.push("chrono");
    if ((R.evenements && R.evenements.pieges || []).length) out.push("piege");
    return out;
  }
  function tirerEvenement(contenu, partie, t, rj) {
    var E = contenu.plateau.regles.evenements, pl = partie.plateau; if (!E) return null;
    var rt = route(contenu, partie), j = pl.idx + 1;
    if (j >= rt.length - 1) return null;
    var n = rt[j], en = ennemisPlateau(contenu, partie);
    if (en[n] || specialDe(contenu, partie, n) || (partie.sauvages || []).some(function (x) { return x.case === n; })) return null;
    var fav = faveurIA(contenu, partie, t), palier = fav ? fav.palier.id : "contente";
    var g = String(t) + "|ev|" + partie.journal.length + "|" + (partie.cree || 0);
    var chance = (E.chance && E.chance[palier]) != null ? E.chance[palier] : 0.25;
    // Les masques qui donnaient des cases de plus (ou de moins) écartent (ou attirent) les rencontres.
    if (rj && rj.avance && E.par_avance_masque) chance = Math.max(0, Math.min(0.9, chance + E.par_avance_masque * rj.avance));
    if (tirage(g + "|oui", 1000) >= Math.round(chance * 1000)) return null;
    var types = evenementsPossibles(contenu, partie, t, rj), poids = (E.poids && E.poids[palier]) || {};
    var total = types.reduce(function (a, x) { return a + (poids[x] != null ? poids[x] : 1); }, 0);
    if (!total) return null;
    var x = tirage(g + "|type", 1000) / 1000 * total, type = types[types.length - 1];
    for (var i = 0; i < types.length; i++) { x -= poids[types[i]] != null ? poids[types[i]] : 1; if (x < 0) { type = types[i]; break; } }
    if (type === "ennemi") {
      var bete = partie.bestiaire || {}, poste = {}; Object.keys(en).forEach(function (k) { poste[en[k]] = 1; });
      var choix = contenu.ennemis.filter(function (e) { return e.id !== contenu.reserve && !poste[e.id]; }).map(function (e) {
        var f = bete[e.id], vu = f && (f.victoires || f.defaites);
        return { id: e.id, score: (vu ? 0 : 1000) + (f ? f.defaites * 60 : 0) + hacher(g + "|" + e.id) % 400 };
      }).sort(function (a, b) { return b.score - a.score; })[0];
      if (!choix) return null;
      en[n] = choix.id;
      return { type: "surgit", quoi: "ennemi", case: n, ennemi: choix.id };
    }
    if (type === "piege") {
      var L = E.pieges, sp = Object.assign({}, L[tirage(g + "|piege", L.length)], { evenement: true });
      pl.speciaux[n] = sp;
      return { type: "surgit", quoi: "piege", case: n, regle: sp.type };
    }
    pl.speciaux[n] = { type: type === "atome" ? "mendeleiev" : "chrono", evenement: true };
    return { type: "surgit", quoi: type, case: n };
  }

  // v20 : les cases qu'un désarmement acheté rend inoffensives.
  var PIEGES = { recul: 1, retour_epoque: 1, teleport: 1, oubli: 1, revision: 1, quarantaine: 1, prison: 1 };
  // Déplace le pion de `valeur` cases (négatif : recul simple, sans effet de case).
  // Mode test : on peut l'appeler directement pour parcourir le plateau.
  function deplacer(contenu, partie, valeur, t, cause) {
    var pl = partie.plateau, R = contenu.plateau.regles, c = partie.compteurs;
    if (modeIle(partie)) return { de: pl.position, a: pl.position, valeur: 0, cause: cause, tour: pl.tours, etapes: [], chemin: [pl.position], places: [pl.idx + 1], t: t, contextes: [] };
    // v21 : un parcours dessiné mais pas encore choisi s'impose dès que le pion repart.
    if (pl.parcoursSuivant) appliquerParcours(contenu, partie);
    var dur = pl.tours > 0, mult = dur ? R.tour_suivant.multiplicateur_recul : 1;
    // v15 : le pion avance sur la route du tour (pl.route, liste de cases que l'IA peut raccourcir ou rallonger) ;
    // pl.idx est sa place sur la route, pl.position la case où il se tient.
    var der = route(contenu, partie).length - 1;
    var de = pl.position, deI = pl.idx, etapes = [], chemin = [de], places = [pl.idx + 1];
    function poser(i) {
      var n = pl.route[i];
      pl.idx = i; pl.position = n;
      chemin.push(n); places.push(i + 1);
      pl.visites[n] = (pl.visites[n] || 0) + 1;
      (pl.arrets || (pl.arrets = {}))[n] = 1;
      if (n > pl.atteinte) pl.atteinte = n;
      // v36 : la progression du premier tour se lit à l'année de la case (les numéros ne sont plus dans l'ordre).
      var an = anneeDe(contenu, n);
      if (an != null && (pl.anneeMax == null || an > pl.anneeMax)) pl.anneeMax = an;
    }
    // v32 : ce que fait un piège qui se déclenche (aussi après une question piège ratée).
    function subir(sp) {
      if (sp.type === "recul") {
        var avant = pl.position, avantI = pl.idx;
        poser(Math.max(0, pl.idx - sp.n * mult));
        c.reculs++;
        etapes.push({ type: "recul", case: avant, n: avantI - pl.idx, cause: "piege" });
      } else if (sp.type === "retour_epoque" || sp.type === "teleport") {
        var depuis = pl.position, depuisI = pl.idx;
        poser(placeVers(contenu, pl.route, pl.idx, sp.vers));
        c.reculs++;
        etapes.push({ type: sp.type, case: depuis, n: depuisI - pl.idx, vers: pl.position });
      } else if (sp.type === "oubli") {
        // v15 : retour à la première case jamais dévoilée (à défaut, la première pas encore foulée dans ce tour).
        var ici = pl.position, iciI = pl.idx, vers = caseOubliee(contenu, partie, iciI);
        if (vers != null) { poser(vers); c.reculs++; etapes.push({ type: "oubli", case: ici, n: iciI - vers, vers: pl.position }); }
        else etapes.push({ type: "oubli_vide", case: ici });
      } else if (sp.type === "revision") {
        var cible = compARevisier(contenu, partie, t);
        if (cible) {
          partie.revision = { comp: cible.id, case: pl.position, depuis: t };
          c.revisions = (c.revisions || 0) + 1;
          etapes.push({ type: "revision", case: pl.position, comp: cible.id });
        } else etapes.push({ type: "revision_vide", case: pl.position });
      } else if (sp.type === "quarantaine") {
        pl.quarantaine = sp.n * mult;
        etapes.push({ type: "quarantaine", case: pl.position, n: pl.quarantaine });
      } else if (sp.type === "prison") {
        pl.prison = dur ? R.tour_suivant.quiz_parfaits_prison : 1;
        etapes.push({ type: "prison", case: pl.position, n: pl.prison });
      }
    }
    var rj = reglesDuJour(contenu, partie, t);
    // v11 : un masque peut écarter les ennemis pour la journée.
    var ennemis = rj.ennemis === "absents" ? {} : ennemisPlateau(contenu, partie);
    function avancer(n) {
      var cible = pl.idx + n;
      // v7 : un ennemi sur la route arrête le pion et lance un duel ; il reste `reste` cases à faire après la victoire.
      // v9 : chaque case Mendeleïev croisée (ou atteinte) fait apparaître un atome sauvage.
      for (var j = pl.idx + 1; j <= Math.min(cible, der - 1); j++) {
        var e = pl.route[j], spE = specialDe(contenu, partie, e);
        if (spE && spE.type === "mendeleiev" && contenu.atomes) {
          // v19 : un atome qui apparaît arrête le pion sur sa case ; le reste du trajet attend le combat (ou qu'on le laisse partir).
          var ap = apparition(contenu, partie, e, t);
          if (spE.evenement) pl.speciaux[e] = null;
          if (ap.type === "atome") {
            poser(j);
            ap.reste = cible - j; ap.arret = true;
            partie.sauvages[partie.sauvages.length - 1].reste = cible - j;
            etapes.push(ap);
            return false;
          }
          etapes.push(ap);
        }
        if (ennemis[e]) {
          poser(j);
          partie.duel = { ennemi: ennemis[e], case: e, reste: cible - j, pret: true, depuis: t };
          etapes.push({ type: "ennemi", case: e, ennemi: ennemis[e], reste: cible - j });
          return false;
        }
      }
      if (cible >= der) {
        poser(der);
        // v21 : les records se comptent par forme de parcours.
        var forme = (pl.parcours && pl.parcours.forme) || "serpentin", mf = pl.meilleurs || (pl.meilleurs = {});
        if (mf.serpentin == null && pl.meilleur != null) mf.serpentin = pl.meilleur;
        var coups = pl.coups || 0, record = coups > 0 && (mf[forme] == null || coups < mf[forme]);
        var fin = { type: "tour_fini", tour: pl.tours + 1, coups: coups, record: record, ancien: mf[forme], forme: forme, case: pl.route[der] };
        // Victor (2026-10-31) : le tour suivant reprend après la dernière case de celui-ci. Toutes les cases vues : victoire,
        // et l'histoire recommence au début (avec, peut-être, d'autres arbres allumés).
        var pcF = pl.parcours || {};
        if (pcF.fin) { fin.victoire = true; c.victoires = (c.victoires || 0) + 1; pl.departTour = null; pl.victoire = { t: t, tour: pl.tours + 1 }; }
        else if (pcF.dernier) pl.departTour = pcF.dernier;
        etapes.push(fin);
        if (record) mf[forme] = coups;
        if (coups > 0 && (pl.meilleur == null || coups < pl.meilleur)) pl.meilleur = coups;
        pl.coups = 0; pl.arrets = {};
        pl.tours++;
        pl.atteinte = R.arrivee; pl.anneeMax = null;
        pl.ennemis = null; pl.speciaux = Object.assign({}, pl.parcours && pl.parcours.speciaux); ennemis = rj.ennemis === "absents" ? {} : ennemisPlateau(contenu, partie);
        // Victor (2026-11-02) : le pion reste sur l'arrivée tant que le joueur n'a pas choisi « Refaire un tour » (ou relancé
        // une épreuve) : c'est appliquerParcours qui le ramène au départ du nouveau parcours.
        if (contenu.plateau.parcours) {
          pl.parcoursSuivant = dessinerParcours(contenu, partie, t);
          pl.arrets[pl.position] = 1;
        } else {
          pl.route = null; der = route(contenu, partie).length - 1;
          pl.idx = 0; pl.position = pl.route[0]; pl.arrets[pl.position] = 1;
          chemin.push(pl.position); places.push(1);
        }
        // v32 (Victor) : boucler un tour ravit l'IA. Le parcours suivant est déjà dessiné, selon l'humeur d'avant.
        var Ag = contenu.ia && contenu.ia.credits && contenu.ia.credits.agacement, fv = faveurIA(contenu, partie, t);
        if (Ag && Ag.tour_fini && fv) {
          partie.faveur = { valeur: Math.min(100, fv.valeur + Ag.tour_fini), maj: t };
          fin.faveur = { gain: partie.faveur.valeur - fv.valeur, avant: fv.valeur, apres: partie.faveur.valeur };
        }
        return false;
      }
      poser(cible);
      return true;
    }
    if (cause === "piege" && partie.piege) {
      var pg = partie.piege; partie.piege = null;
      if (pl.position === pg.case) subir(pg.regle);
    } else if (partie.piege && partie.piege.case === pl.position && valeur > 0) etapes.push({ type: "bloque_piege", case: pl.position });
    else if (valeur < 0 && pl.prison > 0) etapes.push({ type: "bloque_prison", reste: pl.prison });
    else if (valeur < 0) {
      poser(Math.max(0, pl.idx + valeur));
      if (pl.idx < deI) { c.reculs++; etapes.push({ type: "recul", n: deI - pl.idx, cause: cause === "cadeau" ? "cadeau" : "echec" }); }
    } else if (valeur > 0) {
      // Le pion repart d'une autre façon : les atomes qui l'avaient arrêté ne retiennent plus de trajet.
      if (cause !== "atome") (partie.sauvages || []).forEach(function (x) { x.reste = 0; });
      if (pl.prison > 0) etapes.push({ type: "bloque_prison", reste: pl.prison });
      else if (pl.quarantaine > 0) { pl.quarantaine--; etapes.push({ type: "bloque_quarantaine", reste: pl.quarantaine }); }
      else if (revisionEnCours(partie)) etapes.push({ type: "bloque_revision", comp: partie.revision.comp });
      else if (partie.duel && partie.duel.case === pl.position && cause !== "duel") {
        // Un duel perdu reprend à l'épreuve réussie suivante, qui vaut alors pour la suite du trajet.
        partie.duel.reste = valeur; partie.duel.pret = true;
        etapes.push({ type: "duel_attente", case: pl.position, ennemi: partie.duel.ennemi, reste: valeur });
      } else {
        var pas = valeur, garde = 0;
        // Victor (2026-10-31) : le plus souvent on avance d'une case ; parfois un ennemi, un atome, une partie de Chrono
        // ou un piège surgit sur la case suivante (selon les packs allumés et l'humeur d'Alyca).
        if (cause === "quiz" || cause === "rappel" || cause === "chrono") {
          var ev = tirerEvenement(contenu, partie, t, rj);
          if (ev) etapes.push(ev);
        }
        while (avancer(pas) && garde++ < MAX_ENCHAINEMENT) {
          var sp = specialDe(contenu, partie, pl.position);
          if (!sp) break;
          if (sp.evenement) pl.speciaux[pl.position] = null;
          if (sp.type === "eureka") { c.eurekas++; etapes.push({ type: "eureka", case: pl.position, n: pas }); continue; }
          if (sp.type === "avance") { pas = sp.n; etapes.push({ type: "avance", case: pl.position, n: sp.n }); continue; }
          if (PIEGES[sp.type] && enPoche(partie, "desarme") && !(sp.type === "revision" && revisionEnCours(partie))) {
            utiliser(partie, "desarme", t);
            etapes.push({ type: "piege_desarme", case: pl.position, regle: sp.type });
          } else if (rj.pieges === "neutres" && (sp.type === "recul" || sp.type === "teleport" || sp.type === "retour_epoque" || sp.type === "oubli")) {
            etapes.push({ type: "piege_evite", case: pl.position, regle: sp.type });
          } else if (PIEGES[sp.type] && contenu.plateau.regles.question_piege && cause !== "test") {
            // v32 (Victor) : « Piège ! » Le pion s'arrête ; une question difficile, sans faute, le désamorce.
            partie.piege = { case: pl.position, regle: sp, depuis: t, q: null };
            etapes.push({ type: "piege", case: pl.position, regle: sp.type });
          } else if (PIEGES[sp.type]) {
            subir(sp);
          } else if (sp.type === "chrono" && !sp.libre && contenu.plateau.regles.chrono) {
            // v34 (Victor) : case Chrono. Le pion s'arrête ; la partie de Chrono sert d'épreuve de la case.
            if (chronoPossible(contenu, partie)) { etatChrono(partie).case = pl.position; etapes.push({ type: "chrono", case: pl.position }); }
            else if (chronoActif(partie)) etapes.push({ type: "chrono_vide", case: pl.position });
          } else if (sp.type === "cadeau") {
            var cad = tirerCadeau(contenu, partie, t);
            if (cad) {
              (partie.cadeauxCase || (partie.cadeauxCase = [])).push({ famille: cad.famille, id: cad.chose.id });
              c.cadeauxCase = (c.cadeauxCase || 0) + 1;
              etapes.push({ type: "cadeau", case: pl.position, famille: cad.famille, id: cad.chose.id });
            } else etapes.push({ type: "cadeau_vide", case: pl.position });
          }
          break;
        }
      }
    }
    // Le pion a quitté la case de l'ennemi (recul) : le duel est oublié. Pareil pour un piège en attente.
    if (partie.duel && partie.duel.case !== pl.position) partie.duel = null;
    if (partie.piege && partie.piege.case !== pl.position) partie.piege = null;
    if (partie.siecles && partie.siecles.case && partie.siecles.case !== pl.position) { partie.siecles.case = null; if (partie.siecles.jeu && partie.siecles.jeu.mode === "case") partie.siecles.jeu = null; }
    // chemin : les cases où le pion se pose, dans l'ordre, pour l'animer case par case.
    // places : les mêmes, en rang sur la route (1 = départ), pour le dessin.
    var dep = { de: de, a: pl.position, valeur: valeur, cause: cause, tour: pl.tours, etapes: etapes, chemin: chemin, places: places, t: t };
    pl.historique.unshift({ t: t, de: de, a: pl.position, valeur: valeur, cause: cause, etapes: etapes.map(function (e) { return e.type; }) });
    if (pl.historique.length > MAX_HISTORIQUE) pl.historique.length = MAX_HISTORIQUE;
    partie.maj = t;
    return dep;
  }

  // Mode test : avance le pion sans épreuve, puis débloque ce qui doit l'être.
  function avancerPion(contenu, partie, n, t) {
    var dep = deplacer(contenu, partie, n, t, "test");
    dep.contextes = contextesPlateau(dep);
    partie.compteurs.modeTest++;
    dep.recompenses = verifierRecompenses(contenu, partie, t);
    return dep;
  }

  // --- Duels (v7) -----------------------------------------------------------
  // Passer sur un ennemi arrête le pion. Le duel : cinq affirmations à juger, vraies ou fausses, toutes justes pour gagner.
  // Gagné : l'ennemi quitte le plateau jusqu'au tour suivant, le pion finit son trajet, un butin tombe à coup sûr.
  // Perdu : le pion reste, et le duel reprend à la prochaine épreuve réussie.

  function ficheBestiaire(partie, id) {
    partie.bestiaire = partie.bestiaire || {};
    return partie.bestiaire[id] || (partie.bestiaire[id] = { victoires: 0, defaites: 0, serie: 0, meilleure: 0, dernier: null, vus: [] });
  }

  // Les affirmations du duel en cours : d'abord celles que le joueur n'a pas encore vues, dans un ordre mêlé.
  function tirerDuel(contenu, partie, t, alea) {
    var d = partie.duel; if (!d) return [];
    alea = alea || Math.random;
    var f = ficheBestiaire(partie, d.ennemi), toutes = contenu.mythes.filter(function (m) { return m.ennemi === d.ennemi; });
    var neuves = toutes.filter(function (m) { return f.vus.indexOf(m.id) < 0; });
    if (neuves.length < contenu.questionsDuel) { f.vus = []; neuves = toutes; }
    var choix = melanger(neuves, alea).slice(0, contenu.questionsDuel);
    f.vus = f.vus.concat(choix.map(function (m) { return m.id; }));
    return choix;
  }

  // Butin garanti d'une victoire : un butin ouvert, ou à défaut un butin gagnable du lot suivant.
  function butinDuel(contenu, partie, t, alea) {
    var b = tirerButin(contenu, partie, { type: "duel", ennemi: partie.duel && partie.duel.ennemi }, t, alea);
    if (b) return b;
    var tour = partie.plateau.tours + 2, proches = [];
    FAMILLES_BUTIN.forEach(function (f) {
      listeFamille(contenu, f).forEach(function (x) {
        if (f !== "livres" && partie.gagnables && partie.gagnables[cleButin(f, x.id)] && !possede(partie, f, x.id) && x.lot <= tour) proches.push({ famille: f, chose: x });
      });
    });
    var lot = lotDe(partie, t); if (lotPlein(lot)) return null;
    proches = horsLot(lot, proches);
    if (!proches.length) return null;
    b = proches[Math.floor((alea || Math.random)() * proches.length)];
    partie[b.famille][b.chose.id] = t; compterLot(lot, b.famille);
    delete partie.gagnables[cleButin(b.famille, b.chose.id)];
    if (b.famille === "masques") partie.masque = b.chose.id;
    return b;
  }

  // `resultats` : [{id, correct}]. Renvoie {gagne, ennemi, bonnes, total, plateau, recompenses, butin, premiere, fiche}.
  var VOL_DUEL = { part: 0.15, min: 5, max: 50 };
  // v21 : un duel ouvert sur la case du pion ferme les autres épreuves.
  function duelBloquant(partie) { var d = partie.duel; return !!(d && d.pret && partie.plateau && d.case === partie.plateau.position); }
  function terminerDuel(contenu, partie, resultats, t, alea, total) {
    var d = partie.duel; if (!d) return null;
    ouvrirLot(partie, t, themeActif(contenu, contenu.ennemiParId[d.ennemi] && contenu.ennemiParId[d.ennemi].theme));
    var e = contenu.ennemiParId[d.ennemi], f = ficheBestiaire(partie, d.ennemi), c = partie.compteurs;
    var bonnes = resultats.filter(function (x) { return x.correct; }).length, gagne = resultats.length > 0 && bonnes === resultats.length;
    f.dernier = t;
    var out = { gagne: gagne, ennemi: e, bonnes: bonnes, total: Math.max(resultats.length, total || 0), plateau: null, recompenses: null, butin: null, premiere: false, fiche: f };
    out.agacement = agacerIA(contenu, partie, resultats.length - bonnes, !gagne, t, "duel_gagne");
    if (gagne) { var chasses = chasserParasites(contenu, partie); if (chasses) out.parasitesChasses = chasses; }
    if (gagne) {
      f.victoires++; f.serie++; f.meilleure = Math.max(f.meilleure, f.serie);
      c.duelsGagnes = (c.duelsGagnes || 0) + 1;
      out.premiere = f.victoires === 1;
      delete ennemisPlateau(contenu, partie)[d.case];
      partie.duel = null;
      partie.plateau.coups = (partie.plateau.coups || 0) + 1;
      partie.lot.cap = SUCCES_DUEL;
      out.butin = butinDuel(contenu, partie, t, alea);
      var avant = verifierRecompenses(contenu, partie, t);
      if (out.butin) { if (out.butin.famille === "masques") avant.masque = out.butin.chose; else avant[out.butin.famille].push(out.butin.chose); }
      var dep = deplacer(contenu, partie, d.reste, t, "duel");
      dep.contextes = contextesPlateau(dep);
      out.plateau = dep;
      lotExceptionnel(partie, dep);
      var apres = verifierRecompenses(contenu, partie, t);
      out.recompenses = fusionRec(avant, apres); out.avantPlateau = avant; out.apresPlateau = apres;
    } else {
      f.defaites++; f.serie = 0;
      c.duelsPerdus = (c.duelsPerdus || 0) + 1;
      // v21 : l'ennemi garde sa case et le duel reste ouvert : il faut le battre pour passer, pas d'autre épreuve.
      // Vainqueur, il fait les poches du joueur.
      var cr = partie.credits, vol = reglage(partie, "vol") === false ? 0 : Math.min(cr.solde, Math.max(VOL_DUEL.min, Math.min(VOL_DUEL.max, Math.round(cr.solde * VOL_DUEL.part))));
      if (vol > 0) { cr.solde -= vol; cr.voles = (cr.voles || 0) + vol; f.vole = (f.vole || 0) + vol; }
      out.vol = vol;
      partie.plateau.coups = (partie.plateau.coups || 0) + 1;
      // v15 : certains ennemis renvoient le pion à la première case qu'il n'a pas encore vue. Le duel est levé ;
      // l'ennemi garde son poste et attend le prochain passage.
      route(contenu, partie);
      var pl = partie.plateau, ici = pl.idx, j = e.renvoi ? caseOubliee(contenu, partie, ici) : null;
      if (j != null) {
        var vers = pl.route[j];
        pl.idx = j; pl.position = vers; pl.visites[vers] = (pl.visites[vers] || 0) + 1; (pl.arrets || (pl.arrets = {}))[vers] = 1;
        c.reculs++; partie.duel = null;
        out.plateau = { de: d.case, a: vers, chemin: [d.case, vers], places: [ici + 1, j + 1], valeur: 0, cause: "renvoi",
          etapes: [{ type: "renvoi", case: d.case, ennemi: e.id, vers: vers, n: ici - j }] };
        out.plateau.contextes = contextesPlateau(out.plateau);
      }
      out.recompenses = verifierRecompenses(contenu, partie, t);
    }
    partie.maj = t;
    return out;
  }

  // --- Jeu de Mendeleïev (v9) -----------------------------------------------
  // Passer sur une case Mendeleïev fait apparaître un atome sauvage, qui attend son combat (au plus
  // `attente_max` à la fois). Le combat : trois questions (symbole, numéro atomique, où on le croise) ; `seuil`
  // bonnes réponses le capturent, sinon il s'enfuit et pourra revenir. Le tableau périodique sert de Pokédex.

  function estCapture(partie, z) { return !!(partie.atomes && partie.atomes[z] && partie.atomes[z].capture); }
  function ficheAtome(partie, z) {
    partie.atomes = partie.atomes || {};
    return partie.atomes[z] || (partie.atomes[z] = { capture: null, rencontres: 0, fuites: 0 });
  }
  function elementZ(contenu, z) { return contenu.atomes ? contenu.atomes.elements[z - 1] : null; }

  // L'atome sauvage : un élément pas encore capturé ni déjà en attente, tiré selon sa rareté.
  // Tirage déterministe (date, case, journal) comme les cases cadeau. Tout est capturé : n'importe lequel revient.
  function tirerAtome(contenu, partie, n, t) {
    var A = contenu.atomes, attente = (partie.sauvages || []).map(function (x) { return x.z; });
    var libres = A.elements.filter(function (e) { return !estCapture(partie, e.z) && attente.indexOf(e.z) < 0; });
    if (!libres.length) libres = A.elements.filter(function (e) { return attente.indexOf(e.z) < 0; });
    if (!libres.length) return null;
    // v19 : en début de parcours, les éléments du début du tableau (les plus faciles) sortent surtout.
    // L'échelle s'élargit avec la progression : au premier tour, case 7 → surtout z ≤ 12 ; à partir du 2e tour, presque tout.
    var pl = partie.plateau, prog = pl ? (pl.tours || 0) + (pl.route && pl.route.length > 1 ? (pl.idx || 0) / (pl.route.length - 1) : 0) : 2, echelle = 6 + 45 * prog;
    // Les matériaux qu'un chantier de l'île attend passent devant : au moins le poids d'un élément facile, et six fois le leur.
    var attendus = materiauxAttendus(contenu, partie);
    var poids = libres.map(function (e) { var p = A.raretes[e.rarete].poids * Math.exp(-(e.z - 1) / echelle) * 1000; return attendus[e.z] ? Math.max(p * 6, A.raretes[e.rarete].poids * 400) : p; }), total = poids.reduce(function (a, b) { return a + b; }, 0);
    var x = tirage(String(t) + "|" + n + "|" + partie.journal.length + "|" + attente.length, 1000000) / 1000000 * total;
    for (var i = 0; i < libres.length; i++) { x -= poids[i]; if (x < 0) return libres[i]; }
    return libres[libres.length - 1];
  }
  function apparition(contenu, partie, n, t) {
    if (!contenu.atomes) return { type: "atome_vide", case: n };
    partie.sauvages = partie.sauvages || [];
    if (partie.sauvages.length >= contenu.atomes.regles.attente_max) return { type: "atome_plein", case: n };
    var e = tirerAtome(contenu, partie, n, t);
    if (!e) return { type: "atome_vide", case: n };
    partie.sauvages.push({ z: e.z, case: n, depuis: t });
    ficheAtome(partie, e.z).rencontres++;
    return { type: "atome", case: n, z: e.z };
  }
  function atomeSauvage(contenu, partie) {
    var s = partie.sauvages && partie.sauvages[0];
    return s && contenu.atomes ? { z: s.z, case: s.case, element: elementZ(contenu, s.z), attente: partie.sauvages.length, reste: s.reste || 0 } : null;
  }

  function texteMasse(e) { return e.stable ? e.masse.toFixed(1).replace(".", ",") : "[" + e.masse + "]"; }
  function sansAccents(x) { return x.normalize("NFD").replace(/[\u0300-\u036f]/g, ""); }
  function mots(x) {
    return sansAccents(x.toLowerCase()).split(/[^a-z]+/).filter(function (m) { return m.length >= 6; }).map(function (m) { return m.slice(0, 6); });
  }

  // Les trois questions du combat en cours, choix mélangés. Rien n'est enregistré : on peut les retirer.
  function tirerCombat(contenu, partie, alea) {
    var s = atomeSauvage(contenu, partie); if (!s) return null;
    return { z: s.z, element: s.element, questions: questionsCombat(contenu.atomes, s.element, alea || Math.random) };
  }
  function questionsCombat(atomes, e, alea) {
    var A = atomes.elements, nom = TX(e.nom);
    function finir(type, enonce, bonne, faux) {
      var choix = melanger([bonne].concat(faux.slice(0, 3)), alea);
      return { type: type, enonce: enonce, choix: choix, reponse: choix.indexOf(bonne) };
    }
    // Symbole : des symboles réels de même initiale, puis des faux tirés des lettres du nom.
    var initiale = e.symbole[0], reels = A.filter(function (x) { return x.z !== e.z && x.symbole[0] === initiale; }).map(function (x) { return x.symbole; });
    var lettres = sansAccents(nom).toLowerCase().replace(/[^a-z]/g, ""), faux = [];
    for (var i = 1; i < lettres.length; i++) {
      var f = lettres[0].toUpperCase() + lettres[i];
      if (f !== e.symbole && faux.indexOf(f) < 0) faux.push(f);
    }
    var pS = melanger(reels, alea).slice(0, 2);
    melanger(faux, alea).forEach(function (f) { if (pS.length < 3 && pS.indexOf(f) < 0) pS.push(f); });
    melanger(A.map(function (x) { return x.symbole; }), alea).forEach(function (f) { if (pS.length < 3 && f !== e.symbole && pS.indexOf(f) < 0) pS.push(f); });
    var q1 = finir("symbole", __("Quel est le symbole de l'atome « {nom} » ?", { nom: nom }), e.symbole, pS);
    // v15 : le numéro atomique (Victor ne voulait pas la masse). v34 (Victor) : leurres éloignés d'au moins 12,
    // pour deviner avec la logique léger/lourd plutôt que de tout savoir par cœur.
    var pZ = [], pris = [e.z];
    melanger(A.map(function (x) { return x.z; }), alea).forEach(function (z) {
      if (pZ.length < 3 && pris.every(function (y) { return Math.abs(y - z) >= 12; })) { pZ.push(String(z)); pris.push(z); }
    });
    var q2 = finir("numero", __("Quel est le numéro atomique de « {nom} » ?", { nom: nom }), String(e.z), pZ);
    // Où : un lieu de cet atome, et des lieux d'autres familles sans mot commun avec les siens.
    var siens = {}; e.ou.forEach(function (o) { mots(TX(o)).forEach(function (m) { siens[m] = 1; }); });
    var bonne = TX(e.ou[Math.floor(alea() * e.ou.length)]), pO = [];
    // Hydrogène, carbone, azote, oxygène sont partout dans le vivant : leurs leurres viennent des métaux lourds.
    var organique = [1, 6, 7, 8].indexOf(e.z) >= 0;
    melanger(A.filter(function (x) { return x.famille !== e.famille && Math.abs(x.z - e.z) > 4 && (!organique || (x.z > 20 && [25, 26, 27, 29, 30, 34, 42, 53].indexOf(x.z) < 0)); }), alea).forEach(function (x) {
      if (pO.length >= 3) return;
      var o = TX(x.ou[Math.floor(alea() * x.ou.length)]);
      if (!mots(o).some(function (m) { return siens[m]; })) pO.push(o);
    });
    var q3 = finir("ou", __("Où croise-t-on surtout « {nom} » ?", { nom: nom }), bonne, pO);
    // v34 (Victor) : le placer sur le tableau, en touchant sa case. `reponse` : le numéro de la case juste.
    var qP = { type: "place", enonce: __("Où va « {nom} » dans le tableau ? Touche sa case.", { nom: nom }), choix: [], reponse: e.z };
    return [q1, q2, qP, q3];
  }

  // v34 (Victor : « super dur de retenir le numéro atomique ») : pas de calcul, une image. L'atome allumé dans le
  // tableau, avec ses deux voisins nommés : on retient une place, pas un nombre isolé.
  // Place dans la grille à 18 colonnes, lanthanides et actinides en lignes 9 et 10 (comme le tableau des Collections).
  function placeTableau(e) {
    if (e.groupe) return { col: e.groupe, lig: e.periode };
    return { col: 3 + (e.z >= 89 ? e.z - 89 : e.z - 57), lig: e.z >= 89 ? 10 : 9 };
  }
  function astuceNumero(atomes, e) {
    var av = atomes.elements[e.z - 2], ap = atomes.elements[e.z], nom = function (x) { return TX(x.nom).toLowerCase() + " (" + x.z + ")"; };
    var voisins = av && ap ? __("entre ") + nom(av) + __(" et ") + nom(ap) : av ? __("juste après ") + nom(av) + __(", tout au bout du tableau") : __("le tout premier, avant ") + nom(ap);
    return { texte: TX(e.nom) + ", n° " + e.z + " : " + voisins + ".", voisins: [av, ap].filter(Boolean).map(function (x) { return x.z; }), illustration: schemaNumero(atomes, e, av, ap) };
  }
  // Le tableau en miniature : l'atome en couleur d'accent, ses deux voisins en jaune, numéros écrits.
  function schemaNumero(atomes, e, av, ap) {
    var T = 17, X0 = 8, Y0 = 6, out = [], haut = function (lig) { return Y0 + (lig - 1) * T + (lig >= 9 ? 6 : 0); };
    var voisin = function (x) { return (av && x.z === av.z) || (ap && x.z === ap.z); };
    atomes.elements.forEach(function (x) {
      var p = placeTableau(x), cl = x.z === e.z ? "a" : voisin(x) ? "jaune" : "f2";
      var px = X0 + (p.col - 1) * T, py = haut(p.lig);
      out.push('<rect class="' + cl + '" x="' + px + '" y="' + py + '" width="' + (T - 2) + '" height="' + (T - 2) + '" rx="2"/>');
      if (x.z === e.z || voisin(x)) out.push('<text x="' + (px + (T - 2) / 2) + '" y="' + (py + 11) + '" font-size="8.5" font-weight="700" text-anchor="middle" fill="' + (x.z === e.z ? "#fff" : "#222") + '" font-family="sans-serif">' + x.z + "</text>");
    });
    var y = haut(10) + T + 14;
    out.push('<text class="t" x="' + X0 + '" y="' + y + '" font-size="13" font-weight="700">' + TX(e.nom) + " (" + e.symbole + ") = " + e.z + "</text>");
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ' + (X0 + 18 * T + 4) + " " + (y + 8) + '" role="img" aria-label="Tableau périodique : ' + TX(e.nom) + __(", numéro ") + e.z + '">' + out.join("") + "</svg>";
  }
  // v34 (Victor) : l'atome dessiné couche par couche. Le nombre de couches donne la ligne ; les électrons de la couche
  // extérieure (plus ceux « en trop » de l'avant-dernière, au milieu du tableau) donnent la colonne.
  var COULEURS_COUCHES = ["#D99A0B", "#2E9E5B", "#2B7BBF", "#8A57C9", "#D9534F", "#17998A", "#A4791A"];
  function lectureCouches(atomes, e) {
    var K = atomes.couches; if (!K) return null;
    var c = K.par_z[e.z - 1].slice(), n = c.length, ext = c[n - 1], av = n > 1 ? c[n - 2] : 0, out = { couches: c, predite: e.z >= K.predites_des, lignes: [] };
    var nom = TX(e.nom), pl = function (k, mot) { return k + " " + mot + (k > 1 ? "s" : ""); };
    if (e.z === 46) {
      out.ligne = 5; out.colonne = 10; out.cas = "palladium";
      out.lignes.push(__("4 couches remplies, et une 5e restée vide : le palladium a gardé tous ses électrons en dessous. Il est quand même sur la ligne 5."));
      out.lignes.push(__("Sa 4e couche est pleine à 18 : 0 dehors + 10 = colonne 10."));
      return out;
    }
    out.ligne = n;
    out.lignes.push(pl(n, __("couche")) + __(" → ligne ") + n + ".");
    if (!e.groupe) {
      out.cas = "terre_rare";
      var serie = e.z >= 89 ? "actinides" : "lanthanides";
      out.lignes.push(__("Sa {n}e couche se remplit ({e} électrons) pendant que les deux dernières bougent à peine : c'est un des {serie}, rangés dans la ligne du bas.", { n: n - 2, e: c[n - 3], serie: serie }));
      return out;
    }
    if (e.z === 2) { out.cas = "helium"; out.colonne = 18; out.lignes.push(__("2 électrons : sa seule couche est déjà pleine. Couche extérieure pleine = gaz noble, colonne 18.")); return out; }
    if (n <= 2 || av === 8 && ext <= 2 || av === 2 || av === 8 && n === 3) {
      out.cas = "principal"; out.colonne = ext <= 2 ? ext : ext + 10;
      out.lignes.push(ext <= 2 ? pl(ext, __("électron")) + __(" sur la couche extérieure → colonne ") + ext + "." : pl(ext, __("électron")) + __(" sur la couche extérieure → colonne ") + ext + " + 10 = " + (ext + 10) + __(" (on saute les 10 colonnes du milieu)."));
    } else if (av === 18 || av === 32) {
      out.colonne = ext + 10; out.cas = ext <= 2 ? "fin_transition" : "principal";
      out.lignes.push(pl(ext, __("électron")) + __(" sur la couche extérieure, et la couche d'en dessous pleine à ") + av + __(" → colonne ") + ext + " + 10 = " + (ext + 10) + ".");
    } else {
      var trop = av - 8; out.cas = "transition"; out.colonne = ext + trop;
      out.lignes.push(pl(ext, __("électron")) + __(" dehors, plus ") + trop + __(" en trop sur la couche d'en dessous (") + av + __(" au lieu de 8) → colonne ") + ext + " + " + trop + " = " + out.colonne + ".");
    }
    return out;
  }
  function dessinCouches(atomes, e) {
    var L = lectureCouches(atomes, e); if (!L) return "";
    var c = L.couches, n = c.length, R = 118, r0 = 20, pas = Math.min(26, (R - r0 - 4) / n), out = [], cx = 125, cy = 125;
    for (var i = 0; i < n; i++) {
      var r = r0 + 4 + pas * (i + 1), col = COULEURS_COUCHES[i], k = c[i], dehors = i === n - 1;
      out.push('<circle cx="' + cx + '" cy="' + cy + '" r="' + r.toFixed(1) + '" fill="none" stroke="' + col + '" stroke-width="' + (dehors ? 2.6 : 1.4) + '" stroke-opacity="' + (dehors ? 1 : 0.75) + '"/>');
      var dr = Math.max(1.6, Math.min(dehors ? 6 : 4.4, (2 * Math.PI * r / Math.max(k, 1)) * 0.36));
      for (var j = 0; j < k; j++) {
        var a = -Math.PI / 2 + 2 * Math.PI * j / k + i * 0.35;
        out.push('<circle cx="' + (cx + r * Math.cos(a)).toFixed(1) + '" cy="' + (cy + r * Math.sin(a)).toFixed(1) + '" r="' + dr.toFixed(1) + '" fill="' + col + '"' + (dehors ? ' stroke="#222" stroke-width="1.2"' : "") + "/>");
      }
    }
    out.push('<circle cx="' + cx + '" cy="' + cy + '" r="' + r0 + '" fill="#C0392B"/><text x="' + cx + '" y="' + (cy + 5) + '" font-size="15" font-weight="700" text-anchor="middle" fill="#fff" font-family="sans-serif">' + e.symbole + "</text>");
    // La légende : une ligne par couche, à sa couleur.
    var lx = 262;
    out.push('<text class="tm" x="' + lx + __('" y="20" font-size="11">couche · électrons</text>'));
    for (i = 0; i < n; i++) {
      var y = 40 + i * 24;
      out.push('<circle cx="' + (lx + 7) + '" cy="' + (y - 4) + '" r="7" fill="' + COULEURS_COUCHES[i] + '"/><text class="t" x="' + (lx + 20) + '" y="' + y + '" font-size="14" font-weight="' + (i === n - 1 ? 700 : 400) + '">' + (i + 1) + " · " + c[i] + (i === n - 1 ? __(" ← dehors") : "") + "</text>");
    }
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 380 250" role="img" aria-label="' + TX(e.nom) + " : " + c.join(", ") + __(' électrons par couche">') + out.join("") + "</svg>";
  }

  // Les questions d'un atome sur le mur : mêmes questions qu'au combat, leurres figés ; le numéro s'y écrit au clavier.
  function questionsMur(atomes, e) {
    var k = 0, graine = "mur-atome|" + e.z, alea = function () { return (hacher(graine + "|" + (k++)) % 100000) / 100000; };
    var qs = questionsCombat(atomes, e, alea), ast = astuceNumero(atomes, e);
    var lieux = e.ou.map(function (o) { return TX(o); }).join(", ");
    return qs.map(function (q) {
      var base = { id: "atome." + e.z + "." + q.type, competence: "sci.atomes", atome: e.z, enonce: { fr: q.enonce } };
      var lc = lectureCouches(atomes, e);
      if (q.type === "numero") return Object.assign(base, { type: "numerique", reponse: e.z, tolerance: 0, explication: { fr: ast.texte + (lc ? " " + lc.lignes.join(" ") : "") }, illustration_explication: (lc ? dessinCouches(atomes, e) : "") + ast.illustration });
      if (q.type === "place") return Object.assign(base, { type: "place", reponse: e.z, explication: { fr: (lc ? lc.lignes.join(" ") + " " : "") + ast.texte }, illustration_explication: (lc ? dessinCouches(atomes, e) : "") + ast.illustration });
      return Object.assign(base, { type: "qcm", choix: q.choix.map(function (c) { return { fr: c }; }), reponse: q.reponse,
        explication: { fr: q.type === "symbole" ? __("Le symbole de « {nom} » est {symbole}, numéro {z}.", { nom: TX(e.nom), symbole: e.symbole, z: e.z }) : __("On le croise surtout dans ") + lieux + ". " + TX(e.anecdote) } });
    });
  }
  // L'atome qui porte ce symbole ou ce numéro : « tu as dit 24 ? c'est le chrome ».
  function atomeDit(atomes, type, valeur) {
    return atomes.elements.filter(function (x) { return type === "numero" ? String(x.z) === String(valeur) : x.symbole === valeur; })[0] || null;
  }

  // `bonnes` : nombre de bonnes réponses. Renvoie {capture, element, bonnes, total, premiere, fiche, recompenses}.
  // v34 : `ratees` (facultatif) : [{type, rep}] des questions manquées, épinglées au mur de la honte.
  // v34 (Victor) : `indice` : les atomes capturés ont été montrés sur le tableau. Ça aide, mais ça coûte :
  // une récompense de moins dans le lot, et pas de faveur gagnée si l'atome est pris.
  function terminerCombat(contenu, partie, bonnes, t, ratees, indice) {
    var s = atomeSauvage(contenu, partie); if (!s) return null;
    if (ratees && ratees.length) epinglerOublis(partie, "sci.atomes", ratees.map(function (x) {
      var id = "atome." + s.z + "." + x.type, q = contenu.questionParId[id], rep = x.rep === undefined ? null : x.rep;
      // Leurre absent des choix figés du mur : on garde son texte.
      if (q && q.type === "qcm" && rep !== null) { var ix = q.choix.map(function (c) { return TX(c); }).indexOf(rep); if (ix >= 0) rep = ix; }
      return { id: id, correct: false, rep: rep };
    }).filter(function (x) { return contenu.questionParId[x.id]; }), t, "atome");
    ouvrirLot(partie, t, themeActif(contenu, contenu.atomes && contenu.atomes.theme));
    if (indice) partie.lot.cap = RECOMPENSES_PAR_EPREUVE - 1;
    var R = contenu.atomes.regles, c = partie.compteurs, f = ficheAtome(partie, s.z);
    partie.sauvages.shift();
    var capture = bonnes >= seuilAtome(contenu, partie, t), premiere = capture && !f.capture;
    if (capture) { if (!f.capture) { f.capture = t; c.atomesCaptures = (c.atomesCaptures || 0) + 1; } }
    else { f.fuites++; c.atomesEnfuis = (c.atomesEnfuis || 0) + 1; }
    var ag = indice && capture ? null : agacerIA(contenu, partie, R.questions - bonnes, !capture, t);
    var avant = verifierRecompenses(contenu, partie, t);
    var dep = suiteTrajet(contenu, partie, s, t);
    var apres = verifierRecompenses(contenu, partie, t), rec = fusionRec(avant, apres);
    partie.maj = t;
    return { chantiers: capture ? chantiersDe(contenu, partie, s.element.z, t) : [], avantPlateau: avant, apresPlateau: apres, plateau: dep, capture: capture, element: s.element, bonnes: bonnes, total: R.questions, premiere: premiere, fiche: f, recompenses: rec, agacement: ag, indice: !!indice,
      captures: Object.keys(partie.atomes).filter(function (z) { return partie.atomes[z].capture; }).length };
  }

  // v19 : l'atome a arrêté le pion ; capturé, enfui ou laissé partir, le pion finit son trajet.
  function suiteTrajet(contenu, partie, s, t) {
    if (!s.reste || !contenu.plateau || partie.plateau.position !== s.case) return null;
    var dep = deplacer(contenu, partie, s.reste, t, "atome");
    dep.contextes = contextesPlateau(dep);
    return dep;
  }
  // Le laisser partir : pas de combat, pas de fuite comptée. Il pourra revenir.
  function laisserPartir(contenu, partie, t) {
    var s = atomeSauvage(contenu, partie); if (!s) return null;
    partie.sauvages.shift();
    var dep = suiteTrajet(contenu, partie, s, t);
    partie.maj = t;
    var apres = verifierRecompenses(contenu, partie, t);
    return { element: s.element, plateau: dep, recompenses: apres, apresPlateau: apres };
  }

  // --- Boutique de l'IA (v19) -------------------------------------------------
  // Tout s'achète à l'aveugle avec les crédits : on paie, l'IA tire au hasard parmi ce qu'on n'a pas encore.
  // Le parcours aussi : chasser le prochain ennemi, en convoquer un, ou faire piocher l'IA dans un arbre.
  var FAMILLE_ARTICLE = { objet: "objets", livre: "livres", accessoire: "accessoires", masque: "masques" };
  function boutique(contenu) { return contenu.ia && contenu.ia.credits && contenu.ia.credits.boutique; }
  // v35 : chaque article est une fiche de pack ; un pack éteint retire les siens du rayon.
  function articleDe(contenu, id) {
    var B = boutique(contenu);
    return (B && B.articles.filter(function (a) { return a.id === id; })[0]) || null;
  }
  function enRayon(contenu, partie, article, t) {
    var f = FAMILLE_ARTICLE[article];
    if (f) return listeFamille(contenu, f).filter(function (x) { return (estButin(x) || f === "masques") && !possede(partie, f, x.id); });
    // v34 (Victor) : le kit du chasseur, un équipement acheté une fois pour toutes.
    if (article === "kit") return contenu.atomes && !partie.kit ? [1] : [];
    // Mode Île : rien à acheter qui concerne le pion.
    if (!contenu.plateau || !contenu.placement || modeIle(partie)) return [];
    var pl = partie.plateau, en = ennemisPlateau(contenu, partie), rt = route(contenu, partie);
    if (article === "chasser") return rt.slice(pl.idx).filter(function (n) { return en[n]; });
    if (article === "convoquer") {
      var pris = Object.keys(en).map(function (n) { return en[n]; });
      return contenu.ennemis.filter(function (e) { return pris.indexOf(e.id) < 0; }).length && casesLibres(contenu, partie).length ? [1] : [];
    }
    if (article === "arbre") return contenu.stats.filter(function (st) { return arbreOuvert(contenu, partie, st.id); });
    if (POCHE[article]) { var B = boutique(contenu); return enPoche(partie, article) < ((B && B.stock_max) || 5) ? [1] : []; }
    // v26 : une case de plus, une fois par jour ; pas quand le pion est retenu (duel à rejouer, révision forcée).
    if (article === "avancer") return (t != null && (partie.credits.avanceJour === cleJour(t) || jeuFerme(contenu, partie, t))) || duelBloquant(partie) || revisionEnCours(partie) ? [] : [1];
    return [];
  }
  // Cases devant le pion où poser un ennemi : ni spéciales, ni déjà gardées, ni la dernière.
  function casesLibres(contenu, partie) {
    var pl = partie.plateau, en = ennemisPlateau(contenu, partie), rt = route(contenu, partie);
    return rt.slice(pl.idx + 2, rt.length - 1).filter(function (n) { return !en[n] && !specialDe(contenu, partie, n) && !(partie.sauvages || []).some(function (x) { return x.case === n; }); });
  }
  // `choix` : l'arbre favori (article « arbre »). Renvoie {ok, article, prix, chose, famille, ennemi, case, stat, mot} ou {ok: false, raison}.
  function acheter(contenu, partie, article, t, choix) {
    var B = boutique(contenu), fiche = articleDe(contenu, article); if (!B || !fiche) return { ok: false, raison: "inconnu" };
    var prix = fiche.prix, cr = partie.credits;
    if (cr.solde < prix) return { ok: false, raison: "solde" };
    var rayon = enRayon(contenu, partie, article, t);
    if (!rayon.length) return { ok: false, raison: article === "avancer" && partie.credits.avanceJour === cleJour(t) ? "jour" : "vide" };
    var graine = "boutique|" + article + "|" + t + "|" + (partie.journal ? partie.journal.length : 0), out = { ok: true, article: article, prix: prix };
    var f = FAMILLE_ARTICLE[article], pl = partie.plateau;
    if (f) {
      var x = rayon[tirage(graine, rayon.length)];
      partie[f][x.id] = t; out.chose = x; out.famille = f;
      if (partie.gagnables) delete partie.gagnables[cleButin(f, x.id)];
      if (f === "masques") {
        partie.masque = x.id;
        var fav = faveurIA(contenu, partie, t);
        if (fav) partie.faveur = { valeur: Math.min(100, fav.valeur + (B.faveur_masque || 0)), maj: t };
      }
    } else if (article === "chasser") {
      var n = rayon[0], en = ennemisPlateau(contenu, partie);
      out.ennemi = contenu.ennemiParId[en[n]]; out.case = n;
      delete en[n];
      if (partie.duel && partie.duel.case === n) partie.duel = null;
    } else if (article === "convoquer") {
      var en2 = ennemisPlateau(contenu, partie), pris = Object.keys(en2).map(function (k) { return en2[k]; });
      var libres = contenu.ennemis.filter(function (e) { return pris.indexOf(e.id) < 0; }), cases = casesLibres(contenu, partie);
      var e = libres[tirage(graine + "|e", libres.length)], c = cases[Math.min(cases.length - 1, tirage(graine + "|c", Math.min(4, cases.length)))];
      en2[c] = e.id; out.ennemi = e; out.case = c;
    } else if (article === "arbre") {
      var st = rayon.filter(function (x) { return x.id === choix; })[0];
      if (!st) return { ok: false, raison: "arbre" };
      pl.arbreAchete = { stat: st.id, restant: B.arbre_epreuves || 5 };
      out.stat = st.id;
    } else if (article === "avancer") {
      cr.avanceJour = cleJour(t);
      out.plateau = deplacer(contenu, partie, 1, t, "achat");
      if (out.plateau) out.plateau.contextes = contextesPlateau(out.plateau);
    } else if (article === "kit") {
      partie.kit = t;
    } else if (POCHE[article]) {
      var inv = partie.inventaire || (partie.inventaire = {});
      inv[article] = (inv[article] || 0) + 1; out.stock = inv[article];
    }
    cr.solde -= prix;
    cr.achats = (cr.achats || 0) + 1;
    if (out.plateau) out.recompenses = verifierRecompenses(contenu, partie, t);
    var mots = fiche.mots || [];
    if (mots.length) out.mot = mots[tirage(graine + "|mot", mots.length)];
    partie.maj = t;
    return out;
  }
  // v20 : les articles de poche. Joker 50/50 et droit à l'erreur servent en quiz, la relance sur un atome sauvage ;
  // le désarmement se déclenche tout seul sur le prochain piège où le pion s'arrête.
  var POCHE = { joker: 1, erreur: 1, relance: 1, desarme: 1 };
  function enPoche(partie, article) { return (partie.inventaire && partie.inventaire[article]) || 0; }
  function utiliser(partie, article, t) {
    if (!enPoche(partie, article)) return false;
    partie.inventaire[article]--;
    var u = partie.compteurs.objetsPoche || (partie.compteurs.objetsPoche = {});
    u[article] = (u[article] || 0) + 1;
    partie.maj = t;
    return true;
  }
  // Le joker : les mauvais choix d'un QCM à effacer, tous sauf un, tirés au hasard. null si la question ne s'y prête pas.
  function joker(question, alea) {
    if (question.type !== "qcm" || question.choix.length < 3) return null;
    var faux = question.choix.map(function (_, i) { return i; }).filter(function (i) { return i !== question.reponse; });
    faux = melanger(faux, alea || Math.random);
    return faux.slice(1);
  }
  // La relance : l'atome qui attend est remplacé par un autre, tiré de la même façon.
  function relancerAtome(contenu, partie, t) {
    var s = partie.sauvages && partie.sauvages[0]; if (!s || !enPoche(partie, "relance")) return null;
    var e = tirerAtome(contenu, partie, s.case, t + 1);
    if (!e || e.z === s.z) return null;
    utiliser(partie, "relance", t);
    var avant = s.z; s.z = e.z;
    ficheAtome(partie, e.z).rencontres++;
    return { avant: elementZ(contenu, avant), apres: e };
  }

  // --- Emplettes de l'IA (v20) -------------------------------------------------
  // L'argent des ultimatums payés va dans sa bourse. Une fois par jour, une chance sur deux, elle file à la boutique.
  // Elle ne tire pas au hasard : l'objet qui brille le plus, le masque qui la flatte le plus, l'accessoire le plus ridicule
  // pour votre tête, ou un ennemi pour le spectacle. Trop pauvre, elle lèche la vitrine.
  var MAX_EMPLETTES = 10;
  function rayonIA(contenu, partie, article) {
    var E = contenu.ia.credits.emplettes, cr = partie.credits;
    if (article === "masque") {
      var flatte = E.tons_flatteurs || [];
      return enRayon(contenu, partie, "masque").map(function (m) {
        return { chose: m, gout: (m.tons || []).filter(function (x) { return flatte.indexOf(x) >= 0; }).length * 10 + (m.tons || []).length };
      });
    }
    if (article === "objet") {
      var tr = partie.tresorIA || {};
      return (contenu.objets || []).filter(function (o) { return o.cadeau && tr[o.id] == null; }).map(function (o) { return { chose: o, gout: (o.cadeau.eclat || 1) * 10 }; });
    }
    if (article === "farce") {
      var acc = {}, av = partie.avatar || {}; (contenu.avatar && contenu.avatar.accessoires || []).forEach(function (a) { acc[a.id] = a; });
      var f = farceActive(partie, cr.jourEmplettes || 0);
      return (E.farces || []).filter(function (id) { return acc[id] && av[acc[id].emplacement] !== id && !(f && f.id === id); })
        .map(function (id, i, l) { return { chose: acc[id], gout: l.length - i }; });
    }
    if (article === "convoquer") return enRayon(contenu, partie, "convoquer").length ? [{ chose: null, gout: 1 }] : [];
    return [];
  }
  var ARTICLE_EMPLETTE = { masque: "masque", objet: "objet", farce: "accessoire", convoquer: "convoquer" };
  function emplettesIA(contenu, partie, t, alea) {
    var E = contenu.ia && contenu.ia.credits && contenu.ia.credits.emplettes, B = boutique(contenu), cr = partie.credits;
    if (!E || !B || !cr.ia || partie.ultimatum) return null;
    if (cr.jourEmplettes && cleJour(cr.jourEmplettes) === cleJour(t)) return null;
    cr.jourEmplettes = t;
    if ((alea || Math.random)() >= E.chance) return null;
    var graine = "emplettes|" + cleJour(t) + "|" + (partie.journal ? partie.journal.length : 0);
    var choix = Object.keys(E.poids).filter(function (a) { var f = articleDe(contenu, ARTICLE_EMPLETTE[a]); return f && f.prix <= cr.ia && rayonIA(contenu, partie, a).length; });
    var e = { t: t, vu: false };
    if (!choix.length) {
      // Rien à sa portée : la vitrine, une fois seulement tant que la bourse n'a pas grossi.
      if (cr.vitrine === cr.ia) return null;
      cr.vitrine = cr.ia; e.type = "vitrine";
    } else {
      var total = choix.reduce(function (n, a) { return n + E.poids[a]; }, 0), x = tirage(graine, 1000) / 1000 * total, article = choix[choix.length - 1];
      for (var i = 0; i < choix.length; i++) { x -= E.poids[choix[i]]; if (x < 0) { article = choix[i]; break; } }
      // Ce qui l'amuse le plus : le meilleur goût, et parmi les ex æquo, celui du jour.
      var rayon = rayonIA(contenu, partie, article), haut = Math.max.apply(null, rayon.map(function (r) { return r.gout; }));
      var top = rayon.filter(function (r) { return r.gout === haut; }), pris = top[tirage(graine + "|" + article, top.length)].chose;
      e.type = article; e.prix = articleDe(contenu, ARTICLE_EMPLETTE[article]).prix;
      cr.ia -= e.prix;
      cr.depensesIA = (cr.depensesIA || 0) + e.prix;
      if (article === "masque") {
        partie.masques[pris.id] = t; partie.masque = pris.id; e.id = pris.id;
        if (partie.gagnables) delete partie.gagnables[cleButin("masques", pris.id)];
        var fav = faveurIA(contenu, partie, t);
        if (fav) partie.faveur = { valeur: Math.min(100, fav.valeur + Math.round((B.faveur_masque || 0) / 2)), maj: t };
      } else if (article === "objet") {
        (partie.tresorIA || (partie.tresorIA = {}))[pris.id] = t; partie.objetIA = pris.id; e.id = pris.id;
      } else if (article === "farce") {
        partie.farce = { type: "accessoire", id: pris.id, emplacement: pris.emplacement, depuis: t, jusqua: t + DUREE_FARCE, ia: true };
        e.id = pris.id;
      } else {
        var en = ennemisPlateau(contenu, partie), occ = Object.keys(en).map(function (k) { return en[k]; });
        var libres = contenu.ennemis.filter(function (x) { return occ.indexOf(x.id) < 0; }), cases = casesLibres(contenu, partie);
        var ennemi = libres[tirage(graine + "|e", libres.length)], c = cases[Math.min(cases.length - 1, tirage(graine + "|c", Math.min(4, cases.length)))];
        en[c] = ennemi.id; e.id = ennemi.id; e.case = c;
      }
    }
    var mots = (E.mots && E.mots[e.type]) || [];
    if (mots.length) e.mot = mots[tirage(graine + "|mot", mots.length)];
    partie.emplettes = [e].concat(partie.emplettes || []).slice(0, MAX_EMPLETTES);
    partie.maj = t;
    return e;
  }
  function empletteAVoir(partie) { var e = partie.emplettes && partie.emplettes[0]; return e && !e.vu ? e : null; }

  // L'arbre acheté : il remplace celui de la case pour le choix de l'IA, le temps de quelques épreuves.
  function arbreAchete(partie) { var a = partie.plateau && partie.plateau.arbreAchete; return a && a.restant > 0 ? a : null; }
  function consommerArbre(partie, stat) {
    var a = arbreAchete(partie);
    if (a && a.stat === stat) { a.restant--; if (a.restant <= 0) partie.plateau.arbreAchete = null; }
  }

  // --- Cadeaux à l'IA (v7) ---------------------------------------------------
  // Un cadeau par jour, une fois par objet. L'IA répond selon l'objet, garde parfois l'objet sur son masque,
  // et s'en sert sur le plateau : le pion avance ou recule, une case spéciale change de place, un ennemi arrive, ou rien.

  function cadeauPossible(contenu, partie, id, t) {
    var o = (contenu.objets || []).filter(function (x) { return x.id === id; })[0];
    if (!o || !o.cadeau || !partie.objets[id] || !dramaturgie(contenu)) return { ok: false, raison: "inconnu" };
    // v10 : un objet déjà offert peut l'être de nouveau après quelques jours ; l'IA s'en lasse et n'en donne que la moitié.
    var F = contenu.ia && contenu.ia.faveur, dernier = partie.cadeaux.donnes[id];
    if (dernier && (!F || joursEntre(dernier, t) < F.lassitude_jours)) return { ok: false, raison: "recent", jours: F ? F.lassitude_jours - joursEntre(dernier, t) : null };
    if (partie.cadeaux.jour === cleJour(t)) return { ok: false, raison: "jour" };
    return { ok: true, objet: o };
  }

  function donnerObjet(contenu, partie, id, t, alea) {
    var p = cadeauPossible(contenu, partie, id, t); if (!p.ok) return null;
    alea = alea || Math.random;
    var o = p.objet, cd = o.cadeau, pl = partie.plateau, R = contenu.plateau ? contenu.plateau.regles : null;
    var repete = !!partie.cadeaux.donnes[id], avant = faveurIA(contenu, partie, t), gain = 0;
    if (avant) {
      gain = contenu.ia.faveur.gains[String(cd.eclat || 1)] || 0;
      if (repete) gain = Math.round(gain / 2);
      partie.faveur = { valeur: Math.min(100, avant.valeur + gain), maj: t };
    }
    partie.cadeaux.jour = cleJour(t);
    partie.cadeaux.donnes[id] = t;
    partie.compteurs.cadeaux = (partie.compteurs.cadeaux || 0) + 1;
    if (cd.garde) partie.objetIA = id;
    var effet = { type: cd.effet }, dep = null;
    if (R && cd.effet === "avance") { dep = deplacer(contenu, partie, cd.n, t, "cadeau"); effet.n = cd.n; }
    else if (R && cd.effet === "recule") { dep = deplacer(contenu, partie, -cd.n, t, "cadeau"); effet.n = cd.n; }
    else if (R && cd.effet === "echange") {
      // Une case spéciale devant le pion change de place avec une case ordinaire devant lui.
      var ennemis = ennemisPlateau(contenu, partie), devant = [], speciales = [], libres = [];
      devant = devantPion(contenu, partie, 1, Infinity);
      devant.forEach(function (n) {
        var sp = specialDe(contenu, partie, n);
        if (sp && sp.type !== "retour_epoque" && sp.type !== "teleport" && sp.type !== "mendeleiev") speciales.push(n); else if (!sp && !ennemis[n]) libres.push(n);
      });
      if (speciales.length && libres.length) {
        var a = speciales[Math.floor(alea() * speciales.length)], b = libres[Math.floor(alea() * libres.length)];
        var spA = specialDe(contenu, partie, a);
        pl.speciaux[a] = null; pl.speciaux[b] = spA;
        effet.de = a; effet.vers = b; effet.regle = spA.type;
      } else if (libres.length) {
        // Victor (2026-10-31) : plus de case spéciale fixe à déplacer ; Alyca en pose une sur une case devant (piège ou cadeau).
        var E = R.evenements, choixE = ((E && E.pieges) || []).concat([{ type: "cadeau" }]);
        var spN = Object.assign({ evenement: true }, choixE[Math.floor(alea() * choixE.length)]), bN = libres[Math.floor(alea() * libres.length)];
        pl.speciaux[bN] = spN; effet.de = null; effet.vers = bN; effet.regle = spN.type;
      } else effet.type = "rien";
    } else if (R && cd.effet === "ennemi") {
      var en = ennemisPlateau(contenu, partie), presents = Object.keys(en).map(function (k) { return en[k]; });
      var absents = contenu.ennemis.map(function (x) { return x.id; }).filter(function (x) { return presents.indexOf(x) < 0; });
      if (absents.indexOf(contenu.reserve) >= 0) absents = [contenu.reserve];
      var cases = [];
      devantPion(contenu, partie, 3, 12).forEach(function (m) { if (!en[m] && !specialDe(contenu, partie, m)) cases.push(m); });
      if (absents.length && cases.length) {
        var c = cases[Math.floor(alea() * cases.length)];
        en[c] = absents[Math.floor(alea() * absents.length)];
        effet.case = c; effet.ennemi = contenu.ennemiParId[en[c]];
      } else effet.type = "rien";
    }
    if (dep) dep.contextes = contextesPlateau(dep);
    var rec = verifierRecompenses(contenu, partie, t);
    partie.maj = t;
    return { objet: o, texte: cd.texte, garde: !!cd.garde, effet: effet, plateau: dep, recompenses: rec,
      eclat: cd.eclat || 1, repete: repete, gain: gain, avant: avant, faveur: faveurIA(contenu, partie, t) };
  }

  // --- Crédits et pots-de-vin (v16) -------------------------------------------
  // Chaque succès rapporte des crédits : un tarif selon son genre (petit, jalon, exploit, monument, honte),
  // multiplié par l'humeur de l'IA, tirée au sort et penchée par sa faveur. Elle commente son choix.
  function tarifSucces(contenu, sc) {
    var K = contenu.ia && contenu.ia.credits; if (!K) return 0;
    var g = K.genres[sc.condition && sc.condition.type] || "jalon", n = K.bareme[g] || 0;
    return Math.round(n * (sc.cache ? K.bonus_cache : 1));
  }
  function crediterSucces(contenu, partie, sc) {
    var K = contenu.ia && contenu.ia.credits; if (!K) return null;
    var base = tarifSucces(contenu, sc), g = K.genres[sc.condition && sc.condition.type] || "jalon";
    var h = hacher(sc.id + "|" + (partie.cree || 0) + "|" + (partie.journal ? partie.journal.length : 0)), r = (h % 1000) / 1000;
    var humeur, mots, facteur;
    // Sans dramaturgie (pas d'humeurs), le tarif est versé tel quel, sans commentaire.
    if (!K.humeurs || !K.humeurs.length) {
      partie.credits.solde += base; partie.credits.gagnes += base;
      partie.credits.parSucces[sc.id] = { n: base, base: base, humeur: null, mot: null };
      return { succes: sc.id, n: base, base: base, humeur: null, mot: null };
    }
    if (g === "honte" && K.honte && r < K.honte.chance) { humeur = "honte"; facteur = K.honte.facteur; mots = K.honte.mots; }
    else {
      var fav = partie.faveur ? partie.faveur.valeur : 60, col = fav >= 75 ? 3 : fav >= 45 ? 2 : fav >= 20 ? 1 : 0;
      var total = 0; K.humeurs.forEach(function (x) { total += x.poids[col]; });
      var tir = ((h >>> 10) % 1000) / 1000 * total, choix = K.humeurs[0];
      for (var i = 0; i < K.humeurs.length; i++) { tir -= K.humeurs[i].poids[col]; if (tir < 0) { choix = K.humeurs[i]; break; } }
      humeur = choix.id; facteur = choix.facteur; mots = choix.mots;
    }
    var n = Math.round(base * facteur);
    partie.credits.solde += n; partie.credits.gagnes += n;
    var mot = mots[(h >>> 20) % mots.length];
    // v32 (Victor) : le verdict de l'humeur, puis une pique sur le sujet même du succès.
    var pique = K.piques && K.piques[sc.id], verdicts = K.verdicts && K.verdicts[humeur];
    if (pique && verdicts && verdicts.length) {
      var v = verdicts[(h >>> 20) % verdicts.length];
      mot = { fr: TX(v) + " " + TX(pique) };
    }
    partie.credits.parSucces[sc.id] = { n: n, base: base, humeur: humeur, mot: mot };
    return { succes: sc.id, n: n, base: base, humeur: humeur, mot: mot };
  }
  // Chaque erreur agace l'IA ; une épreuve ratée encore plus. Renvoie la perte (ou le gain, sans faute) de faveur, ou null.
  function agacerIA(contenu, partie, erreurs, ratee, t, cle) {
    var A = contenu.ia && contenu.ia.credits && contenu.ia.credits.agacement, avant = faveurIA(contenu, partie, t);
    if (!A || !avant) return null;
    var perte = Math.min(A.max, Math.max(0, erreurs) * A.par_erreur + (ratee ? A.epreuve_ratee : 0));
    // v31 : réussie malgré des fautes, elle reste contente (un peu).
    if (!ratee && perte && A.reussi) {
      partie.faveur = { valeur: Math.min(100, avant.valeur + A.reussi), maj: t };
      return { perte: 0, gain: A.reussi, raison: "reussi", avant: avant, apres: faveurIA(contenu, partie, t) };
    }
    // v28 : sans faute, elle vous aime un peu plus. Un peu.
    // v31 : `cle` choisit un autre gain (duel_gagne : un ennemi battu la ravit).
    var g = (cle && A[cle]) || A.sans_faute;
    if (!perte && !ratee && g) {
      partie.faveur = { valeur: Math.min(100, avant.valeur + g), maj: t };
      return { perte: 0, gain: g, raison: cle && A[cle] ? cle : "sans_faute", avant: avant, apres: faveurIA(contenu, partie, t) };
    }
    if (!perte) return null;
    partie.faveur = { valeur: Math.max(0, avant.valeur - perte), maj: t };
    return { perte: perte, avant: avant, apres: faveurIA(contenu, partie, t) };
  }
  function potPossible(contenu, partie, montant, t) {
    if (!contenu.ia || !contenu.ia.credits || !contenu.ia.credits.pots) return { ok: false, raison: "inconnu" };
    if (partie.credits.jour === cleJour(t)) return { ok: false, raison: "jour" };
    montant = Math.floor(Number(montant));
    if (!(montant > 0)) return { ok: false, raison: "montant" };
    if (montant > partie.credits.solde) return { ok: false, raison: "solde" };
    return { ok: true, montant: montant };
  }
  // Un pot-de-vin par jour. Au-dessus de son record, elle est ravie : faveur pleine et le pion avance.
  // Égal au record, la moitié de la faveur. En dessous, elle garde l'argent, se vexe et pose un piège.
  function corrompre(contenu, partie, montant, t) {
    var p = potPossible(contenu, partie, montant, t); if (!p.ok) return p;
    var K = contenu.ia.credits.pots, cr = partie.credits, m = p.montant, record = cr.record || 0;
    var issue = !cr.pots ? "premier" : m > record ? "genereux" : m === record ? "egal" : "radin";
    var avant = faveurIA(contenu, partie, t), gain = 0, dep = null, piege = null;
    cr.solde -= m; cr.jour = cleJour(t); cr.pots = (cr.pots || 0) + 1; cr.dernier = m; cr.record = Math.max(record, m);
    if (issue === "radin") {
      gain = -K.colere;
      if (avant) partie.faveur = { valeur: Math.max(0, avant.valeur - K.colere), maj: t };
      if (contenu.plateau) {
        var en = ennemisPlateau(contenu, partie), libres = [];
        devantPion(contenu, partie, 1, 5).forEach(function (n) { if (!specialDe(contenu, partie, n) && !en[n]) libres.push(n); });
        if (libres.length) {
          piege = libres[0];
          partie.plateau.speciaux[piege] = { type: K.piege.type, n: K.piege.n, ia: true, raison: { fr: "Posé par l'IA : votre dernier pot-de-vin était plus petit que le précédent. Elle a de la mémoire." } };
        }
      }
    } else {
      gain = Math.min(K.gain_max, Math.round(K.gain_base + m * K.gain_par_credit));
      if (issue === "egal") gain = Math.round(gain / 2);
      if (avant) partie.faveur = { valeur: Math.min(100, avant.valeur + gain), maj: t };
      if (issue !== "egal" && contenu.plateau && (K.avance || K.avance_double)) {
        var pas = record && m >= 2 * record ? K.avance_double : K.avance;
        dep = deplacer(contenu, partie, pas, t, "pot");
        if (dep) dep.contextes = contextesPlateau(dep);
      }
    }
    var rec = verifierRecompenses(contenu, partie, t);
    partie.maj = t;
    return { ok: true, montant: m, issue: issue, record: record, gain: gain, avant: avant, faveur: faveurIA(contenu, partie, t), plateau: dep, piege: piege, recompenses: rec };
  }

  // --- Ultimatum (v17) ---------------------------------------------------------
  // Une fois de temps en temps, l'IA exige une grosse somme de crédits. Payer : elle est contente, et sa
  // prochaine exigence sera plus haute. Refuser : elle verse elle-même la somme, mais retire de vrais niveaux.
  function exigence(contenu, partie) {
    var U = contenu.ia.credits.ultimatum, cr = partie.credits;
    return Math.max(U.plancher, Math.ceil((cr.exigence || 0) * U.hausse), Math.ceil(cr.solde * U.part_solde));
  }
  function tenterUltimatum(contenu, partie, t, alea) {
    var U = contenu.ia && contenu.ia.credits && contenu.ia.credits.ultimatum, cr = partie.credits;
    if (!U || reglage(partie, "ultimatum") === false || partie.ultimatum || cr.solde < U.solde_min || niveauGlobal(contenu, partie) < 1) return null;
    if (cr.jourUltimatum && joursEntre(cr.jourUltimatum, t) < U.delai_jours) return null;
    cr.jourUltimatum = t;
    if ((alea || Math.random)() >= U.chance) return null;
    partie.ultimatum = { demande: exigence(contenu, partie), niveaux: U.niveaux, depuis: t };
    return partie.ultimatum;
  }
  // Retire de vrais niveaux : l'arbre le plus haut perd assez d'XP pour redescendre d'un niveau, autant de fois que demandé.
  function retirerNiveaux(contenu, partie, n) {
    var p = contenu.regles.xp.paliers_niveau, perdus = 0;
    for (var i = 0; i < n; i++) {
      var xp = xpParStat(contenu, partie), haut = null;
      contenu.stats.forEach(function (st) { var nv = niveau(contenu, xp[st.id]).niveau; if (nv > 0 && (!haut || nv > haut.nv)) haut = { id: st.id, nv: nv }; });
      if (!haut) break;
      var trop = xp[haut.id] - (p[haut.nv] - 1);
      (contenu.parStat[haut.id] || []).map(function (k) { return partie.competences[k.id]; })
        .filter(function (e) { return e && e.maitrise && e.xp > 0; }).sort(function (a, b) { return b.xp - a.xp; })
        .forEach(function (e) { if (trop <= 0) return; var r = Math.min(e.xp, trop); e.xp -= r; trop -= r; });
      perdus++;
    }
    return perdus;
  }
  function repondreUltimatum(contenu, partie, paye, t) {
    var u = partie.ultimatum; if (!u) return null;
    var U = contenu.ia.credits.ultimatum, cr = partie.credits, avant = niveauGlobal(contenu, partie), fav = faveurIA(contenu, partie, t);
    if (paye && cr.solde < u.demande) return { ok: false, raison: "solde" };
    partie.ultimatum = null;
    var out = { ok: true, paye: paye, demande: u.demande, niveauAvant: avant };
    if (paye) {
      cr.solde -= u.demande; cr.exigence = u.demande;
      cr.ia = (cr.ia || 0) + u.demande;
      if (fav) partie.faveur = { valeur: Math.min(100, fav.valeur + U.faveur_paye), maj: t };
    } else {
      cr.solde += u.demande; cr.gagnes += u.demande;
      out.perdus = retirerNiveaux(contenu, partie, u.niveaux);
    }
    out.niveauApres = niveauGlobal(contenu, partie);
    partie.maj = t;
    return out;
  }

  // --- Faveur de l'IA (v10) ----------------------------------------------------
  // Une jauge de 0 à 100, qui baisse chaque jour. Les cadeaux la font remonter selon leur éclat.
  // Le palier (comblée, contente, boudeuse, furieuse) change le butin, l'avancée et, furieuse, pose des pièges.
  function faveurIA(contenu, partie, t) {
    var F = contenu.ia && contenu.ia.faveur; if (!F) return null;
    if (!partie.faveur) partie.faveur = { valeur: F.depart, maj: t };
    // v27 : tombée à 0 (erreurs, pot-de-vin radin), elle ferme le jeu pour la journée ; le lendemain, elle remonte d'elle-même.
    if (partie.faveur.valeur <= 0 && joursEntre(partie.faveur.maj, t) >= 1) partie.faveur = { valeur: F.remontee || 25, maj: debutJour(t), remontee: cleJour(t) };
    var jours = Math.max(0, joursEntre(partie.faveur.maj, t));
    // La baisse quotidienne seule ne descend pas sous 1 : l'absence la rend furieuse, pas muette.
    var valeur = partie.faveur.valeur <= 0 ? 0 : Math.max(Math.min(1, partie.faveur.valeur), partie.faveur.valeur - F.baisse_par_jour * jours);
    var palier = F.paliers.filter(function (p) { return valeur >= p.min; })[0] || F.paliers[F.paliers.length - 1];
    // v28 : chaque chute sous un palier (boudeuse, furieuse, puis 0) l'envoie vous enfermer au mur de la honte.
    var rang = valeur <= 0 ? F.paliers.length : F.paliers.indexOf(palier);
    if (partie.humeurRang == null || rang < partie.humeurRang) partie.humeurRang = rang;
    else if (rang > partie.humeurRang) { enfermer(contenu, partie, rang, t); partie.humeurRang = rang; }
    // v25 : comblée pour la première fois, elle donne son nom. Pour de bon : fâchée, elle le reproche sans le reprendre.
    if (palier.id === "comblee" && !partie.alyca && contenu.ia.alyca) partie.alyca = { depuis: t, vu: false };
    return { valeur: valeur, palier: palier, fermee: valeur <= 0, demain: valeur <= 0 ? (F.remontee || 25) : Math.max(1, valeur - F.baisse_par_jour),
      cadeauDuJour: partie.cadeaux.jour === cleJour(t) };
  }
  // v28 : enfermé au mur de la honte. La peine dépend du palier franchi et double à chaque nouvelle chute du jour ;
  // elle s'ajoute à celle qui reste. Le temps ne s'écoule que mur affiché (purger, appelé par l'interface).
  function enfermer(contenu, partie, rang, t) {
    var M_ = contenu.ia.faveur.mur, ids = contenu.ia.faveur.paliers.map(function (p) { return p.id; }).concat("nulle");
    var min = M_ && M_[ids[rang]]; if (!min) return null;
    if (!partie.chutes || partie.chutes.jour !== cleJour(t)) partie.chutes = { jour: cleJour(t), n: 0 };
    partie.chutes.n++;
    var ms = min * 60000 * Math.pow(2, partie.chutes.n - 1), p = partie.punition, max = (contenu.ia.faveur.mur_max || Infinity) * 60000;
    // v29 : plafond de la peine en attente (mur_max minutes).
    ms = Math.max(0, Math.min(ms, max - (p ? p.restant : 0)));
    partie.punition = p ? { restant: p.restant + ms, total: p.total + ms, palier: rang > p.rang ? ids[rang] : p.palier, rang: Math.max(rang, p.rang), depuis: p.depuis, n: partie.chutes.n }
      : { restant: ms, total: ms, palier: ids[rang], rang: rang, depuis: t, n: partie.chutes.n };
    return partie.punition;
  }
  // Retire `ms` à la peine ; renvoie ce qui reste (0 : libéré).
  function purger(partie, ms) {
    if (!partie.punition) return 0;
    partie.punition.restant = Math.max(0, partie.punition.restant - ms);
    if (!partie.punition.restant) { partie.punition = null; return 0; }
    return partie.punition.restant;
  }
  // v29 (Victor) : au mur, des questions de rattrapage tirées des thèmes du jour (erreurs, puis fiches imposées).
  // Chacune réussie retire mur_rattrapage minutes à la peine ; ratée, elle ne coûte rien de plus que la honte.
  function themesCorvee(contenu, partie, t) {
    var ids = [], vu = {};
    murDeLaHonte(contenu, partie, t).aujourdhui.forEach(function (x) { var c = x.question.competence; if (!vu[c]) { vu[c] = true; ids.push(c); } });
    fichesImposees(contenu, partie, t, 3).forEach(function (k) { if (!vu[k.id]) { vu[k.id] = true; ids.push(k.id); } });
    return ids;
  }
  // La question en cours, tirée une fois et gardée jusqu'à la réponse ; null hors peine.
  function questionRattrapage(contenu, partie, t, alea) {
    var p = partie.punition; if (!p || !(p.restant > 0)) return null;
    if (p.q && contenu.questionParId[p.q]) return contenu.questionParId[p.q];
    var themes = themesCorvee(contenu, partie, t), vues = {};
    (p.vues || []).forEach(function (id) { vues[id] = true; });
    var dans = contenu.questions.filter(function (q) { return themes.indexOf(q.competence) >= 0; });
    var neuves = dans.filter(function (q) { return !vues[q.id]; });
    var vu = croisees(contenu, partie), connues = contenu.questions.filter(function (q) { return vu[q.competence]; });
    var choix = neuves.length ? neuves : dans.length ? dans : connues;
    if (!choix.length) return null;
    p.q = choix[Math.floor((alea || Math.random)() * choix.length)].id;
    return contenu.questionParId[p.q];
  }
  function repondreRattrapage(contenu, partie, correct, t) {
    var p = partie.punition; if (!p || !p.q) return null;
    p.vues = (p.vues || []).concat(p.q).slice(-40);
    p.q = null;
    var ms = correct ? (contenu.ia.faveur.mur_rattrapage || 1) * 60000 : 0, reste = ms ? purger(partie, ms) : p.restant;
    partie.maj = t;
    return { gagne: ms, reste: reste, libere: !reste, replique: reste ? replique(contenu, partie, [correct ? "rattrapage_reussi" : "rattrapage_rate"]) : null };
  }
  // v32 (Victor) : « Piège ! » Une question difficile (compétence du second losange, pas de vrai/faux),
  // tirée d'abord parmi celles qu'évoque la case, puis dans son arbre. Juste : le piège est déjoué. Faux : il se déclenche.
  function piegeEnAttente(partie) { var p = partie.piege; return !!(p && partie.plateau && p.case === partie.plateau.position); }
  function questionPiege(contenu, partie, alea) {
    if (!piegeEnAttente(partie)) return null;
    var p = partie.piege;
    if (p.q && contenu.questionParId[p.q]) return contenu.questionParId[p.q];
    var R = contenu.plateau.regles.question_piege || {}, rangMin = R.rang_min || 5;
    var dures = contenu.questions.filter(function (q) { var k = contenu.parId[q.competence]; return q.type !== "vrai_faux" && k && k.rang >= rangMin; });
    var k = caseN(contenu, p.case), CC = contenu.plateau.competences_cases, evoque = (CC && CC[String(p.case)]) || [];
    var choix = dures.filter(function (q) { return evoque.indexOf(q.competence) >= 0; });
    if (!choix.length && k && k.stat) choix = dures.filter(function (q) { return contenu.parId[q.competence].stat === k.stat; });
    if (!choix.length) choix = dures.length ? dures : contenu.questions;
    p.q = choix[Math.floor((alea || Math.random)() * choix.length)].id;
    return contenu.questionParId[p.q];
  }
  function repondrePiege(contenu, partie, correct, t) {
    if (!piegeEnAttente(partie)) return null;
    var p = partie.piege, c = partie.compteurs;
    if (correct) {
      partie.piege = null; c.piegesDejoues = (c.piegesDejoues || 0) + 1; partie.maj = t;
      return { dejoue: true, case: p.case, regle: p.regle.type, replique: replique(contenu, partie, ["piege_dejoue"]) };
    }
    var dep = deplacer(contenu, partie, 0, t, "piege");
    dep.contextes = contextesPlateau(dep);
    return { dejoue: false, case: p.case, regle: p.regle.type, plateau: dep, ile: exodeIle(contenu, partie, t), replique: replique(contenu, partie, ["piege_declenche"]), recompenses: verifierRecompenses(contenu, partie, t) };
  }
  // --- Chrono, le jeu des siècles (v34) ----------------------------------------
  // Alyca présente un événement déjà débloqué (frise, livre, savant, objet) ; le joueur dit quand il s'est produit.
  // Chaque événement a son niveau : siècle, demi-siècle, décennie, année exacte (plateau.json regles.chrono.niveaux).
  // Deux justes de suite le font monter d'un cran, une erreur le fait redescendre. Juste : des crédits ; proche : un peu.
  // Deux portes : une case Chrono (la partie sert d'épreuve de la case) ou Alyca, d'elle-même, une fois par jour au plus.
  function reglesChrono(contenu) { return contenu.plateau && contenu.plateau.regles && contenu.plateau.regles.chrono || null; }
  function etatChrono(partie) {
    return partie.siecles || (partie.siecles = { fiches: {}, case: null, offre: null, joueJour: null, jeu: null,
      parties: 0, parfaits: 0, justes: 0, proches: 0, faux: 0, rapides: 0, exactes: 0, maxExactes: 0 });
  }
  // Créneau d'une année pour un pas donné, en suivant le calendrier (pas d'an zéro) :
  // pas 100 et 50 : siècles et demi-siècles au sens propre (1901-2000 = XXe) ; pas 10 : décennies (1680-1689) ; pas 1 : l'année.
  // Avant `prehistoire`, une seule case : la Préhistoire.
  function creneau(annee, pas, prehistoire) {
    var y = Number(annee);
    if (prehistoire != null && y < prehistoire) return creneau(prehistoire, pas, null) - 1;
    if (pas >= 50) return y > 0 ? Math.floor((y - 1) / pas) : -Math.floor((-y - 1) / pas) - 1;
    if (pas === 1) return y > 0 ? y - 1 : y;
    return y > 0 ? Math.floor(y / pas) : -Math.floor((-y - 1) / pas) - 1;
  }
  // Une année du créneau `k`, la première : ce que l'interface renvoie pour un siècle ou une décennie choisis.
  function anneeDuCreneau(k, pas) {
    if (pas >= 50) return k >= 0 ? k * pas + 1 : k * pas;
    if (pas === 1) return k >= 0 ? k + 1 : k;
    return k >= 0 ? Math.max(1, k * pas) : k * pas;
  }
  function chiffreRomain(n) {
    var v = [[1000, "M"], [900, "CM"], [500, "D"], [400, "CD"], [100, "C"], [90, "XC"], [50, "L"], [40, "XL"], [10, "X"], [9, "IX"], [5, "V"], [4, "IV"], [1, "I"]], s = "";
    v.forEach(function (x) { while (n >= x[0]) { s += x[1]; n -= x[0]; } });
    return s;
  }
  // Le rang d'un siècle : « XVIIe », « Ier » en français, « 17th », « 1st » en anglais.
  function ordinalSiecle(n) {
    if (LANGUE === "en") return n + (n % 100 >= 11 && n % 100 <= 13 ? "th" : ["th", "st", "nd", "rd"][n % 10] || "th");
    return chiffreRomain(n) + (n === 1 ? "er" : "e");
  }
  function texteSiecle(k) { return k >= 0 ? __("{o} siècle", { o: ordinalSiecle(k + 1) }) : __("{o} siècle av. J.-C.", { o: ordinalSiecle(-k) }); }
  // Le libellé d'un créneau : « XVIIe siècle », « 2de moitié du XVIIe siècle », « 1680-1689 », « 585 av. J.-C. ».
  function texteCreneau(k, pas, prehistoire) {
    if (prehistoire != null && k < creneau(prehistoire, pas, null)) return __("Préhistoire (avant {a} av. J.-C.)", { a: -prehistoire });
    if (pas === 100) return texteSiecle(k);
    if (pas === 50) { var c = Math.floor(k / 2); return k - 2 * c ? __("2de moitié du {siecle}", { siecle: texteSiecle(c) }) : __("1re moitié du {siecle}", { siecle: texteSiecle(c) }); }
    if (pas === 1) { var y = anneeDuCreneau(k, 1); return y > 0 ? String(y) : __("{a} av. J.-C.", { a: -y }); }
    var a = anneeDuCreneau(k, pas), b = k >= 0 ? k * pas + pas - 1 : k * pas + pas - 1;
    return a > 0 ? a + "-" + b : __("{a} à {b} av. J.-C.", { a: -a, b: -b });
  }
  // Une phrase qui donnerait la date (un nombre de trois ou quatre chiffres) n'est pas montrée.
  function sansDate(o) { var x = o && TX(o); return x && !/\d{3,4}/.test(x) ? x : null; }
  // « vers 370 / 415 », « -384 / -322 », « vers -2650 » → {debut, fin, vers}.
  function lireAnnees(s) {
    var parts = String(s || "").split("/"), vers = /vers/.test(s);
    var n = parts.map(function (p) { var m = p.match(/-?\d+/); return m ? Number(m[0]) : null; });
    if (n[0] == null) return null;
    return { debut: n[0], fin: n[1] != null ? n[1] : n[0], vers: vers || n[1] == null, naissanceVers: /vers/.test(parts[0]) || n[1] == null };
  }
  // Tout ce que le joueur a débloqué et qui porte une date : le réservoir de Chrono.
  function reservoirChrono(contenu, partie) {
    var R = reglesChrono(contenu); if (!R) return [];
    var out = [], pre = R.prehistoire, maxN = R.niveaux.length, cc = contenu.plateau && contenu.plateau.competences_cases || {};
    // Victor (2026-11-01) : seulement ce qui tient à une compétence déjà apprise (sa condition, ou la compétence de sa case).
    function arbreAppris(st) { return !!(st && contenu.parStat[st] && contenu.parStat[st].some(function (k) { return estMaitrisee(partie, k.id); })); }
    function appris(c, o) {
      if (!c) return false;
      if (c.type === "competence_maitrisee") return estMaitrisee(partie, c.id);
      // Une case sans compétence propre : il faut au moins une compétence apprise dans son arbre.
      if (c.type === "case_atteinte") return cc[String(c.n)] ? cc[String(c.n)].some(function (id) { return estMaitrisee(partie, id); }) : arbreAppris(o.stat || o.theme);
      if (c.type === "branche_complete") return true;
      // Autre condition (un succès, les tours…) : l'arbre de la chose doit avoir au moins une compétence apprise.
      return arbreAppris(o.stat || o.theme);
    }
    var source = {};
    (contenu.evenements || []).forEach(function (e) { source["frise:" + e.id] = e; });
    (contenu.livres || []).forEach(function (e) { source["livre:" + e.id] = e; });
    (contenu.avatar && contenu.avatar.savants || []).forEach(function (e) { source["savant:" + e.id] = e; });
    (contenu.objets || []).forEach(function (e) { source["objet:" + e.id] = e; });
    function ajouter(x) {
      var o = source[x.cle]; if (!o || !appris(o.condition, o)) return; if (x.debut < pre) x.max = 1; x.theme = x.theme || x.stat || null;
      // Ce qui relie la chose au plateau : sa case, et la compétence dont elle dépend.
      var c = o.condition || {};
      x.lienCase = o.case || (c.type === "case_atteinte" ? c.n : null);
      x.lienComp = o.competence || (c.type === "competence_maitrisee" ? c.id : null);
      out.push(x);
    }
    (contenu.evenements || []).forEach(function (e) {
      if (partie.evenements && partie.evenements[e.id] != null && e.annee != null)
        ajouter({ cle: "frise:" + e.id, sorte: "frise", id: e.id, titre: TX(e.titre), texte: sansDate(e.phrase), debut: e.annee, fin: e.annee, max: e.date ? 1 : maxN, source: e.source, case: e.case || null, stat: e.stat });
    });
    (contenu.livres || []).forEach(function (l) {
      if (partie.livres && partie.livres[l.id] != null && l.annee != null)
        ajouter({ cle: "livre:" + l.id, sorte: "livre", id: l.id, titre: TX(l.titre), auteur: l.auteur, texte: null, debut: l.annee, fin: l.annee, max: l.date ? 1 : maxN, source: l.source, stat: l.stat });
    });
    (contenu.avatar && contenu.avatar.savants || []).forEach(function (s) {
      var a = partie.savants && partie.savants[s.id] != null && lireAnnees(s.annees);
      // Pour un savant, tout siècle de sa vie compte juste ; en mode année exacte, on demande sa naissance (Victor).
      if (a) ajouter({ cle: "savant:" + s.id, sorte: "savant", id: s.id, titre: TX(s.nom), texte: null, debut: a.debut, fin: a.fin, max: a.naissanceVers ? 2 : maxN, source: s.source, theme: s.theme });
    });
    (contenu.objets || []).forEach(function (o) {
      if (partie.objets && partie.objets[o.id] != null && o.annee != null)
        ajouter({ cle: "objet:" + o.id, sorte: "objet", id: o.id, titre: TX(o.nom), texte: sansDate(o.notice), debut: o.annee, fin: o.annee, max: maxN, source: o.source, theme: o.theme });
    });
    return out;
  }
  // La case du pion attend sa partie de Chrono.
  function chronoEnAttente(partie) { var s = partie.siecles; return !!(s && chronoActif(partie) && s.case && partie.plateau && s.case === partie.plateau.position); }
  // Alyca propose une partie aujourd'hui (et elle n'est pas encore jouée).
  function offreChrono(partie, t) { var s = partie.siecles; return !!(s && chronoActif(partie) && s.offre && s.offre === cleJour(t)); }
  // Victor (2026-11-01) : désactivable dans les Réglages (options.jeuChrono), et jamais avant la 5e case du premier tour.
  function chronoActif(partie) { return !(partie.options && partie.options.jeuChrono === false); }
  function chronoPossible(contenu, partie) {
    var R = reglesChrono(contenu), pl = partie.plateau || {};
    if (!R || !chronoActif(partie)) return false;
    if (!pl.tours && (pl.idx || 0) < (R.case_min || 5)) return false;
    return reservoirChrono(contenu, partie).length >= R.min_reservoir;
  }
  // Après une épreuve : Alyca lance-t-elle une partie d'elle-même ? Une chance sur trois, une fois par jour au plus.
  function chronoSpontane(contenu, partie, t, alea) {
    var R = reglesChrono(contenu); if (!R || !chronoActif(partie)) return false;
    var s = etatChrono(partie), jour = cleJour(t);
    if (s.offre === jour) return true;
    if (s.joueJour === jour || chronoEnAttente(partie) || s.jeu || !chronoPossible(contenu, partie)) return false;
    // Sans `alea`, le tirage dépend du jour et du journal : le même résultat à chaque affichage d'un même bilan.
    if ((alea ? alea() : tirage(jour + "|chrono|" + partie.journal.length, 1000) / 1000) >= R.spontane) return false;
    s.offre = jour; partie.maj = t;
    return true;
  }
  function niveauChrono(R, n) { return R.niveaux[Math.max(1, Math.min(n, R.niveaux.length)) - 1]; }
  // Lance (ou reprend) une partie. `mode` : « case » (case Chrono du pion) ou « alyca » (proposée par elle aujourd'hui).
  // Tirage : d'abord les événements ratés la dernière fois, puis les jamais vus, puis les plus anciennement vus ;
  // pas deux du même siècle tant que c'est possible, pour que la frise s'étale.
  function lancerChrono(contenu, partie, mode, t, alea) {
    var R = reglesChrono(contenu); if (!R) return null;
    var s = etatChrono(partie);
    if (s.jeu && s.jeu.mode === mode && s.jeu.reponses.length < s.jeu.questions.length) return s.jeu;
    // Mode Île : une partie de Chrono par jour, lancée depuis l'île pour bâtir les monuments.
    if (mode === "case" ? !chronoEnAttente(partie) : mode === "ile" ? !(modeIle(partie) && s.ileJour !== cleJour(t)) : !offreChrono(partie, t)) return null;
    var pool = reservoirChrono(contenu, partie);
    // Trop peu d'éléments datés : la case ne retient pas le pion.
    if (pool.length < R.min_reservoir) { if (mode === "case") s.case = null; return null; }
    alea = alea || Math.random;
    // Victor (2026-11-01) : l'arbre de la partie d'abord (celui de la case) ; les autres arbres ne font que compléter.
    // Victor (2026-11-01) : Chrono se joue avant la case ; il revient sur les cases déjà passées (leur date, leur compétence).
    var pl = partie.plateau || {}, cc = contenu.plateau && contenu.plateau.competences_cases || {}, passees = {}, compsPassees = {};
    Object.keys(pl.visites || {}).forEach(function (n) { if (+n !== pl.position) { passees[n] = 1; (cc[n] || []).forEach(function (id) { compsPassees[id] = 1; }); } });
    var passe = function (x) { return !!((x.lienCase != null && passees[x.lienCase]) || (x.lienComp && compsPassees[x.lienComp])); };
    var th = themeCase(contenu, partie);
    var dejaVu = pool.filter(passe), memeArbre = th ? pool.filter(function (x) { return x.theme === th; }) : [];
    if (dejaVu.length >= R.evenements) pool = dejaVu;
    else if (dejaVu.length + memeArbre.length >= R.evenements) pool = pool.filter(function (x) { return passe(x) || x.theme === th; });
    var prio = function (x) { var f = s.fiches[x.cle]; return (passe(x) ? 20 : 0) + (th && x.theme === th ? 10 : 0) + (!f ? 2 : f.rate ? 3 : 1); };
    var tries = melanger(pool, alea).sort(function (a, b) {
      var pa = prio(a), pb = prio(b);
      if (pa !== pb) return pb - pa;
      return pa % 10 === 1 ? (s.fiches[a.cle].dernier || 0) - (s.fiches[b.cle].dernier || 0) : 0;
    });
    var choix = [], siecles = {};
    // Des siècles tous différents d'abord, en puisant dans les trois listes ; on ne complète avec un siècle déjà pris
    // qu'ensuite (avant, la liste du thème se remplissait de doublons avant de regarder les autres).
    var listes = [tries.filter(passe), tries.filter(function (x) { return th && x.theme === th; }), tries];
    listes.forEach(function (liste) {
      liste.forEach(function (x) { var k = creneau(x.debut, 100, R.prehistoire); if (choix.length < R.evenements && !siecles[k] && choix.indexOf(x) < 0) { siecles[k] = 1; choix.push(x); } });
    });
    listes.forEach(function (liste) {
      liste.forEach(function (x) { if (choix.length < R.evenements && choix.indexOf(x) < 0) choix.push(x); });
    });
    s.jeu = { mode: mode, depuis: t, case: mode === "case" ? s.case : null, reponses: [], questions: choix.map(function (x) {
      var f = s.fiches[x.cle], n = Math.min(f ? f.niveau : 1, x.max), N = niveauChrono(R, n);
      return Object.assign({}, x, { niveau: n, pas: N.pas, proche: N.proche, nomNiveau: TX(N.nom), naissance: x.sorte === "savant" && N.pas < 50 });
    }) };
    partie.maj = t;
    return s.jeu;
  }
  function jeuChrono(partie) { var s = partie.siecles; return s && s.jeu || null; }
  // Corrige la réponse à la question en cours. `annee` : l'année choisie (la première du créneau suffit) ; `ms` : temps de réponse.
  function repondreChrono(contenu, partie, annee, ms, t) {
    var R = reglesChrono(contenu), s = etatChrono(partie), j = s.jeu;
    if (!R || !j || j.reponses.length >= j.questions.length) return null;
    var q = j.questions[j.reponses.length], pre = R.prehistoire, pas = q.pas;
    var g = creneau(annee, pas, pre), a = creneau(q.debut, pas, pre), b = q.naissance ? a : creneau(q.fin, pas, pre);
    var d = g < a ? a - g : g > b ? g - b : 0;
    var verdict = d === 0 ? "juste" : d <= q.proche ? "proche" : "faux", rapide = verdict === "juste" && typeof ms === "number" && ms < R.rapide_ms;
    var P = R.points, points = verdict === "juste" ? P.juste + (rapide ? P.rapide : 0) : verdict === "proche" ? P.proche : 0;
    var f = s.fiches[q.cle] || (s.fiches[q.cle] = { niveau: 1, serie: 0, vus: 0, justes: 0, dernier: null, rate: false });
    var avant = f.niveau;
    f.vus++; f.dernier = t;
    if (verdict === "juste") {
      f.justes++; f.serie++; f.rate = false;
      if (f.serie >= R.monter && f.niveau < q.max) { f.niveau++; f.serie = 0; }
      s.justes++; if (rapide) s.rapides++; if (pas === 1) s.exactes++;
    } else if (verdict === "proche") { f.serie = 0; f.rate = false; s.proches++; }
    else { f.serie = 0; f.rate = true; f.niveau = Math.max(1, f.niveau - 1); s.faux++; }
    var r = { cle: q.cle, annee: Number(annee), choisi: texteCreneau(g, pas, pre), verdict: verdict, rapide: rapide, points: points, ecart: d,
      vrai: q.naissance || q.debut === q.fin ? texteCreneau(a, pas, pre) : texteCreneau(a, pas, pre) + " → " + texteCreneau(b, pas, pre),
      niveauAvant: avant, niveauApres: f.niveau, ms: ms };
    j.reponses.push(r);
    partie.maj = t;
    return r;
  }
  // Fin de partie : crédits (selon l'humeur d'Alyca, comme le butin), faveur, et sur une case Chrono, l'épreuve.
  function terminerChrono(contenu, partie, t, alea) {
    var R = reglesChrono(contenu), s = etatChrono(partie), j = s.jeu;
    if (!R || !j || j.reponses.length < j.questions.length) return null;
    s.jeu = null;
    var total = j.questions.length, justes = j.reponses.filter(function (r) { return r.verdict === "juste"; }).length;
    var proches = j.reponses.filter(function (r) { return r.verdict === "proche"; }).length, parfait = justes === total;
    var exactes = j.reponses.filter(function (r, i) { return r.verdict === "juste" && j.questions[i].pas === 1; }).length;
    var points = j.reponses.reduce(function (n, r) { return n + r.points; }, 0) + (parfait ? R.points.parfait : 0);
    var fav = faveurIA(contenu, partie, t), mult = fav ? fav.palier.butin : 1, credits = Math.round(points * mult);
    partie.credits.solde += credits; partie.credits.gagnes += credits;
    s.parties++; if (parfait) s.parfaits++; s.maxExactes = Math.max(s.maxExactes || 0, exactes);
    var reussi = justes >= R.reussite, enCase = j.mode === "case" && s.case && partie.plateau.position === s.case;
    marquerJour(partie, t);
    noter(partie, t, { type: "chrono", bonnes: justes, total: total, xp: credits, source: j.mode });
    var out = { mode: j.mode, questions: j.questions, reponses: j.reponses, justes: justes, proches: proches, total: total, parfait: parfait, reussi: reussi,
      exactes: exactes, points: points, mult: mult, credits: credits, plateau: null, agacement: null,
      montees: j.reponses.filter(function (r) { return r.niveauApres > r.niveauAvant; }).length,
      contextes: [parfait ? "chrono_parfait" : reussi ? "chrono_bilan_bon" : "chrono_bilan_rate"] };
    if (enCase) {
      // La case est jouée, réussie ou non : on n'y revient pas. Victor (2026-11-01) : elle se libère, comme après un atome.
      var spC = partie.plateau.speciaux && partie.plateau.speciaux[s.case];
      if (spC && spC.type === "chrono") spC.libre = true;
      out.caseLibre = s.case;
      s.case = null;
      ouvrirLot(partie, t, themeCase(contenu, partie));
      var avant = verifierRecompenses(contenu, partie, t);
      if (reussi) ajouterButin(contenu, partie, avant, { type: "chrono" }, t, alea);
      var dep = jouerPlateau(contenu, partie, { type: "chrono" }, { reussi: reussi, parfait: parfait, jouer: true, alea: alea }, t);
      out.agacement = agacerIA(contenu, partie, total - justes, !reussi, t);
      lotExceptionnel(partie, dep);
      var apres = verifierRecompenses(contenu, partie, t);
      out.plateau = dep; out.avantPlateau = avant; out.apresPlateau = apres; out.recompenses = fusionRec(avant, apres);
    } else {
      // Partie offerte par Alyca : des crédits, rien d'autre, sauf un sans-faute qui la ravit.
      if (j.mode === "alyca") { s.offre = null; s.joueJour = cleJour(t); }
      if (j.mode === "ile") s.ileJour = cleJour(t);
      ouvrirLot(partie, t, null);
      if (parfait) out.agacement = agacerIA(contenu, partie, 0, false, t);
      out.recompenses = out.avantPlateau = verifierRecompenses(contenu, partie, t);
      out.apresPlateau = { succes: [], objets: [], accessoires: [], savants: [], evenements: [], livres: [], masque: null, gagnables: [], credits: [] };
    }
    // L'île : les monuments auxquels cette partie a ajouté une date (une chose datée juste pour la première fois).
    var nouvelles = {}; j.questions.forEach(function (q, i) { var f = s.fiches[q.cle]; if (j.reponses[i].verdict === "juste" && f && f.justes === 1) nouvelles[q.cle] = true; });
    out.monuments = (ilePresente(contenu) ? monumentsIle(contenu, partie) : []).map(function (m) {
      var n = m.dates.filter(function (x) { return nouvelles[x.cle]; }).length;
      return n ? { epoque: m.epoque, nomEpoque: m.nomEpoque, nom: m.nom, usage: m.usage, quartier: m.quartier, dates: m.dates.length, seuil: m.seuil, ajoutees: n, bati: m.bati, inaugure: m.bati && m.dates.length - n < m.seuil, habitants: m.habitants } : null;
    }).filter(Boolean);
    partie.maj = t;
    return out;
  }
  // Les événements vus, par niveau (pour les stats et les succès).
  function statsChrono(contenu, partie) {
    var s = etatChrono(partie), R = reglesChrono(contenu), parNiveau = {};
    Object.keys(s.fiches).forEach(function (k) { var n = s.fiches[k].niveau; parNiveau[n] = (parNiveau[n] || 0) + 1; });
    return { parties: s.parties, parfaits: s.parfaits, justes: s.justes, proches: s.proches, faux: s.faux, rapides: s.rapides, exactes: s.exactes,
      vus: Object.keys(s.fiches).length, parNiveau: parNiveau, reservoir: R ? reservoirChrono(contenu, partie).length : 0 };
  }
  function datesAuNiveau(partie, niveau) { var s = partie.siecles; return s ? Object.keys(s.fiches).filter(function (k) { return s.fiches[k].niveau >= niveau; }).length : 0; }
  // Enfermé au mur : plus rien ne se joue (quiz, rappels, duels, atomes) tant que la peine court.
  function jeuFerme(contenu, partie, t) { faveurIA(contenu, partie, t); return !!(partie.punition && partie.punition.restant > 0); }
  // Furieuse, l'IA pose chaque jour un piège sur une case libre juste devant le pion. Renvoie la case, ou null.
  function piegeIA(contenu, partie, t) {
    var fav = faveurIA(contenu, partie, t);
    if (!fav || fav.palier.id !== "furieuse" || !contenu.plateau || partie.colere === cleJour(t)) return null;
    var pl = partie.plateau, R = contenu.plateau.regles, en = ennemisPlateau(contenu, partie), libres = [];
    devantPion(contenu, partie, 1, 5).forEach(function (n) { if (!specialDe(contenu, partie, n) && !en[n]) libres.push(n); });
    partie.colere = cleJour(t);
    if (!libres.length) return null;
    var c = libres[hacher(cleJour(t) + "|" + pl.position) % libres.length], P = contenu.ia.faveur.piege;
    pl.speciaux[c] = { type: P.type, n: P.n, ia: true, raison: { fr: "Posé par l'IA, furieuse qu'on l'oublie. Un cadeau la calmerait peut-être." } };
    partie.maj = t;
    return c;
  }

  // --- Masques du jour (v11) --------------------------------------------------
  // Chaque jour, l'IA choisit de 1 à 3 masques parmi ceux qu'elle a gagnés, selon sa faveur :
  // comblée, des masques cléments ; furieuse, des masques cruels. Leurs règles s'additionnent.
  function masquesDuJour(contenu, partie, t) {
    if (!contenu.ia || !contenu.ia.masques_jour) return [];
    var jour = cleJour(t), parId = {};
    contenu.ia.masques.forEach(function (m) { parId[m.id] = m; });
    var mj = partie.masquesJour;
    if (mj && mj.jour === jour) return mj.ids.map(function (id) { return parId[id]; }).filter(Boolean);
    var fav = faveurIA(contenu, partie, t), permis = contenu.ia.masques_jour.selon_faveur[fav ? fav.palier.id : "contente"] || ["neutre"];
    var gagnes = contenu.ia.masques.filter(function (m) { return masqueDebloque(partie, m.id); });
    var aptes = gagnes.filter(function (m) { return permis.indexOf(m.caractere) >= 0; });
    if (!aptes.length) aptes = gagnes.filter(function (m) { return m.caractere === "neutre"; });
    if (!aptes.length) aptes = [contenu.ia.masques[0]];
    var tries = aptes.slice().sort(function (a, b) { return hacher(jour + "|" + a.id) - hacher(jour + "|" + b.id); });
    var n = 1 + hacher(jour + "|nombre") % Math.min(contenu.ia.masques_jour.max, tries.length);
    var choisis = tries.slice(0, n);
    partie.masquesJour = { jour: jour, ids: choisis.map(function (m) { return m.id; }), renfort: null };
    // Un masque « renfort » poste un ennemi absent sur une case libre devant le pion.
    if (choisis.some(function (m) { return m.regles && m.regles.ennemis === "renfort"; }) && contenu.plateau && contenu.placement) {
      var pl = partie.plateau, R = contenu.plateau.regles, en = ennemisPlateau(contenu, partie);
      var presents = Object.keys(en).map(function (k) { return en[k]; });
      var absents = contenu.ennemis.map(function (x) { return x.id; }).filter(function (x) { return presents.indexOf(x) < 0; });
      var cases = [];
      devantPion(contenu, partie, 2, 8).forEach(function (c) { if (!en[c] && !specialDe(contenu, partie, c)) cases.push(c); });
      if (absents.length && cases.length) {
        var k = cases[hacher(jour + "|case") % cases.length];
        en[k] = absents[hacher(jour + "|ennemi") % absents.length];
        partie.masquesJour.renfort = { case: k, ennemi: en[k] };
      }
    }
    return choisis;
  }
  // Les règles cumulées des masques du jour.
  function reglesDuJour(contenu, partie, t) {
    var out = { butin: 1, avance: 0, questions: 0, ennemis: null, pieges: null, echec: 1, atome: 0 };
    masquesDuJour(contenu, partie, t).forEach(function (m) {
      var g = m.regles || {};
      if (g.butin != null) out.butin *= g.butin;
      if (g.echec != null) out.echec *= g.echec;
      out.avance += g.avance || 0; out.questions += g.questions || 0; out.atome += g.atome || 0;
      if (g.ennemis === "absents" || (g.ennemis && !out.ennemis)) out.ennemis = g.ennemis;
      if (g.pieges) out.pieges = g.pieges;
    });
    return out;
  }
  function questionsQuiz(contenu, partie, t) {
    return Math.max(3, Math.min(8, contenu.regles.quiz.questions_par_quiz + reglesDuJour(contenu, partie, t).questions));
  }
  function seuilAtome(contenu, partie, t) {
    var A = contenu.atomes; if (!A) return 0;
    return Math.max(1, Math.min(A.regles.questions, A.regles.seuil + reglesDuJour(contenu, partie, t).atome));
  }

  // --- Aujourd'hui -----------------------------------------------------------

  // v28 : au mur sans grand-chose à relire, l'IA impose les fiches des compétences les plus fragiles :
  // les plus ratées ces 30 derniers jours, puis les maîtrisées au rappel le plus proche, puis les arbres ouverts.
  // Victor (2026-11-08) : le mur ne parle que de ce que le joueur a croisé : une compétence jouée, ratée, ou dont il
  // s'est arrêté sur la case. Jamais d'une case à venir.
  function croisees(contenu, partie) {
    var vu = {}, pl = partie.plateau || {}, cc = (contenu.plateau && contenu.plateau.competences_cases) || {};
    Object.keys(partie.competences || {}).forEach(function (id) { vu[id] = true; });
    (partie.oublis || []).forEach(function (e) { var q = contenu.questionParId && contenu.questionParId[e.q]; if (q) vu[q.competence] = true; });
    Object.keys(pl.arrets || pl.visites || {}).forEach(function (n) { (cc[n] || []).forEach(function (id) { vu[id] = true; }); });
    if (pl.position != null) (cc[pl.position] || []).forEach(function (id) { vu[id] = true; });
    return vu;
  }
  function fichesImposees(contenu, partie, t, n) {
    var rates = {}, vu = croisees(contenu, partie);
    (partie.oublis || []).forEach(function (e) { var q = contenu.questionParId && contenu.questionParId[e.q]; if (q && joursEntre(e.t, t) <= 30) rates[q.competence] = (rates[q.competence] || 0) + 1; });
    function poids(k) { var e = partie.competences[k.id]; return (rates[k.id] || 0) * 1e15 + (estMaitrisee(partie, k.id) ? 1e14 - Math.max(0, e.prochainRappel - t) / 1000 : 0); }
    return contenu.competences.filter(function (k) { return k.fiche && vu[k.id] && arbreOuvert(contenu, partie, k.stat); })
      .sort(function (a, b) { return poids(b) - poids(a) || (a.id < b.id ? -1 : 1); }).slice(0, n || 3);
  }

  function rappelsDus(contenu, partie, t) {
    return contenu.competences
      .filter(function (k) { return estMaitrisee(partie, k.id) && t >= partie.competences[k.id].prochainRappel; })
      .sort(function (a, b) { return partie.competences[a.id].prochainRappel - partie.competences[b.id].prochainRappel; })
      .slice(0, contenu.regles.aujourdhui.max_rappels);
  }

  function prochainsRappels(contenu, partie, t, n) {
    return contenu.competences
      .filter(function (k) { return estMaitrisee(partie, k.id) && t < partie.competences[k.id].prochainRappel; })
      .sort(function (a, b) { return partie.competences[a.id].prochainRappel - partie.competences[b.id].prochainRappel; })
      .slice(0, n || 3);
  }

  function disponibles(contenu, partie, t) {
    return contenu.competences.filter(function (k) { return statut(contenu, partie, k.id, t).etat === "disponible"; });
  }

  // Suggestion d'évolution : la stat la plus faible qui a une compétence jouable.
  function suggestion(contenu, partie, t) {
    var xp = xpParStat(contenu, partie);
    var stats = contenu.stats.slice().sort(function (a, b) { return xp[a.id] - xp[b.id]; });
    for (var i = 0; i < stats.length; i++) {
      var k = contenu.parStat[stats[i].id].filter(function (c) { return statut(contenu, partie, c.id, t).etat === "disponible"; })[0];
      if (k) return k;
    }
    return null;
  }

  // --- Succès ----------------------------------------------------------------

  function conditionRemplie(contenu, partie, cond, t) {
    var c = partie.compteurs;
    var maitrisees = contenu.competences.filter(function (k) { return estMaitrisee(partie, k.id); });
    switch (cond.type) {
      case "competences_maitrisees": return maitrisees.length >= cond.n;
      case "competence_maitrisee": return estMaitrisee(partie, cond.id);
      // Donjons : plusieurs conditions à la fois (par exemple deux arbres réussis).
      case "toutes": return (cond.conditions || []).every(function (x) { return conditionRemplie(contenu, partie, x, t); });
      case "quiz_parfaits_stat": return (c.parfaitsParStat[cond.stat] || 0) >= cond.n;
      case "quiz_eclair_rates": return c.quizEclairRates >= cond.n;
      case "quiz_zero": return c.quizZero >= cond.n;
      case "quiz_joues": return c.quizJoues >= cond.n;
      case "quiz_nuit": return c.quizNuit >= cond.n;
      case "quiz_aube": return c.quizAube >= cond.n;
      case "chrono_parfaits": return c.chronoParfaits >= cond.n;
      case "reponses_eclair_fausses": return c.reponsesEclairFausses >= cond.n;
      case "rappels_retard": return c.rappelsRetard >= cond.n;
      case "retours": return c.retours >= cond.n;
      case "mode_test": return c.modeTest >= cond.n;
      case "meme_quiz_rate": return Object.keys(partie.competences).some(function (id) { return (partie.competences[id].echecsSuite || 0) >= cond.n; });
      case "niveau_global": return niveauGlobal(contenu, partie) >= cond.n;
      case "succes": return !!partie.succes[cond.id];
      case "succes_obtenus": return Object.keys(partie.succes).length >= cond.n;
      case "objets": return Object.keys(partie.objets).length >= cond.n;
      case "quiz_parfaits": return c.quizParfaits >= cond.n;
      case "quiz_rates": return c.quizRates >= cond.n;
      case "branche_complete": return contenu.parStat[cond.stat].every(function (k) { return (cond.rang_max && k.rang > cond.rang_max) || estMaitrisee(partie, k.id); });
      // Un arbre en chantier (un seul savoir écrit) n'est ni « complet » ni exigé (Victor, 2026-11-12 : le feu donnait « Cultiver son jardin »).
      case "branches_completes": return contenu.stats.filter(function (s) { return !s.chantier && contenu.parStat[s.id].every(function (k) { return estMaitrisee(partie, k.id); }); }).length >= cond.n;
      case "rang_maitrise": return maitrisees.some(function (k) { return k.rang >= cond.rang; });
      case "toutes_branches": return contenu.stats.every(function (s) { return s.chantier || contenu.parStat[s.id].some(function (k) { return estMaitrisee(partie, k.id); }); });
      case "rappels_reussis": return c.rappelsReussis >= cond.n;
      case "serie_rappels": return c.serieRappels >= cond.n;
      case "duree_maitrise": return maitrisees.some(function (k) { return joursEntre(partie.competences[k.id].maitriseDepuis, t) >= cond.jours; });
      case "niveau_stat":
        var xp = xpParStat(contenu, partie);
        return contenu.stats.some(function (s) { return niveau(contenu, xp[s.id]).niveau >= cond.niveau; });
      case "competences_regagnees": return c.regagnees >= cond.n;
      case "competences_perdues": return c.perdues >= cond.n;
      case "jours_actifs": return partie.jours.length >= cond.n;
      // v15 : une case survolée ne débloque rien ; il faut s'y être arrêté.
      case "case_atteinte": return caseAtteinte(contenu, partie, cond.n);
      case "epoque_atteinte":
        if (partie.plateau.tours > 0) return true;
        var aa = contenu.plateau ? anneeAtteinte(contenu, partie.plateau) : null, ac = contenu.plateau ? anneeDe(contenu, cond.n) : null;
        return aa != null && ac != null ? aa >= ac : (partie.plateau.atteinte || 1) >= cond.n;
      case "case_visitee": return (partie.plateau.visites[cond.n] || 0) > 0;
      case "tours_plateau": return partie.plateau.tours >= cond.n;
      case "sorties_prison": return c.sortiesPrison >= cond.n;
      case "ennemi_vaincu": return !!(partie.bestiaire && partie.bestiaire[cond.id] && partie.bestiaire[cond.id].victoires);
      case "duels_gagnes": return (c.duelsGagnes || 0) >= cond.n;
      case "cadeaux_offerts": return (c.cadeaux || 0) >= cond.n;
      case "atomes_captures": return Object.keys(partie.atomes || {}).filter(function (z) { return partie.atomes[z].capture; }).length >= cond.n;
      case "atomes_enfuis": return (c.atomesEnfuis || 0) >= cond.n;
      case "hontes": return (c.hontes || 0) >= cond.n;
      case "hontes_effacees": return (c.hontesEffacees || 0) >= cond.n;
      case "famille_capturee":
        if (!contenu.atomes) return false;
        return contenu.atomes.elements.every(function (e) { return e.famille !== cond.famille || estCapture(partie, e.z); });
      // v34 : Chrono.
      case "chronos_joues": return !!partie.siecles && partie.siecles.parties >= cond.n;
      case "chronos_parfaits": return !!partie.siecles && partie.siecles.parfaits >= cond.n;
      case "dates_exactes_partie": return !!partie.siecles && (partie.siecles.maxExactes || 0) >= cond.n;
      case "dates_niveau": return datesAuNiveau(partie, cond.niveau) >= cond.n;
      case "dates_rapides": return !!partie.siecles && partie.siecles.rapides >= cond.n;
      case "dates_fausses": return !!partie.siecles && partie.siecles.faux >= cond.n;
      // Donjons (v-donjon) : pièces posées, bugs chassés (tous donjons confondus), donjon allumé.
      case "composants_poses": return compterDonjons(partie, function (e) { return Object.keys(e.poses || {}).length; }) >= cond.n;
      case "bugs_chasses": return compterDonjons(partie, function (e) { return e.bugsChasses || 0; }) >= cond.n;
      case "donjon_fini": return !!(partie.donjons && partie.donjons[cond.id] && partie.donjons[cond.id].allume);
      case "proces_gagne": return !!(partie.proces && partie.proces[cond.id] && partie.proces[cond.id].acquitte);
      case "proces_perdus": return Object.keys(partie.proces || {}).reduce(function (n, k) { return n + (partie.proces[k].perdus || 0); }, 0) >= cond.n;
      case "eurekas": return c.eurekas >= cond.n;
      case "reculs": return c.reculs >= cond.n;
      default: return false;
    }
  }

  // v6 : objets, livres, accessoires et masques forment le butin. Les reliques des tours (sans `lot`) et le
  // premier masque restent donnés d'office ; le reste devient « gagnable » quand sa condition est remplie,
  // puis tombe au hasard après une épreuve réussie (voir tirerButin).
  var FAMILLES_BUTIN = ["objets", "livres", "accessoires", "masques"];
  // v15 : au plus un savant, un livre ou un objet par épreuve. Le reste attend l'épreuve suivante.
  // `partie.lot` compte ce qui est tombé pendant l'épreuve datée `t` ; hors épreuve, chaque appel a son propre lot.
  var FAMILLES_LOT = { savants: 1, objets: 1, livres: 1 };
  // v19 : au plus RECOMPENSES_PAR_EPREUVE récompenses par épreuve (ou par visite), succès compris. Les autres attendent
  // les épreuves suivantes : leurs conditions restent remplies, elles tombent plus tard. Le thème de l'épreuve passe d'abord.
  // Quatre seulement pour un exploit : un tour complet du plateau ; trois pour un duel gagné.
  var RECOMPENSES_PAR_EPREUVE = 2, SUCCES_EXPLOIT = 4, SUCCES_DUEL = 3;
  function lotExceptionnel(partie, dep) {
    if (partie.lot && dep && dep.etapes && dep.etapes.some(function (e) { return e.type === "tour_fini"; })) partie.lot.cap = SUCCES_EXPLOIT;
  }
  // Un thème ne compte que si son arbre est joué (pack allumé) : l'ennemi ou l'atome d'un arbre éteint ne donne pas de ton.
  function themeActif(contenu, th) { return th && contenu.parStat[th] ? th : null; }
  function ouvrirLot(partie, t, theme) { partie.lot = { t: t, n: 0, r: 0, theme: theme || null }; }
  function lotDe(partie, t) { return partie.lot && partie.lot.t === t ? partie.lot : { t: t, n: 0, r: 0, theme: null }; }
  // Victor (2026-11-08) : succès, personnages, objets et livres sont toujours liés à la case. Ce qu'un contenu
  // désigne (une compétence, une case, une époque) doit être celui de la case du pion ou de l'épreuve qu'on vient de
  // jouer ; sinon il attend d'y être. Les succès de comportement (séries, ratés, duels…) ne visent rien : ils tombent
  // quand on les mérite.
  function ici(contenu, partie, lot) {
    var P = contenu.plateau, pl = partie.plateau, n = pl ? pl.position : null, k = P && n != null ? caseN(contenu, n) : null;
    var comps = {}; ((P && P.competences_cases && P.competences_cases[n]) || []).forEach(function (id) { comps[id] = true; });
    if (lot && lot.comp) comps[lot.comp] = true;
    return { n: n, epoque: k ? k.epoque : null, comps: comps, gagnes: {} };
  }
  // null : la condition ne vise aucun contenu ; true/false : elle en vise un, celui d'ici ou un autre.
  function condLiee(contenu, cond, la) {
    if (!cond) return null;
    switch (cond.type) {
      case "competence_maitrisee": return !!la.comps[cond.id];
      case "case_atteinte": case "case_visitee": return cond.n === la.n;
      case "epoque_atteinte": var ke = caseN(contenu, cond.n); return cond.n === la.n || !!(ke && ke.epoque === la.epoque);
      case "succes":
        if (la.gagnes[cond.id]) return true;
        var s2 = contenu.parSucces && contenu.parSucces[cond.id], prof = la.prof || 0;
        if (!s2 || prof > 4) return null;
        la.prof = prof + 1; var v2 = condLiee(contenu, s2.condition, la); la.prof = prof;
        return v2;
      case "toutes":
        var r = (cond.conditions || []).map(function (c) { return condLiee(contenu, c, la); }).filter(function (v) { return v !== null; });
        return r.length ? r.some(Boolean) : null;
      default: return null;
    }
  }
  function lieIci(contenu, x, la) {
    if (!contenu.plateau || la.n == null) return true;
    if (x.competence && la.comps[x.competence]) return true;
    var v = condLiee(contenu, x.condition, la);
    if (v === null) return !x.competence;
    return v;
  }
  function horsLot(lot, liste) { return lot.n ? liste.filter(function (b) { return !FAMILLES_LOT[b.famille]; }) : liste; }
  function compterLot(lot, famille) { if (FAMILLES_LOT[famille]) lot.n++; if (famille !== "evenements") lot.r = (lot.r || 0) + 1; }
  // v19 : tout ce qu'une épreuve montre à la fin (succès, savants, masques, objets, livres, accessoires, cadeaux) compte.
  function lotPlein(lot) { return (lot.r || 0) >= (lot.cap || RECOMPENSES_PAR_EPREUVE); }
  function listeFamille(contenu, f) {
    if (f === "objets") return contenu.objets;
    if (f === "livres") return contenu.livres || [];
    if (f === "accessoires") return contenu.avatar ? contenu.avatar.accessoires : [];
    if (f === "masques") return contenu.ia ? contenu.ia.masques : [];
    return [];
  }
  function estButin(x) { return typeof x.lot === "number"; }
  // Un même identifiant peut exister dans deux familles (les Principia : relique et livre).
  function cleButin(f, id) { return f + ":" + id; }
  function possede(partie, f, id) { var r = partie[f] || (partie[f] = {}); return r[id] != null; }

  // Débloque succès, savants, dates de la frise, reliques ; range le butin dont la condition est remplie.
  // Certains dépendent des autres (« 30 succès », « 10 objets ») : on boucle jusqu'à stabilité.
  // v20 : les récompenses d'une épreuve en deux temps, celles de l'épreuve puis celles du déplacement du pion
  // (tour bouclé, cases…). Le bilan montre les premières avant le plateau, les secondes après.
  function fusionRec(a, b) {
    var o = {};
    Object.keys(a).forEach(function (k) { o[k] = Array.isArray(a[k]) ? a[k].concat(b[k] || []) : a[k] || b[k] || null; });
    return o;
  }
  function verifierRecompenses(contenu, partie, t) {
    var out = { succes: [], objets: [], accessoires: [], savants: [], evenements: [], livres: [], masque: null, gagnables: [], credits: [] };
    partie.gagnables = partie.gagnables || {};
    partie.masques = partie.masques || {};
    var nCadeaux = 0;
    // v8 : les cadeaux des cases, déjà rangés, rejoignent le résultat pour être montrés au joueur.
    (partie.cadeauxCase || []).forEach(function (c) {
      var x = listeFamille(contenu, c.famille).filter(function (y) { return y.id === c.id; })[0];
      if (!x) return;
      if (c.famille === "masques") out.masque = x; else out[c.famille].push(x);
      nCadeaux++;
    });
    partie.cadeauxCase = [];
    var lot = lotDe(partie, t);
    lot.r = (lot.r || 0) + nCadeaux;
    var la = ici(contenu, partie, lot);
    var directes = [
      ["savants", contenu.avatar && contenu.avatar.savants ? contenu.avatar.savants : [], partie.savants || (partie.savants = {})],
      ["succes", contenu.succes, partie.succes],
      ["evenements", contenu.evenements, partie.evenements],
    ];
    var change = true;
    while (change) {
      change = false;
      directes.forEach(function (f) {
        var liste = f[1];
        if (f[0] === "succes") {
          var place = (lot.cap || RECOMPENSES_PAR_EPREUVE) - (lot.r || 0);
          liste = place <= 0 ? [] : liste.filter(function (x) { return !f[2][x.id] && lieIci(contenu, x, la) && conditionRemplie(contenu, partie, x.condition, t); });
          if (lot.theme) liste = liste.filter(function (x) { return themeDe(x) === lot.theme; }).concat(liste.filter(function (x) { return themeDe(x) !== lot.theme; }));
          liste = liste.slice(0, Math.max(0, place));
        }
        liste.forEach(function (x) {
          if (f[2][x.id] || (FAMILLES_LOT[f[0]] && lot.n) || (f[0] !== "evenements" && lotPlein(lot)) || !conditionRemplie(contenu, partie, x.condition, t)) return;
          if (f[0] === "evenements" && !dateAtteinte(contenu, partie, x)) return;
          if (f[0] === "savants" && !lieIci(contenu, x, la)) return;
          // Victor (2026-11-01) : une date d'un arbre éteint ne se débloque pas (la case qui la porte n'est pas sur la route).
          if (f[0] === "evenements" && x.stat && contenu.parStat && !contenu.parStat[x.stat]) return;
          f[2][x.id] = t; out[f[0]].push(x); change = true; compterLot(lot, f[0]);
          if (f[0] === "succes") la.gagnes[x.id] = true;
          if (f[0] === "succes") { var cr = crediterSucces(contenu, partie, x); if (cr) out.credits.push(cr); }
        });
      });
      FAMILLES_BUTIN.forEach(function (f) {
        listeFamille(contenu, f).forEach(function (x) {
          if (possede(partie, f, x.id) || partie.gagnables[cleButin(f, x.id)]) return;
          if (x.condition && !conditionRemplie(contenu, partie, x.condition, t)) return;
          if (estButin(x)) { partie.gagnables[cleButin(f, x.id)] = { famille: f, id: x.id, depuis: t }; out.gagnables.push(x); return; }
          // Hors butin : reliques des tours, premier masque de l'IA.
          if ((FAMILLES_LOT[f] && lot.n) || lotPlein(lot)) return;
          partie[f][x.id] = t; change = true; compterLot(lot, f);
          if (f === "masques") partie.masque = x.id; else out[f].push(x);
        });
      });
    }
    var m = masqueActuel(contenu, partie);
    if (m) partie.masque = m.id;
    if (out.succes.length || out.objets.length || out.savants.length || out.evenements.length || out.gagnables.length) partie.maj = t;
    return out;
  }

  // Chance qu'une épreuve réussie fasse tomber un butin : un rappel, ou un quiz selon son rang.
  function chanceButin(contenu, epreuve) {
    var b = contenu.plateau && contenu.plateau.regles.butin;
    if (!b) return 0;
    if (epreuve.type === "rappel") return b.rappel;
    if (epreuve.type === "duel") return 1;
    var k = contenu.parId[epreuve.comp];
    return Math.min(1, b.quiz_base + b.quiz_par_rang * (k ? k.rang : 1));
  }
  // Butin qui peut tomber maintenant : gagnable, et dont le lot est ouvert (lot N à partir du tour N).
  // v15 : pas d'anachronisme. Un livre ne tombe que s'il est paru avant la fin de l'époque de la case du pion.
  // Victor (2026-11-03) : un livre ne tombe que sur le quiz ou le rappel de sa compétence (tirerButin) ; pour lui,
  // `livresLies` lève le filtre d'époque, puisque l'épreuve est déjà la sienne.
  function butinOuvert(contenu, partie, livresLies) {
    var tour = (partie.plateau ? partie.plateau.tours : 0) + 1, out = [], fin = livresLies ? null : finEpoqueCase(contenu, partie);
    FAMILLES_BUTIN.forEach(function (f) {
      listeFamille(contenu, f).forEach(function (x) {
        if (f === "livres" && fin != null && Number(x.annee) > fin) return;
        if (partie.gagnables && partie.gagnables[cleButin(f, x.id)] && !possede(partie, f, x.id) && x.lot <= tour) out.push({ famille: f, chose: x });
      });
    });
    return out;
  }
  // La frise suit le pion : pendant le premier tour, une date (gagnée par une compétence) attend que le pion
  // ait atteint son époque. Au début du parcours, on ne débloque donc que de l'antique.
  function dateAtteinte(contenu, partie, ev) {
    var P = contenu.plateau, pl = partie.plateau;
    if (!P || !pl || pl.tours > 0 || ev.annee == null) return true;
    var a = anneeAtteinte(contenu, pl);
    var e = a != null && (P.epoques || []).filter(function (x) { return (x.debut == null || x.debut <= a) && (x.fin == null || a <= x.fin); })[0];
    return !e || e.fin == null || Number(ev.annee) <= e.fin;
  }
  function epoqueCase(contenu, partie) {
    var P = contenu.plateau, k = P && partie.plateau && caseN(contenu, partie.plateau.position);
    return k ? (P.epoques || []).filter(function (e) { return e.id === k.epoque; })[0] || null : null;
  }
  function finEpoqueCase(contenu, partie) { var e = epoqueCase(contenu, partie); return e ? e.fin : null; }
  // --- v18 : le thème. La case du pion donne le ton : butin, cadeaux, apartés, masques, farces et répliques ---
  // Le thème d'une chose : son champ `theme` (objets, savants, masques, ennemis, succès), sinon son arbre (livres).
  function themeDe(x) { return x ? x.theme || x.stat || null : null; }
  // Le thème de la case où se tient le pion.
  function themeCase(contenu, partie) {
    var k = contenu.plateau && partie.plateau && caseN(contenu, partie.plateau.position);
    // Une case dont l'arbre est éteint ne donne pas de ton.
    return k && k.stat && contenu.parStat[k.stat] ? k.stat : null;
  }
  // Le thème d'une épreuve : l'arbre de sa compétence, celui de l'ennemi d'un duel, sinon celui de la case.
  function themeEpreuve(contenu, partie, epreuve) {
    if (epreuve && epreuve.comp && contenu.parId[epreuve.comp]) return contenu.parId[epreuve.comp].stat;
    if (epreuve && epreuve.ennemi && contenu.ennemiParId && contenu.ennemiParId[epreuve.ennemi]) return themeActif(contenu, themeDe(contenu.ennemiParId[epreuve.ennemi]));
    return themeCase(contenu, partie);
  }
  // Trois fois sur quatre, quand c'est possible, on puise dans ce qui est du thème. Tiré par hachage, pour
  // ne pas déranger les tirages au sort ; `de` donne l'élément à comparer (par défaut la chose elle-même).
  var PART_THEME = 4;
  // Hachage brassé : les bits bas du hachage simple se ressemblent trop d'une graine voisine à l'autre.
  function tirage(texte, n) {
    var h = hacher(texte);
    h ^= h >>> 16; h = Math.imul(h, 0x45d9f3b) >>> 0; h ^= h >>> 16; h = Math.imul(h, 0x45d9f3b) >>> 0; h ^= h >>> 16;
    return (h >>> 0) % n;
  }
  function duTheme(liste, theme, graine, de) {
    if (!theme || !liste.length) return liste;
    var ici = liste.filter(function (x) { return themeDe(de ? de(x) : x) === theme; });
    return ici.length && tirage("theme|" + graine, PART_THEME) ? ici : liste;
  }

  // v8 : case cadeau. Un objet du cabinet tombe sans épreuve ; à défaut, n'importe quel autre butin ouvert.
  function tirerCadeau(contenu, partie, t) {
    var lot = lotDe(partie, t), ouvert = horsLot(lot, butinOuvert(contenu, partie)).filter(function (b) { return b.famille !== "livres"; }), objets = ouvert.filter(function (b) { return b.famille === "objets"; });
    var liste = objets.length ? objets : ouvert;
    // v18 : un objet du thème de la case, si le cabinet en a un en attente.
    var th = themeCase(contenu, partie), ici = th ? liste.filter(function (b) { return themeDe(b.chose) === th; }) : [];
    if (ici.length) liste = ici;
    if (!liste.length) return null;
    var b = liste[hacher(String(t) + "|" + partie.plateau.position + "|" + partie.journal.length) % liste.length];
    partie[b.famille][b.chose.id] = t; compterLot(lot, b.famille);
    delete partie.gagnables[cleButin(b.famille, b.chose.id)];
    if (b.famille === "masques") partie.masque = b.chose.id;
    return b;
  }
  // Le butin en attente rattaché à la compétence de l'épreuve (champ competence, ou condition sur elle).
  function butinLie(ouvert, epreuve) {
    var c = epreuve && epreuve.comp; if (!c) return [];
    return ouvert.filter(function (b) { var x = b.chose; return x.competence === c || (x.condition && x.condition.id === c); });
  }
  // Après une épreuve réussie : au plus un butin, tiré au hasard. `alea` (facultatif) pour les tests.
  function tirerButin(contenu, partie, epreuve, t, alea) {
    alea = alea || Math.random;
    var lot = lotDe(partie, t); if (lotPlein(lot)) return null;
    // Victor (2026-11-03) : le livre d'une compétence tombe sur son quiz ou son rappel réussi, à coup sûr, et jamais
    // sur une autre épreuve.
    var livre = (epreuve.type === "quiz" || epreuve.type === "rappel") ? butinLie(horsLot(lot, butinOuvert(contenu, partie, true)), epreuve).filter(function (b) { return b.famille === "livres"; })[0] : null;
    if (livre) {
      partie.livres[livre.chose.id] = t; compterLot(lot, "livres");
      delete partie.gagnables[cleButin("livres", livre.chose.id)];
      partie.maj = t;
      return livre;
    }
    var laB = ici(contenu, partie, lot); if (epreuve.comp) laB.comps[epreuve.comp] = true;
    var ouvert = horsLot(lot, butinOuvert(contenu, partie)).filter(function (b) { return b.famille !== "livres" && (b.famille !== "objets" || lieIci(contenu, b.chose, laB)); });
    var fav = epreuve.type === "duel" ? null : faveurIA(contenu, partie, t);
    var assure = partie.butinAssure && epreuve.type !== "duel" && ouvert.length;
    if (assure) partie.butinAssure = false;
    var mult = epreuve.type === "duel" ? 1 : reglesDuJour(contenu, partie, t).butin;
    if (!assure && (!ouvert.length || alea() >= chanceButin(contenu, epreuve) * (fav ? fav.palier.butin : 1) * mult)) return null;
    // v18 : trois fois sur quatre, le butin vient du thème de l'épreuve quand il y en a un en attente.
    // Victor (2026-11-01) : d'abord ce qui tient à l'épreuve elle-même (livre, objet… de sa compétence), sinon le thème.
    var lies = butinLie(ouvert, epreuve);
    var th = themeEpreuve(contenu, partie, epreuve), pool = lies.length ? lies : duTheme(ouvert, th, t + "|" + partie.journal.length, function (x) { return x.chose; });
    var b = pool[Math.floor(alea() * pool.length)];
    partie[b.famille][b.chose.id] = t; compterLot(lot, b.famille);
    delete partie.gagnables[cleButin(b.famille, b.chose.id)];
    if (b.famille === "masques") partie.masque = b.chose.id;
    partie.maj = t;
    return b;
  }
  // Intègre le butin tombé au résultat d'une épreuve, avec ce qu'il débloque à son tour (« 10 objets »…).
  function ajouterButin(contenu, partie, rec, epreuve, t, alea) {
    var b = tirerButin(contenu, partie, epreuve, t, alea);
    if (!b) return null;
    if (b.famille === "masques") rec.masque = b.chose; else rec[b.famille].push(b.chose);
    var suite = verifierRecompenses(contenu, partie, t);
    ["succes", "objets", "accessoires", "savants", "evenements", "livres"].forEach(function (f) { rec[f] = rec[f].concat(suite[f]); });
    return b;
  }

  // v6 : l'avatar incarne le dernier savant débloqué (par ses succès), sans choix du joueur.
  function savantActuel(contenu, partie) {
    if (!contenu.avatar || !contenu.avatar.savants) return null;
    var vus = partie.savants || {}, out = null, tMax = -1;
    contenu.avatar.savants.forEach(function (s) { if (vus[s.id] != null && vus[s.id] >= tMax) { tMax = vus[s.id]; out = s; } });
    return out;
  }

  function verifierSucces(contenu, partie, t) {
    return verifierRecompenses(contenu, partie, t).succes;
  }

  // --- Avatar et narrateur ---------------------------------------------------

  function rangAvatar(contenu, partie) {
    if (!contenu.avatar) return null;
    var ng = niveauGlobal(contenu, partie), rang = contenu.avatar.rangs[0];
    contenu.avatar.rangs.forEach(function (r) { if (ng >= r.niveau_min) rang = r; });
    return rang;
  }

  // --- Personnage : apparence choisie et pouvoirs (Victor, 2026-11-03) -------------------------
  // `partie.apparence` : { espece, teinte, regard, coiffure, cheveux, barbe, tenue, couleur } (ids de avatar.creation),
  // null tant que le joueur n'a pas créé son personnage (l'avatar d'avant : humain, cheveux courts, tenue du rang).
  function parId1(liste, id, defaut) {
    liste = liste || [];
    return liste.filter(function (x) { return x.id === id; })[0] || liste.filter(function (x) { return x.id === defaut; })[0] || liste[0] || null;
  }
  function apparence(contenu, partie) {
    var cr = contenu.avatar && contenu.avatar.creation; if (!cr || !partie.apparence) return null;
    var a = partie.apparence, esp = parId1(cr.especes, a.espece, "humain");
    var tenue = a.tenue && a.tenue !== "rang" ? parId1(cr.tenues, a.tenue) : null;
    var couleur = tenue ? ((parId1(cr.couleurs_tenue, a.couleur) || {}).hexa || tenue.couleur) : null;
    if (tenue && !a.couleur) couleur = tenue.couleur;
    return {
      espece: esp, teinte: parId1(esp.teintes, a.teinte), regard: esp.yeux ? parId1(cr.regards, a.regard, "normal") : null,
      coiffure: parId1(cr.coiffures, a.coiffure, esp.coiffure), cheveux: parId1(cr.couleurs_cheveux, a.cheveux, "chatain"),
      barbe: parId1(cr.barbes, a.barbe, "aucune"), tenue: tenue, couleurs: tenue ? couleursTenue(tenue, couleur) : null,
    };
  }
  function nuance(h, f) {
    var c = [1, 3, 5].map(function (i) { return parseInt(h.slice(i, i + 2), 16); });
    c = c.map(function (v) { return Math.max(0, Math.min(255, Math.round(f < 1 ? v * f : v + (255 - v) * (f - 1)))); });
    return "#" + c.map(function (v) { return (v < 16 ? "0" : "") + v.toString(16).toUpperCase(); }).join("");
  }
  // Une tenue « assortie » (bas de la même couleur que le haut par défaut) suit la couleur choisie jusqu'au pantalon.
  function couleursTenue(tenue, principal) {
    var bas = tenue.bas === tenue.couleur ? principal : tenue.bas, d = tenue.detail;
    return { "!": nuance(principal, 0.68), X: principal, "*": nuance(principal, 1.32), "~": nuance(bas, 0.7), Z: bas, "+": nuance(d, 0.7), Q: d };
  }
  // Victor (2026-11-03) : au départ, toge ou blouse d'écolier ; les autres tenues se gagnent avec leur succès.
  function tenueDebloquee(contenu, partie, tn) {
    if (!tn) return false;
    if (tn.depart || !tn.condition) return true;
    // Une tenue ou un pouvoir gardé par un succès que le jeu n'a pas (son pack est éteint) n'attend pas ce succès.
    if (tn.condition.type === "succes" && succesAbsent(contenu, tn.condition.id)) return true;
    return tn.condition.type === "succes" && !!(partie.succes || {})[tn.condition.id];
  }
  function succesAbsent(contenu, id) { return !!(contenu && contenu.parSucces && !contenu.parSucces[id]); }
  // Les tenues gagnées pas encore annoncées (seulement une fois le personnage créé) ; marquées vues.
  function annoncerTenues(contenu, partie, t) {
    var cr = contenu.avatar && contenu.avatar.creation; if (!cr || !partie.apparence) return [];
    partie.tenues = partie.tenues || {};
    return cr.tenues.filter(function (tn) {
      if (tn.depart || partie.tenues[tn.id] || !tenueDebloquee(contenu, partie, tn)) return false;
      partie.tenues[tn.id] = t;
      // Libre faute de succès : elle est simplement là, sans annonce.
      return !(tn.condition && tn.condition.type === "succes" && succesAbsent(contenu, tn.condition.id));
    });
  }
  // Selon son humeur du moment, Alyca confisque une tenue gagnée ou un accessoire (boudeuse, furieuse), ou dore ta tenue
  // (comblée). Décidé une fois par jour et par palier : qu'elle change d'humeur, et elle revoit sa décision.
  // `partie.humeurPerso` = { jour, palier, type: null | "confisque_tenue" | "confisque_accessoire" | "retouche", cible, ligne }.
  function humeurPerso(contenu, partie, t, alea) {
    var cr = contenu.avatar && contenu.avatar.creation; if (!cr || !contenu.ia || !contenu.ia.faveur) return null;
    var pal = faveurIA(contenu, partie, t).palier.id, jour = cleJour(t), h = partie.humeurPerso;
    if (h && h.jour === jour && h.palier === pal) return h.type ? h : null;
    alea = alea || Math.random;
    var out = { jour: jour, palier: pal, type: null, cible: null, ligne: 0 };
    var ap = partie.apparence, av = partie.avatar || {};
    var tn = ap && ap.tenue && ap.tenue !== "rang" ? parId1(cr.tenues, ap.tenue) : null;
    var tenue = tn && !tn.depart ? { type: "tenue", id: tn.id } : null;
    var accs = ["tete", "visage", "main"].filter(function (e) { return av[e]; }).map(function (e) { return { type: "accessoire", emplacement: e, id: av[e] }; });
    var acc = accs.length ? accs[Math.floor(alea() * accs.length)] : null;
    if (pal === "furieuse" || (pal === "boudeuse" && alea() < 0.5)) {
      var c = pal === "furieuse" ? tenue || acc : acc || tenue;
      if (c) { out.type = c.type === "tenue" ? "confisque_tenue" : "confisque_accessoire"; out.cible = c; }
    } else if (pal === "comblee" && ap && alea() < 0.5) { out.type = "retouche"; out.cible = tn ? { type: "tenue", id: tn.id } : null; }
    out.ligne = Math.floor(alea() * 3);
    partie.humeurPerso = out;
    return out.type ? out : null;
  }
  function humeurPersoActive(partie, t) {
    var h = partie.humeurPerso;
    return h && h.type && h.jour === cleJour(t) ? h : null;
  }
  function choisirApparence(contenu, partie, choix) {
    var cr = contenu.avatar && contenu.avatar.creation; if (!cr) return false;
    var a = {}, cles = { espece: cr.especes, regard: cr.regards, coiffure: cr.coiffures, cheveux: cr.couleurs_cheveux, barbe: cr.barbes, couleur: cr.couleurs_tenue };
    Object.keys(cles).forEach(function (k) { if (choix[k] && parId1(cles[k], choix[k]).id === choix[k]) a[k] = choix[k]; });
    var esp = parId1(cr.especes, a.espece, "humain"); a.espece = esp.id;
    a.teinte = parId1(esp.teintes, choix.teinte).id;
    var tc = choix.tenue === "rang" ? null : parId1(cr.tenues, choix.tenue);
    a.tenue = choix.tenue === "rang" ? "rang" : tc && tc.id === choix.tenue && tenueDebloquee(contenu, partie, tc) ? tc.id : "ecolier";
    partie.apparence = a;
    return true;
  }

  // Pouvoirs : débloqués quand leur condition est remplie (succès, niveau global, niveau d'arbre), ils se rechargent
  // chaque jour ou chaque semaine (lundi). `partie.pouvoirs[id]` = { vu, periode, utilises }.
  function niveauArbres(contenu, partie, ids) {
    var xp = xpParStat(contenu, partie), best = -1;
    (ids || []).forEach(function (id) { if (xp[id] != null) best = Math.max(best, niveau(contenu, xp[id]).niveau); });
    return best;
  }
  function conditionPouvoir(contenu, partie, c) {
    if (!c) return true;
    if (c.succes && !succesAbsent(contenu, c.succes) && !(partie.succes || {})[c.succes]) return false;
    if (c.niveau_global != null && niveauGlobal(contenu, partie) < c.niveau_global) return false;
    if (c.niveau_stat) {
      var nv = niveauArbres(contenu, partie, c.niveau_stat.stats);
      if (nv < 0 ? niveauGlobal(contenu, partie) < (c.niveau_stat.sinon_global || 0) : nv < c.niveau_stat.min) return false;
    }
    return true;
  }
  function periodePouvoir(p, t) {
    if (p.charges.periode !== "semaine") return cleJour(t);
    var d = new Date(debutJour(t)); d.setDate(d.getDate() - (d.getDay() + 6) % 7);
    return "S" + cleJour(d.getTime());
  }
  function chargesMax(contenu, partie, p) {
    var ch = p.charges, pa = ch.palier;
    if (pa && ((pa.niveau_global != null && niveauGlobal(contenu, partie) >= pa.niveau_global) ||
        (pa.niveau_stat != null && niveauArbres(contenu, partie, p.condition.niveau_stat && p.condition.niveau_stat.stats) >= pa.niveau_stat))) return pa.n;
    return ch.n;
  }
  function etatPouvoir(contenu, partie, p, t) {
    var debloque = conditionPouvoir(contenu, partie, p.condition), max = debloque ? chargesMax(contenu, partie, p) : 0;
    var e = (partie.pouvoirs || {})[p.id], utilises = e && e.periode === periodePouvoir(p, t) ? e.utilises || 0 : 0;
    return { pouvoir: p, debloque: debloque, max: max, reste: Math.max(0, max - utilises), annonce: !!(e && e.vu) };
  }
  function pouvoirs(contenu, partie, t) {
    return ((contenu.avatar && contenu.avatar.pouvoirs) || []).map(function (p) { return etatPouvoir(contenu, partie, p, t); });
  }
  function pouvoir(contenu, partie, id, t) {
    var p = ((contenu.avatar && contenu.avatar.pouvoirs) || []).filter(function (x) { return x.id === id; })[0];
    return p ? etatPouvoir(contenu, partie, p, t) : null;
  }
  function utiliserPouvoir(contenu, partie, id, t) {
    var e = pouvoir(contenu, partie, id, t); if (!e || !e.reste) return false;
    partie.pouvoirs = partie.pouvoirs || {};
    var x = partie.pouvoirs[id] || (partie.pouvoirs[id] = { vu: t });
    var per = periodePouvoir(e.pouvoir, t);
    if (x.periode !== per) { x.periode = per; x.utilises = 0; }
    x.utilises++;
    x.total = (x.total || 0) + 1;
    return true;
  }
  // Les pouvoirs débloqués que le joueur n'a pas encore vus annoncés ; marqués vus.
  function annoncerPouvoirs(contenu, partie, t) {
    partie.pouvoirs = partie.pouvoirs || {};
    return pouvoirs(contenu, partie, t).filter(function (e) {
      if (!e.debloque || e.annonce) return false;
      partie.pouvoirs[e.pouvoir.id] = Object.assign(partie.pouvoirs[e.pouvoir.id] || {}, { vu: t });
      return true;
    }).map(function (e) { return e.pouvoir; });
  }

  // Dernier masque gagné par l'IA (ou débloqué par les tours du plateau).
  function masqueActuel(contenu, partie) {
    if (!contenu.ia) return null;
    var vus = partie.masques || {}, parId = {};
    contenu.ia.masques.forEach(function (m) { parId[m.id] = m; });
    if (partie.masque && vus[partie.masque] && parId[partie.masque]) return parId[partie.masque];
    var out = null, tMax = -1;
    contenu.ia.masques.forEach(function (m) { if (vus[m.id] != null && vus[m.id] >= tMax) { tMax = vus[m.id]; out = m; } });
    return out || contenu.ia.masques[0];
  }

  function masqueDebloque(partie, id) { return !!(partie.masques && partie.masques[id] != null); }

  // Hachage stable d'une chaîne : même graine, même choix, d'un affichage à l'autre.
  function hacher(texte) {
    var h = 2166136261;
    for (var i = 0; i < texte.length; i++) { h ^= texte.charCodeAt(i); h = Math.imul(h, 16777619) >>> 0; }
    return h;
  }

  // v5 : l'IA choisit elle-même son masque, parmi ceux qu'elle a gagnés et qui vont au ton de la réplique.
  // Le dernier masque gagné passe en premier tant qu'il va au ton : elle l'étrenne.
  // v18 : `theme` (facultatif) : parmi les masques qui conviennent, elle prend de préférence un masque du thème.
  function masquePourTon(contenu, partie, ton, graine, theme) {
    if (!contenu.ia) return null;
    var gagnes = contenu.ia.masques.filter(function (m) { return masqueDebloque(partie, m.id); });
    if (theme && gagnes.length) {
      var choix = masquePourTon(contenu, partie, ton, graine, null), gt = graine + "|" + theme;
      if (themeDe(choix) === theme) return choix;
      var mj = partie.masquesJour, jour = mj && mj.ids && mj.ids.length && mj.jour === cleJour(partie.maj || Date.now());
      var cands = (jour ? gagnes.filter(function (m) { return mj.ids.indexOf(m.id) >= 0; }) : gagnes).filter(function (m) { return themeDe(m) === theme; });
      var bons = cands.filter(function (m) { return !m.tons || m.tons.indexOf(ton) >= 0; });
      if (bons.length && tirage("masque|" + gt, PART_THEME)) return bons[tirage(ton + "|" + gt, bons.length)];
      return choix;
    }
    if (!gagnes.length) return contenu.ia.masques[0];
    // v11 : elle ne parle qu'avec les masques qu'elle a choisis pour la journée.
    var mj = partie.masquesJour;
    if (mj && mj.ids && mj.ids.length && mj.jour === cleJour(partie.maj || Date.now())) {
      var duJour = gagnes.filter(function (m) { return mj.ids.indexOf(m.id) >= 0; });
      if (duJour.length) { var bons = duJour.filter(function (m) { return !m.tons || m.tons.indexOf(ton) >= 0; }); return (bons.length ? bons : duJour)[hacher(ton + "|" + (graine || "")) % (bons.length ? bons : duJour).length]; }
    }
    var neuf = masqueActuel(contenu, partie), vus = partie.masques || {};
    if (neuf && (neuf.tons || []).indexOf(ton) >= 0 && vus[neuf.id] === Math.max.apply(null, gagnes.map(function (m) { return vus[m.id]; })) &&
        hacher(String(graine || "")) % 2 === 0) return neuf;
    var aptes = gagnes.filter(function (m) { return !m.tons || m.tons.indexOf(ton) >= 0; });
    var liste = aptes.length ? aptes : gagnes;
    return liste[hacher(ton + "|" + (graine || "")) % liste.length];
  }

  // v5 : aparté où l'IA se sert d'un objet ou d'un livre débloqué. Une réplique sur deux environ en a un.
  // Renvoie {texte, objet} ou {texte, livre}, ou null.
  // v18 : `theme` (facultatif) : elle sort de préférence un objet ou un livre du thème.
  function aparte(contenu, partie, ton, graine, theme) {
    var lignes = contenu.apartes || [];
    if (!lignes.length) return null;
    var h = hacher("aparte|" + (graine || ""));
    if (h % 2) return null;
    var objets = contenu.objets.filter(function (o) { return partie.objets[o.id]; });
    var livres = (contenu.livres || []).filter(function (l) { return partie.livres && partie.livres[l.id]; });
    if (theme) {
      var oT = objets.filter(function (o) { return themeDe(o) === theme; }), lT = livres.filter(function (l) { return themeDe(l) === theme; });
      if ((oT.length || lT.length) && tirage("aparte-theme|" + graine, PART_THEME)) { objets = oT; livres = lT; }
    }
    if (!objets.length && !livres.length) return null;
    var sorte = !livres.length ? "objet" : !objets.length ? "livre" : (h >>> 3) % 3 === 0 ? "livre" : "objet";
    var choix = lignes.filter(function (l) { return l.sorte === sorte && l.ton === ton; });
    if (!choix.length) choix = lignes.filter(function (l) { return l.sorte === sorte && l.ton === "neutre"; });
    if (!choix.length) return null;
    var ligne = choix[(h >>> 5) % choix.length];
    var chose = sorte === "objet" ? objets[(h >>> 9) % objets.length] : livres[(h >>> 9) % livres.length];
    var nom = sorte === "objet" ? TX(chose.nom) : TX(chose.titre);
    if (sorte === "objet") nom = nom.charAt(0).toLowerCase() + nom.slice(1);
    var texte = TX(ligne.texte).replace(/\{(objet|livre)\}/g, nom);
    texte = texte.charAt(0).toUpperCase() + texte.slice(1);
    var out = { id: ligne.id, texte: { fr: texte } };
    out[sorte] = chose;
    return out;
  }

  // v7 : surnom donné par l'IA. Il suit son humeur (le dernier résultat) ou, juste après un succès, ce succès.
  function humeur(partie) {
    var j = partie.journal[partie.journal.length - 1];
    if (!j) return "neutre";
    if (j.type === "rappel") return j.xp < 0 ? "decue" : "impressionnee";
    if (j.xp <= 0) return "moqueuse";
    return j.bonnes === j.total ? "impressionnee" : "neutre";
  }
  function surnom(contenu, partie, t) {
    var S = contenu.surnoms; if (!S) return null;
    var dernier = null, tMax = -1;
    Object.keys(partie.succes).forEach(function (id) { if (partie.succes[id] > tMax) { tMax = partie.succes[id]; dernier = id; } });
    var fin = partie.journal[partie.journal.length - 1];
    var jT = fin ? fin.t : -1;
    var h = hacher(cleJour(t) + "|" + partie.journal.length);
    if (dernier && tMax >= jT && joursEntre(tMax, t) <= 1 && contenu.parSucces && contenu.parSucces[dernier]) {
      var sc = contenu.parSucces[dernier], m = S.succes[h % S.succes.length];
      return { texte: TX(m).replace("{succes}", TX(sc.nom)), ton: "impressionnee", succes: sc };
    }
    var ton = humeur(partie), l = S[ton] || S.neutre;
    return { texte: TX(l[h % l.length]), ton: ton };
  }

  // --- Bouton « Jouer » : l'IA choisit l'épreuve ------------------------------
  // Un rappel dû passe d'abord (le plus en retard). Sinon, parmi les quiz ouverts, l'IA tire une raison :
  // la stat la plus faible ou le hasard. Le choix reste le même tant qu'on n'a pas joué.
  var RETARD_PRIORITAIRE = 2 * JOUR;
  function rappelForceTous(contenu) { return (contenu.regles.rappels && contenu.regles.rappels.force_tous) || 3; }
  // La série de révisions en cours : ses rappels restants encore dus et maîtrisés (les autres sont sautés).
  function serieEnCours(contenu, partie, t) {
    var se = partie.serie; if (!se) return null;
    se.ids = se.ids.filter(function (id) { return contenu.parId[id] && estMaitrisee(partie, id); });
    if (!se.ids.length) { partie.serie = null; return null; }
    return se;
  }
  // Proposée après un rappel imposé : enchaîner tous les rappels dus ; tous réussis, prime en crédits.
  function primeSerie(contenu, partie, n, t) {
    var fav = faveurIA(contenu, partie, t), mult = fav ? fav.palier.butin : 1;
    // Victor (2026-11-02) : une série bouclée doit rapporter « pas mal de crédits » : un tarif par rappel et une prime fixe.
    var R = contenu.regles.rappels || {};
    return Math.round((n * (R.serie_credits_par_rappel || 30) + (R.serie_credits_bonus || 0)) * mult);
  }
  function serieProposable(contenu, partie, t) {
    if (partie.serie) return null;
    var dus = rappelsDus(contenu, partie, t);
    return dus.length >= 2 ? { n: dus.length, prime: primeSerie(contenu, partie, dus.length, t) } : null;
  }
  function lancerSerie(contenu, partie, t) {
    var p = serieProposable(contenu, partie, t); if (!p) return null;
    partie.serie = { ids: rappelsDus(contenu, partie, t).map(function (c) { return c.id; }), total: p.n, prime: p.prime, debut: t };
    partie.serieRompue = null;
    return partie.serie;
  }
  function abandonnerSerie(partie) { partie.serie = null; partie.serieRompue = null; }
  // Série rompue par un rappel raté (le jour même) : reprise proposée dès qu'il reste un rappel dû, prime recalculée sur ce reste.
  function serieReprenable(contenu, partie, t) {
    var ro = partie.serieRompue; if (partie.serie || !ro || cleJour(ro.t) !== cleJour(t)) return null;
    var dus = rappelsDus(contenu, partie, t);
    return dus.length ? { n: dus.length, prime: primeSerie(contenu, partie, dus.length, t) } : null;
  }
  function reprendreSerie(contenu, partie, t) {
    var p = serieReprenable(contenu, partie, t); if (!p) return null;
    partie.serie = { ids: rappelsDus(contenu, partie, t).map(function (c) { return c.id; }), total: p.n, prime: p.prime, debut: t, reprise: true };
    partie.serieRompue = null;
    return partie.serie;
  }
  // Victor (2026-10-31) : « une case = un quiz ». La case du pion donne toujours l'épreuve de sa compétence :
  // un quiz si elle n'est pas acquise (même verrouillée, hors ordre), un rappel si elle l'est, même pas encore dû.
  function choixIA(contenu, partie, t) {
    var rv = revisionEnCours(partie);
    if (rv && contenu.parId[rv.comp]) return { comp: contenu.parId[rv.comp], type: "rappel", raison: "revision" };
    if (modeIle(partie) && agesPresents(contenu)) return choixIle(contenu, partie, t);
    var dus = rappelsDus(contenu, partie, t);
    var dispo = disponibles(contenu, partie, t);
    var graine = hacher(cleJour(t) + "|" + partie.journal.length + "|" + (partie.cree || 0));
    // v15 : la case où se tient le pion dicte l'arbre. Les rappels dus passent toujours d'abord (ceux de cet arbre
    // en tête, l'oubli n'attend pas), puis un quiz de cet arbre ; sinon l'ancien choix, annoncé comme hors case.
    // Une partie neuve (pion posé sur 1) ou une case retirée du plateau : la route place d'abord le pion sur une vraie case.
    if (contenu.plateau && partie.plateau && contenu.plateau.cases.length && !caseN(contenu, partie.plateau.position)) route(contenu, partie);
    var k = contenu.plateau && partie.plateau && caseN(contenu, partie.plateau.position);
    var ach = arbreAchete(partie);
    if (ach && !contenu.parStat[ach.stat]) ach = null;
    var st = ach ? ach.stat : k && contenu.parStat[k.stat] ? k.stat : null;
    // v31 (Victor) : la case évoque des compétences précises (Mendel → Génétique) : elles passent avant le reste de l'arbre.
    var CC = contenu.plateau && contenu.plateau.competences_cases, evoque = (k && CC && CC[String(k.n)]) || [];
    if (ach && k && k.stat !== ach.stat) evoque = [];
    function evoquee(c) { return evoque.indexOf(c.id) >= 0; }
    // Un rappel très en retard (RETARD_PRIORITAIRE) passe avant tout ; les autres attendent leur arbre.
    // Victor (2026-10-31) : une série de révisions acceptée passe d'abord, puis, une épreuve sur `force_tous`,
    // Alyca impose un rappel dû (le pion reste sur sa case). La case garde son quiz pour après.
    var se = serieEnCours(contenu, partie, t);
    if (se) return { comp: contenu.parId[se.ids[0]], type: "rappel", raison: "serie", stat: null, kase: k || null, serie: { n: se.total - se.ids.length + 1, total: se.total } };
    var propreDu = dus.filter(evoquee)[0];
    if (!propreDu && dus.length && (partie.depuisRappel || 0) >= rappelForceTous(contenu)) return { comp: dus[0], type: "rappel", raison: "rappel_force", stat: null, kase: k || null };
    if (!ach || (k && k.stat === ach.stat)) {
      var propre = evoque.map(function (id) { return contenu.parId[id]; }).filter(Boolean)[0];
      if (propre) {
        var ep = partie.competences[propre.id];
        if (ep && ep.maitrise) return { comp: propre, type: "rappel", raison: "rappel", stat: propre.stat, kase: k, achat: !!ach, evoque: true };
        var libre = dispo.some(function (c) { return c.id === propre.id; });
        return { comp: propre, type: "quiz", raison: "case", stat: propre.stat, kase: k, achat: !!ach, evoque: true, horsOrdre: !libre || undefined };
      }
    }
    var urgents = dus.filter(function (c) { return t - partie.competences[c.id].prochainRappel >= RETARD_PRIORITAIRE && c.stat !== st; });
    if (urgents.length) return { comp: urgents[0], type: "rappel", raison: "rappel", stat: null, kase: k || null, achat: false };
    var dusEvoques = dus.filter(evoquee);
    if (dusEvoques.length) return { comp: dusEvoques[0], type: "rappel", raison: "rappel", stat: st, kase: k || null, achat: !!ach, evoque: true };
    var dispoEvoques = dispo.filter(evoquee);
    if (dispoEvoques.length) return { comp: dispoEvoques[graine % dispoEvoques.length], type: "quiz", raison: "case", stat: st, kase: k, achat: !!ach, evoque: true };
    // Victor (2026-10-31) : la case de l'ambre donne le quiz de l'ambre, même verrouillé (prérequis manquant ou arbre
    // fermé). Réussi, il est acquis ; il ne débloque la suite qu'une fois ses prérequis maîtrisés (hors ordre).
    var horsOrdre = evoque.map(function (id) { return contenu.parId[id]; }).filter(function (c) {
      if (!c || (ach && c.stat !== ach.stat)) return false;
      var e = partie.competences[c.id]; return !(e && e.maitrise);
    });
    if (horsOrdre.length) { var ho = horsOrdre[graine % horsOrdre.length]; return { comp: ho, type: "quiz", raison: "case", stat: ho.stat, kase: k, achat: !!ach, evoque: true, horsOrdre: true }; }
    var porte = st && porteArbre(contenu, partie, st);
    if (porte) return { comp: porte, type: "quiz", raison: "ouvre_arbre", stat: st, kase: k };
    var dusIci = dus.filter(function (c) { return c.stat === st; });
    if (dusIci.length) return { comp: dusIci[0], type: "rappel", raison: "rappel", stat: st, kase: k || null, achat: !!ach };
    if (st) {
      var ici = dispo.filter(function (c) { return c.stat === st; });
      if (ici.length) return { comp: ici[graine % ici.length], type: "quiz", raison: "case", stat: st, kase: k, achat: !!ach };
    }
    if (dus.length) return { comp: dus[0], type: "rappel", raison: "rappel", stat: null, kase: k || null, achat: false };
    if (!dispo.length) return null;
    if (st) return { comp: dispo[graine % dispo.length], type: "quiz", raison: "hors_case", stat: st, kase: k };
    var raisons = [];
    var sug = suggestion(contenu, partie, t);
    if (sug) raisons.push({ raison: "faible", liste: [sug] });
    raisons.push({ raison: "hasard", liste: dispo });
    var r = raisons[graine % raisons.length];
    return { comp: r.liste[(graine >>> 4) % r.liste.length], type: "quiz", raison: r.raison };
  }

  // Avancer d'une seule case : le joueur choisit l'arbre, l'IA y prend un rappel dû, sinon un quiz disponible.
  function choixArbre(contenu, partie, t, stat) {
    if (revisionEnCours(partie) || !arbreOuvert(contenu, partie, stat)) return null;
    var dus = rappelsDus(contenu, partie, t).filter(function (c) { return c.stat === stat; });
    if (dus.length) return { comp: dus[0], type: "rappel", raison: "choix_arbre", stat: stat };
    var ici = disponibles(contenu, partie, t).filter(function (c) { return c.stat === stat; });
    if (!ici.length) return null;
    var graine = hacher(cleJour(t) + "|" + partie.journal.length + "|" + stat);
    return { comp: ici[graine % ici.length], type: "quiz", raison: "choix_arbre", stat: stat };
  }

  // --- Farces de l'IA --------------------------------------------------------
  var DUREE_FARCE = JOUR;
  var CHANCE_FARCE = 1 / 3;
  // Après une épreuve ratée, une fois sur trois : l'IA déguise l'avatar pour 24 h.
  // v25 : elle ne remplace plus le personnage par un savant ; elle impose un accessoire ou repeint ses vêtements
  // (`avatar.tenues_farce`). `theme` (facultatif) : une tenue du thème de l'épreuve ratée a la priorité, une fois sur deux.
  function tenterFarce(contenu, partie, t, alea, theme) {
    // Les farces sont un tour d'Alyca : sans dramaturgie, personne ne touche au personnage.
    if (!contenu.avatar || !dramaturgie(contenu)) return null;
    alea = alea || Math.random;
    if (alea() >= CHANCE_FARCE) return null;
    var pool = [];
    (contenu.avatar.accessoires || []).forEach(function (a) { pool.push({ type: "accessoire", id: a.id, emplacement: a.emplacement }); });
    (contenu.avatar.tenues_farce || []).forEach(function (v) { pool.push({ type: "tenue", id: v.id, theme: v.theme }); });
    var av = partie.avatar || {}, actuelle = farceActive(partie, t);
    pool = pool.filter(function (f) {
      if (actuelle && actuelle.id === f.id) return false;
      return f.type === "tenue" || av[f.emplacement] !== f.id;
    });
    if (!pool.length) return null;
    if (theme) {
      var ici = pool.filter(function (f) { return f.type === "tenue" && f.theme === theme; });
      if (ici.length && alea() < 0.5) pool = ici;
    }
    var f = pool[Math.floor(alea() * pool.length)];
    partie.farce = { type: f.type, id: f.id, emplacement: f.emplacement || null, depuis: t, jusqua: t + DUREE_FARCE };
    return partie.farce;
  }
  function farceActive(partie, t) {
    var f = partie.farce;
    return f && t < f.jusqua ? f : null;
  }
  function rendreVisage(partie) { partie.farce = null; }
  // v25 : le nom de l'IA, une fois qu'elle l'a donné ; null avant.
  // v35 (Victor) : le nom ne sert qu'une fois la révélation vue, sinon on le découvre en douce, sans la scène.
  function nomIA(contenu, partie) { return partie.alyca && partie.alyca.vu && contenu.ia && contenu.ia.alyca ? contenu.ia.alyca.nom : null; }

  function expression(contenu, contexte) {
    // Packs : « theme_reussi@cosmos » prend l'expression de « theme_reussi ».
    var ex = contenu.ia && contenu.ia.expressions;
    return (ex && (ex[contexte] || ex[String(contexte).split("@")[0]])) || "neutre";
  }

  // Remplace {stat}, {n}… dans le texte d'une réplique, sans toucher au contenu.
  function habiller(contenu, ligne, vars) {
    var texte = {}, remplir = function (t) { return t.replace(/\{(\w+)\}/g, function (m, k) { return vars && vars[k] != null ? vars[k] : m; }); };
    Object.keys(ligne.texte).forEach(function (l) { texte[l] = remplir(ligne.texte[l]); });
    // Dans une autre langue, la traduction est prise avant de remplir les variables.
    if (texte[LANGUE] == null) texte[LANGUE] = remplir(TX(ligne.texte));
    return { id: ligne.id, contexte: ligne.contexte, texte: texte, expression: expression(contenu, ligne.contexte) };
  }

  // v18 : répliques propres à un arbre. Une réussite, un échec ou une annonce d'épreuve sur un thème a ses lignes
  // « theme_reussi@cosmos »… ; l'IA les prend trois fois sur cinq, le reste du temps elle garde ses lignes générales.
  var GROUPE_THEME = {
    quiz_reussi: "reussi", quiz_parfait: "reussi", quiz_parfait_facile: "reussi", rappel_reussi: "reussi", rappel_retard: "reussi",
    revision_reussie: "reussi", duel_gagne: "reussi",
    quiz_rate: "rate", quiz_rate_facile: "rate", quiz_zero: "rate", rappel_perdu: "rate", revision_ratee: "rate", duel_perdu: "rate",
    jouer_case: "jouer", jouer_hasard: "jouer", jouer_faible: "jouer", jouer_rappel: "jouer", jouer_bonus: "jouer", jouer_ouvre_arbre: "jouer",
    jouer_choix_arbre: "jouer", jouer_revision: "jouer",
  };
  // v27 : version furieuse de chaque contexte (sinon son groupe de GROUPE_THEME, sinon « defaut »). null : on garde la ligne ordinaire.
  var FURIEUSE = {
    jouer_case: "jouer", jouer_hasard: "jouer", jouer_faible: "jouer", jouer_rappel: "jouer", jouer_bonus: "jouer", jouer_ouvre_arbre: "jouer",
    jouer_choix_arbre: "jouer", jouer_revision: "jouer", jouer_hors_case: "jouer",
    honte_effacee: "reussi", honte_ratee: "rate", eureka: "reussi", prison_liberation: "reussi", quarantaine: "rate", oubli: "rate", eclair: "rate",
    ennemi: "ennemi", duel_gagne: "duel_gagne", duel_perdu: "duel_perdu",
    atome_apparait: "atome_apparait", atome_capture: "atome_capture", atome_fuite: "atome_fuite",
    chrono_annonce: "chrono", chrono_case: "chrono", chrono_juste: "reussi", chrono_parfait: "reussi", chrono_bilan_bon: "reussi",
    chrono_proche: "rate", chrono_faux: "rate", chrono_bilan_rate: "rate",
    plateau_avance: "plateau", piege: "plateau", piege_ia: "plateau", teleport: "plateau", revision: "plateau", prison: "plateau",
    retour_epoque: "plateau", route_detour: "plateau", route_raccourcie: "plateau", cadeau_case: "plateau", tour_fini: "tour_fini",
    cadeau_terne: "cadeau", cadeau_brillant: "cadeau", cadeau_eblouissant: "cadeau", cadeau_repete: "cadeau",
    farce: "farce", mur_honte: "honte",
    pot_egal: null, pot_genereux: null, pot_premier: null, pot_radin: null, ultimatum: null, ultimatum_paye: null, ultimatum_refuse: null,
    faveur_furieuse: null, faveur_nulle: null, faveur_remontee: null, mode_test: null, mur_force: null, mur_libere: null, rattrapage_reussi: null, rattrapage_rate: null, piege_question: null, piege_dejoue: null, piege_declenche: null,
  };
  function lignesTheme(contenu, partie, ctx, theme) {
    var g = theme && GROUPE_THEME[ctx], cle = g && "theme_" + g + "@" + theme, l = cle && contenu.commentairesPar[cle];
    if (!l || !l.length || tirage(ctx + "|" + theme + "|" + partie.journal.length + "|" + (partie.repliques[cle] || []).length, 5) >= 3) return null;
    return { cle: cle, lignes: l };
  }

  // Choisit une réplique pour le premier contexte de la liste qui en a. Dans chaque contexte,
  // aucune réplique ne revient avant que toutes aient été dites. Retient le choix dans la partie.
  // v18 : `theme` (facultatif), l'arbre de l'épreuve ; la réplique le garde, pour le masque et l'aparté.
  function replique(contenu, partie, contextes, alea, vars, theme) {
    alea = alea || Math.random;
    // v27 : furieuse, elle ne plaisante plus. Chaque moment prend sa version sèche, sans ligne d'arbre.
    var fav = faveurIA(contenu, partie, maintenant(partie)), ton = tonDe(contenu, partie), furieuse = !ton && !!(fav && fav.palier.id === "furieuse");
    for (var i = 0; i < contextes.length; i++) {
      var ctx = contextes[i], lignes = contenu.commentairesPar[ctx];
      if (ton) {
        // Un ton choisi : sa version du moment, sinon celle de son groupe, sinon sa réplique passe-partout. Les lignes
        // d'arbre ne viennent que des packs qui parlent sur ce ton.
        var pre = "ton." + ton + ".";
        var ek = [pre + ctx, pre + (GROUPE_THEME[ctx] || ""), pre + "defaut"].filter(function (k) { return (contenu.commentairesPar[k] || []).length; })[0];
        if (!lignes || !lignes.length || !ek) continue;
        var lte = (contenu.tonArbres || {})[theme] === ton ? lignesTheme(contenu, partie, ctx, theme) : null;
        if (lte) { lignes = lte.lignes; ek = lte.cle; } else lignes = contenu.commentairesPar[ek];
        var vuesE = partie.repliques[ek] || [], frE = lignes.filter(function (l) { return vuesE.indexOf(l.id) < 0; });
        if (!frE.length) { vuesE = vuesE.slice(0, 1); frE = lignes.filter(function (l) { return vuesE.indexOf(l.id) < 0; }); }
        var chE = frE[Math.floor(alea() * frE.length)];
        partie.repliques[ek] = [chE.id].concat(vuesE);
        var outE = habiller(contenu, chE, vars);
        outE.contexte = ctx; outE.expression = expression(contenu, ctx);
        if (theme) outE.theme = theme;
        return outE;
      }
      if (furieuse && FURIEUSE[ctx] !== null) {
        var fc = "furieuse_" + (FURIEUSE[ctx] || GROUPE_THEME[ctx] || "defaut");
        if (contenu.commentairesPar[fc] && contenu.commentairesPar[fc].length) { ctx = fc; lignes = contenu.commentairesPar[fc]; }
      }
      if (!lignes || !lignes.length) continue;
      var lt = /^furieuse_/.test(ctx) ? null : lignesTheme(contenu, partie, ctx, theme), cle = ctx;
      if (lt) { lignes = lt.lignes; cle = lt.cle; }
      var vues = partie.repliques[cle] || [];
      var fraiches = lignes.filter(function (l) { return vues.indexOf(l.id) < 0; });
      if (!fraiches.length) {
        // Contexte épuisé : on repart de zéro, sauf la dernière dite, pour ne pas l'enchaîner.
        vues = vues.slice(0, 1);
        fraiches = lignes.filter(function (l) { return vues.indexOf(l.id) < 0; });
      }
      var choix = fraiches[Math.floor(alea() * fraiches.length)];
      partie.repliques[cle] = [choix.id].concat(vues);
      var out = habiller(contenu, choix, vars);
      // Une ligne d'arbre garde le contexte d'origine : l'expression du masque suit le moment, pas le thème.
      if (lt) { out.contexte = ctx; out.expression = expression(contenu, ctx); }
      if (theme) out.theme = theme;
      return out;
    }
    return null;
  }

  // Réplique d'accueil : la même toute la journée, sans rien modifier dans la partie.
  function repliqueDuJour(contenu, partie, t) {
    var ctx = "accueil";
    if (partie.retour && joursEntre(partie.retour, t) === 0) ctx = "retour";
    else if (rappelsDus(contenu, partie, t).some(function (k) { return joursEntre(partie.competences[k.id].prochainRappel, t) >= 3; })) ctx = "retards";
    else {
      // v10 : hors des jours ordinaires, l'IA parle de ce qu'elle ressent pour vous.
      var fav = faveurIA(contenu, partie, t);
      if (fav && fav.palier.id !== "contente" && contenu.commentairesPar["faveur_" + fav.palier.id]) ctx = "faveur_" + fav.palier.id;
    }
    // v12 : des questions ratées aujourd'hui et pas encore effacées : l'IA vous envoie au mur de la honte.
    if (ctx !== "retour" && contenu.commentairesPar.mur_honte && murDeLaHonte(contenu, partie, t, 0).restantes) ctx = "mur_honte";
    // v27 : à 0, le jeu est fermé ; le lendemain, elle annonce qu'elle reprend, du bout des lèvres.
    var fv = faveurIA(contenu, partie, t);
    if (fv && partie.punition && contenu.commentairesPar.mur_force) ctx = "mur_force";
    else if (fv && fv.fermee && contenu.commentairesPar.faveur_nulle) ctx = "faveur_nulle";
    else if (fv && partie.faveur.remontee === cleJour(t) && contenu.commentairesPar.faveur_remontee) ctx = "faveur_remontee";
    else if (fv && fv.palier.id === "furieuse" && ctx !== "faveur_furieuse") ctx = FURIEUSE[ctx] === null ? ctx : "furieuse_" + (FURIEUSE[ctx] || "defaut");
    var ton = tonDe(contenu, partie), cp = contenu.commentairesPar, pre = "ton." + ton + ".";
    if (ton && cp[pre + "accueil"]) ctx = partie.punition && cp[pre + "mur_force"] ? pre + "mur_force" :
      ctx === "mur_honte" && cp[pre + "honte"] ? pre + "honte" : cp[pre + ctx] ? pre + ctx : pre + "accueil";
    var lignes = contenu.commentairesPar[ctx] || contenu.commentairesPar.accueil;
    if (!lignes || !lignes.length) return null;
    return habiller(contenu, lignes[Math.floor(debutJour(t) / JOUR) % lignes.length]);
  }

  var Moteur = {
    choisirLangue: choisirLangue, langue: langue, TX: TX, __: __, ordinalSiecle: ordinalSiecle, traduireChaines: traduireChaines,
    FORMAT_PARTIE: FORMAT_PARTIE,
    indexerContenu: indexerContenu,
    reglage: reglage, tonDe: tonDe, dramaturgie: dramaturgie, packsEcartes: packsEcartes, succesAbsent: succesAbsent, REGLAGES: REGLAGES, allumeParDefaut: allumeParDefaut, allumerPack: allumerPack, reglagesDesPacks: reglagesDesPacks,
    packsEteints: packsEteints, filtrerPacks: filtrerPacks, verifierPaquet: verifierPaquet, ajouterPaquet: ajouterPaquet, ajouterTextes: ajouterTextes, packDe: packDe, accorderPartie: accorderPartie,
    maintenant: maintenant,
    debutJour: debutJour,
    ajouterJours: ajouterJours,
    joursEntre: joursEntre,
    nouvellePartie: nouvellePartie,
    migrer: migrer,
    statut: statut,
    debloque: debloque,
    estMaitrisee: estMaitrisee,
    xpParStat: xpParStat,
    niveau: niveau, xpRappel: xpRappel,
    niveauGlobal: niveauGlobal,
    melanger: melanger,
    tirerQuestions: tirerQuestions,
    lireNombre: lireNombre,
    corriger: corriger,
    terminerQuiz: terminerQuiz,
    routeTour: routeTour, caseN: caseN, anneeDe: anneeDe, tirerCases: tirerCases, caseAtteinte: caseAtteinte,
    remanierRoute: remanierRoute,
    caseDecouverte: caseDecouverte, voirToutesCases: voirToutesCases,
    caseOubliee: caseOubliee,
    epreuvePerdue: epreuvePerdue,
    terminerRappel: terminerRappel,
    rappelsDus: rappelsDus,
    prochainsRappels: prochainsRappels,
    disponibles: disponibles,
    suggestion: suggestion,
    verifierSucces: verifierSucces,
    verifierRecompenses: verifierRecompenses,
    marquerJour: marquerJour,
    estEclair: estEclair,
    noterVisite: noterVisite,
    avancerHorloge: avancerHorloge,
    rangAvatar: rangAvatar,
    apparence: apparence, couleursTenue: couleursTenue, choisirApparence: choisirApparence, tenueDebloquee: tenueDebloquee, annoncerTenues: annoncerTenues, humeurPerso: humeurPerso, humeurPersoActive: humeurPersoActive,
    pouvoirs: pouvoirs, pouvoir: pouvoir, utiliserPouvoir: utiliserPouvoir, annoncerPouvoirs: annoncerPouvoirs,
    replique: replique,
    repliqueDuJour: repliqueDuJour,
    themeDe: themeDe, themeCase: themeCase, themeEpreuve: themeEpreuve,
    masqueActuel: masqueActuel, masqueDebloque: masqueDebloque, masquePourTon: masquePourTon, aparte: aparte,
    gloiresIle: gloiresIle, suivreGloire: suivreGloire, choixIA: choixIA, serieProposable: serieProposable, lancerSerie: lancerSerie, abandonnerSerie: abandonnerSerie, serieReprenable: serieReprenable, reprendreSerie: reprendreSerie, serieEnCours: serieEnCours, casesParTour: casesParTour, derniereCase: derniereCase, arbreFini: arbreFini, tirerEvenement: tirerEvenement, choixArbre: choixArbre, tarifSucces: tarifSucces, tenterUltimatum: tenterUltimatum, repondreUltimatum: repondreUltimatum, exigence: exigence, retirerNiveaux: retirerNiveaux, agacerIA: agacerIA, potPossible: potPossible, corrompre: corrompre, dateAtteinte: dateAtteinte, humeur: humeur, revisionEnCours: revisionEnCours, compARevisier: compARevisier, arbreOuvert: arbreOuvert, specialDe: specialDe, ennemisPlateau: ennemisPlateau, tirerDuel: tirerDuel, terminerDuel: terminerDuel,
    faveurIA: faveurIA, radoucirIA: radoucirIA, jeuFerme: jeuFerme, purger: purger, questionRattrapage: questionRattrapage, repondreRattrapage: repondreRattrapage, themesCorvee: themesCorvee, fichesImposees: fichesImposees, piegeIA: piegeIA, masquesDuJour: masquesDuJour, reglesDuJour: reglesDuJour, questionsQuiz: questionsQuiz, seuilAtome: seuilAtome,
    atomeSauvage: atomeSauvage, tirerCombat: tirerCombat, astuceNumero: astuceNumero, atomeDit: atomeDit, lectureCouches: lectureCouches, dessinCouches: dessinCouches, COULEURS_COUCHES: COULEURS_COUCHES, terminerCombat: terminerCombat, laisserPartir: laisserPartir, acheter: acheter, duelBloquant: duelBloquant, piegeEnAttente: piegeEnAttente, masterclassImposee: masterclassImposee, masterclassLue: masterclassLue, questionPiege: questionPiege, repondrePiege: repondrePiege, choisirSuite: choisirSuite, ilePresente: ilePresente, exodeIle: exodeIle, placesIle: placesIle, modeIle: modeIle, chercherMateriau: chercherMateriau, defiIle: defiIle, construireIle: construireIle, etatAmenagement: etatAmenagement, agesIle: agesIle, conditionRemplie: conditionRemplie, savoirOuvertIle: savoirOuvertIle, reglerEffort: reglerEffort, chantierExceptionnel: chantierExceptionnel, annonceAlea: annonceAlea, preparerAlea: preparerAlea, forcerAlea: forcerAlea, ressourcesIle: ressourcesIle, visitesIle: visitesIle, repondreVisiteur: repondreVisiteur, passerAge: passerAge, epreuveIle: epreuveIle, epreuveFaite: epreuveFaite, queteIle: queteIle, ramasserIle: ramasserIle, reussirEpreuve: reussirEpreuve, troublesIle: troublesIle, questionQuartier: questionQuartier, ouvrirQuartier: ouvrirQuartier, niveauxIle: niveauxIle, chasserParasites: chasserParasites, objectifIle: objectifIle, ile: ile, etatInstallation: etatInstallation, listeDonjons: listeDonjons, donjonDe: donjonDe, donjonOuvert: donjonOuvert, donjonsOuverts: donjonsOuverts, arbreReussi: arbreReussi, etatDonjon: etatDonjon, bilanDonjon: bilanDonjon, atelierCourant: atelierCourant, piecesEnPanne: piecesEnPanne, entrerDonjon: entrerDonjon, epreuveAtelier: epreuveAtelier, verifierEpreuve: verifierEpreuve, questionsAtelier: questionsAtelier, finirAtelier: finirAtelier, questionBug: questionBug, chasserBug: chasserBug, allumer: allumer, repliqueDonjon: repliqueDonjon, listeProces: listeProces, procesDe: procesDe, procesOuvert: procesOuvert, etatProces: etatProces, maxSalle: maxSalle, itemsSalle: itemsSalle, optionsEchange: optionsEchange, votesJury: votesJury, salleProces: salleProces, entrerProces: entrerProces, repondreSalle: repondreSalle, scoreProces: scoreProces, verdictProces: verdictProces, repliqueProces: repliqueProces, entreesDonjons: entreesDonjons, dessinerParcours: dessinerParcours, formeParcours: formeParcours, bornesBonusJouer: bornesBonusJouer, emplettesIA: emplettesIA, empletteAVoir: empletteAVoir, utiliser: utiliser, enPoche: enPoche, joker: joker, relancerAtome: relancerAtome, enRayon: enRayon, boutique: boutique, articleDe: articleDe, arbreAchete: arbreAchete, estCapture: estCapture, texteMasse: texteMasse,
    ficheBestiaire: ficheBestiaire, cadeauPossible: cadeauPossible, donnerObjet: donnerObjet, surnom: surnom, tirerButin: tirerButin, butinOuvert: butinOuvert, chanceButin: chanceButin, savantActuel: savantActuel, rencontrer: rencontrer, rencontre: rencontre, tenterFarce: tenterFarce, farceActive: farceActive, rendreVisage: rendreVisage, nomIA: nomIA,
    expression: expression,
    bonusDuJour: bonusDuJour,
    valeurEpreuve: valeurEpreuve,
    deplacer: deplacer,
    avancerPion: avancerPion,
    cleJour: cleJour,
    jouerPlateau: jouerPlateau,
    murDeLaHonte: murDeLaHonte,
    reglesChrono: reglesChrono, etatChrono: etatChrono, creneau: creneau, anneeDuCreneau: anneeDuCreneau, texteCreneau: texteCreneau, texteSiecle: texteSiecle,
    reservoirChrono: reservoirChrono, chronoEnAttente: chronoEnAttente, offreChrono: offreChrono, chronoPossible: chronoPossible, chronoActif: chronoActif, chronoSpontane: chronoSpontane,
    lancerChrono: lancerChrono, jeuChrono: jeuChrono, repondreChrono: repondreChrono, terminerChrono: terminerChrono, statsChrono: statsChrono,
    retenterOubli: retenterOubli,
  };

  if (typeof module === "object" && module.exports) module.exports = Moteur;
  else racine.Moteur = Moteur;
})(typeof globalThis !== "undefined" ? globalThis : this);
