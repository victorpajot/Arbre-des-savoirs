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

  // --- Contenu ---------------------------------------------------------------

  // `extras` (facultatif) : { commentaires, objets, avatar, ia, plateau, frise, bibliotheque }, les fichiers du même nom.
  function indexerContenu(regles, skills, questions, succes, extras) {
    extras = extras || {};
    var c = {
      regles: regles,
      stats: regles.stats,
      competences: skills.competences,
      questions: questions.questions,
      succes: succes.succes,
      objets: extras.objets ? extras.objets.objets : [],
      cabinet: extras.objets || null,
      avatar: extras.avatar || null,
      narrateur: extras.commentaires ? extras.commentaires.narrateur : null,
      apartes: extras.commentaires && extras.commentaires.apartes ? extras.commentaires.apartes : [],
      ia: extras.ia || null,
      plateau: extras.plateau || null,
      evenements: extras.frise ? extras.frise.evenements : [],
      frise: extras.frise || null,
      livres: extras.bibliotheque ? extras.bibliotheque.livres : [],
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
    return c;
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
      avatar: { tete: null, visage: null, main: null, savant: null },
      compteurs: {
        quizParfaits: 0, quizRates: 0, rappelsReussis: 0, serieRappels: 0, perdues: 0, regagnees: 0,
        quizJoues: 0, quizEclairRates: 0, quizZero: 0, quizNuit: 0, quizAube: 0, chronoParfaits: 0,
        reponsesEclairFausses: 0, rappelsRetard: 0, retours: 0, modeTest: 0, parfaitsParStat: {},
        eurekas: 0, sortiesPrison: 0, reculs: 0,
      },
      jours: [],
      journal: [],
      repliques: {},
      evenements: {},
      livres: {},
      masque: null,
      masques: {},
      farce: null,
      plateau: nouveauPlateau(),
      derniereVisite: t,
      retour: null,
      options: { chrono: false },
    };
  }

  function nouveauPlateau() {
    return { position: 1, atteinte: 1, tours: 0, visites: { 1: 1 }, prison: 0, quarantaine: 0, historique: [], bonus: null };
  }

  // Remet une partie lue (stockage, import) au format courant.
  // v1 → v2 : nouveaux compteurs, objets, accessoires et avatar ; la progression reste intacte.
  // v2 → v3 : plateau (départ à la case du feu), frise, bibliothèque, masque de l'IA, répliques retenues par contexte.
  // v3 → v4 : les rappels déjà réussis sont repayés au nouveau barème (XP croissante par étape) ; avatar savant.
  // v5 (même format) : le masque choisi par le joueur disparaît, la farce de l'IA apparaît.
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

  // Statut affiché d'une compétence.
  // verrouillee : prérequis manquants ; disponible : quiz jouable ;
  // maitrisee / a_reviser : acquise, rappel à venir ou dû ;
  // gelee (drapeau) : acquise mais un prérequis a été perdu, elle ne débloque plus rien.
  function statut(contenu, partie, id, t) {
    var k = contenu.parId[id];
    var prerequisOk = k.prerequis.every(function (p) { return debloque(contenu, partie, p); });
    var e = etatComp(partie, id);
    if (e && e.maitrise) {
      return {
        etat: t >= e.prochainRappel ? "a_reviser" : "maitrisee",
        gelee: !prerequisOk,
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
    var v = lireNombre(reponse);
    return !isNaN(v) && Math.abs(v - question.reponse) <= (question.tolerance || 0) + 1e-9;
  }

  // --- Actions ---------------------------------------------------------------

  // Bonus des bonnes réponses données avec le chrono activé.
  function bonusChrono(contenu, resultats) {
    return resultats.filter(function (x) { return x.correct && x.chrono; }).length * contenu.regles.chrono.bonus_xp_par_bonne_reponse;
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

  // Termine un quiz d'apprentissage. `resultats` : [{id, correct, chrono, ms}] ; `infos` (facultatif) : {duree} en ms.
  function terminerQuiz(contenu, partie, id, resultats, t, infos) {
    var r = contenu.regles, c = partie.compteurs, k = contenu.parId[id];
    var bonnes = resultats.filter(function (x) { return x.correct; }).length;
    var total = resultats.length;
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
    var xp = 0;
    if (reussi) {
      xp = bonnes * r.xp.par_bonne_reponse + r.xp.bonus_maitrise + bonusChrono(contenu, resultats);
      if (e.perdue) partie.compteurs.regagnees++;
      e.maitrise = true;
      e.maitriseDepuis = t;
      e.palier = 0;
      e.prochainRappel = ajouterJours(t, r.rappels.intervalles_jours[0]);
      e.xp = xp;
    } else {
      partie.compteurs.quizRates++;
    }
    noter(partie, t, { type: "quiz", comp: id, bonnes: bonnes, total: total, xp: xp, source: "quiz" });
    partie.maj = t;
    var contextes = [];
    if (bonnes === 0) contextes.push("quiz_zero");
    if (nuit) contextes.push("nuit");
    if (reussi) contextes.push(parfait ? (k.rang === 1 ? "quiz_parfait_facile" : "quiz_parfait") : "quiz_reussi");
    else contextes.push(k.rang === 1 ? "quiz_rate_facile" : "quiz_rate");
    var chrono = resultats.length > 0 && resultats.every(function (x) { return x.chrono; });
    var jouer = !!(infos && infos.jouer);
    var dep = jouerPlateau(contenu, partie, { type: "quiz", comp: id }, { reussi: reussi, parfait: parfait, chrono: chrono, jouer: jouer }, t);
    var rec = verifierRecompenses(contenu, partie, t);
    if (rec.masque) contextes.splice(contextes.length - 1, 0, "masque");
    var fa = reussi ? null : tenterFarce(contenu, partie, t, infos && infos.alea);
    return { issue: reussi ? "maitrisee" : "echec", bonnes: bonnes, total: total, xp: xp, prochainRappel: e.prochainRappel,
      nouveauxSucces: rec.succes, nouveauxObjets: rec.objets, nouveauxAccessoires: rec.accessoires, nouveauxSavants: rec.savants,
      nouveauxEvenements: rec.evenements, nouveauxLivres: rec.livres, masque: rec.masque, plateau: dep, contextes: contextes, farce: fa, jouer: jouer };
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
    var bonnes = resultats.filter(function (x) { return x.correct; }).length;
    var reussi = bonnes >= r.rappels.bonnes_reponses_min;
    var retard = Math.max(0, joursEntre(e.prochainRappel, t));
    retenirQuestions(e, resultats.map(function (x) { return x.id; }));
    marquerJour(partie, t);
    var nuit = compterSession(partie, resultats, t);
    if (retard >= 7) partie.compteurs.rappelsRetard++;
    var xp = 0, xpPerdue = 0;
    if (reussi) {
      var iv = r.rappels.intervalles_jours;
      e.palier = (e.palier || 0) + 1;
      e.prochainRappel = ajouterJours(t, iv[Math.min(e.palier, iv.length - 1)]);
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
    noter(partie, t, { type: "rappel", comp: id, bonnes: bonnes, total: resultats.length, xp: reussi ? xp : -xpPerdue, source: "rappel" });
    partie.maj = t;
    var contextes = [];
    if (!reussi) contextes.push("rappel_perdu");
    if (nuit) contextes.push("nuit");
    if (reussi && retard >= 3) contextes.push("rappel_retard");
    if (reussi) contextes.push("rappel_reussi");
    var jouer = !!(infos && infos.jouer);
    var dep = jouerPlateau(contenu, partie, { type: "rappel", comp: id }, { reussi: reussi, parfait: false, chrono: false, jouer: jouer }, t);
    var rec = verifierRecompenses(contenu, partie, t);
    if (rec.masque) contextes.splice(contextes.length - 1, 0, "masque");
    var fa = reussi ? null : tenterFarce(contenu, partie, t, infos && infos.alea);
    return { issue: reussi ? "reussi" : "perdue", bonnes: bonnes, total: resultats.length, xp: xp, xpPerdue: xpPerdue, prochainRappel: e.prochainRappel,
      retard: retard, nouveauxSucces: rec.succes, nouveauxObjets: rec.objets, nouveauxAccessoires: rec.accessoires, nouveauxSavants: rec.savants,
      nouveauxEvenements: rec.evenements, nouveauxLivres: rec.livres, masque: rec.masque, plateau: dep, contextes: contextes, farce: fa, jouer: jouer };
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
    var base = epreuve.type === "rappel" ? r.valeurs.rappel : r.valeurs.quiz_rang[String(k.rang)];
    var duJour = k.stat === bonusDuJour(contenu, partie, t) ? r.bonus.du_jour : 0;
    return {
      base: base, duJour: duJour, total: base + duJour,
      parfait: epreuve.type === "quiz" ? r.bonus.parfait : 0,
      chrono: epreuve.type === "quiz" ? r.bonus.chrono : 0,
      echec: epreuve.type === "rappel" ? r.echec.rappel : r.echec.quiz,
    };
  }

  function caseN(contenu, n) {
    return contenu.plateau.cases[n - 1];
  }

  // Applique le résultat d'une épreuve au pion. `issue` : {reussi, parfait, chrono, jouer}.
  // `jouer` : l'épreuve a été lancée par le bouton « Jouer », l'IA l'a choisie ; réussie, elle rapporte un bonus.
  function jouerPlateau(contenu, partie, epreuve, issue, t) {
    if (!contenu.plateau) return null;
    var v = valeurEpreuve(contenu, partie, epreuve, t), pl = partie.plateau, c = partie.compteurs;
    var bonusJouer = issue.reussi && issue.jouer ? (contenu.plateau.regles.bonus.jouer || 0) : 0;
    var valeur = issue.reussi ? v.total + (issue.parfait ? v.parfait : 0) + (issue.chrono ? v.chrono : 0) + bonusJouer : v.echec;
    var etapes = [];
    if (pl.prison > 0 && issue.parfait) {
      pl.prison--;
      etapes.push({ type: pl.prison ? "prison_reste" : "prison_liberation" });
      if (!pl.prison) c.sortiesPrison++;
    }
    var dep = deplacer(contenu, partie, valeur, t, epreuve.type);
    dep.etapes = etapes.concat(dep.etapes);
    dep.contextes = contextesPlateau(dep);
    dep.valeurs = v;
    dep.bonusJouer = bonusJouer;
    return dep;
  }

  function contextesPlateau(dep) {
    var vus = {}, out = [];
    dep.etapes.forEach(function (e) {
      var ctx = { prison_liberation: "prison_liberation", prison: "prison", bloque_prison: "prison", eureka: "eureka", recul: "piege",
        retour_epoque: "retour_epoque", quarantaine: "quarantaine", bloque_quarantaine: "quarantaine", tour_fini: "tour_fini" }[e.type];
      if (ctx && !vus[ctx]) { vus[ctx] = 1; out.unshift(ctx); }
    });
    if (dep.a !== dep.de && dep.valeur > 0) out.push("plateau_avance");
    return out;
  }

  // Déplace le pion de `valeur` cases (négatif : recul simple, sans effet de case).
  // Mode test : on peut l'appeler directement pour parcourir le plateau.
  function deplacer(contenu, partie, valeur, t, cause) {
    var pl = partie.plateau, R = contenu.plateau.regles, c = partie.compteurs;
    var dur = pl.tours > 0, mult = dur ? R.tour_suivant.multiplicateur_recul : 1;
    var de = pl.position, etapes = [], chemin = [de];
    function poser(n) {
      pl.position = n;
      chemin.push(n);
      pl.visites[n] = (pl.visites[n] || 0) + 1;
      if (n > pl.atteinte) pl.atteinte = n;
    }
    function avancer(n) {
      var cible = pl.position + n;
      if (cible >= R.arrivee) {
        poser(R.arrivee);
        etapes.push({ type: "tour_fini", tour: pl.tours + 1 });
        pl.tours++;
        pl.atteinte = R.arrivee;
        pl.position = R.depart;
        chemin.push(R.depart);
        return false;
      }
      poser(cible);
      return true;
    }
    if (valeur < 0 && pl.prison > 0) etapes.push({ type: "bloque_prison", reste: pl.prison });
    else if (valeur < 0) {
      poser(Math.max(R.depart, pl.position + valeur));
      if (pl.position < de) { c.reculs++; etapes.push({ type: "recul", n: de - pl.position, cause: "echec" }); }
    } else if (valeur > 0) {
      if (pl.prison > 0) etapes.push({ type: "bloque_prison", reste: pl.prison });
      else if (pl.quarantaine > 0) { pl.quarantaine--; etapes.push({ type: "bloque_quarantaine", reste: pl.quarantaine }); }
      else {
        var pas = valeur, garde = 0;
        while (avancer(pas) && garde++ < MAX_ENCHAINEMENT) {
          var sp = caseN(contenu, pl.position).special;
          if (!sp) break;
          if (sp.type === "eureka") { c.eurekas++; etapes.push({ type: "eureka", case: pl.position, n: pas }); continue; }
          if (sp.type === "avance") { pas = sp.n; etapes.push({ type: "avance", case: pl.position, n: sp.n }); continue; }
          if (sp.type === "recul") {
            var avant = pl.position;
            poser(Math.max(R.depart, pl.position - sp.n * mult));
            c.reculs++;
            etapes.push({ type: "recul", case: avant, n: avant - pl.position, cause: "piege" });
          } else if (sp.type === "retour_epoque") {
            var depuis = pl.position;
            poser(sp.vers);
            c.reculs++;
            etapes.push({ type: "retour_epoque", case: depuis, n: depuis - sp.vers });
          } else if (sp.type === "quarantaine") {
            pl.quarantaine = sp.n * mult;
            etapes.push({ type: "quarantaine", case: pl.position, n: pl.quarantaine });
          } else if (sp.type === "prison") {
            pl.prison = dur ? R.tour_suivant.quiz_parfaits_prison : 1;
            etapes.push({ type: "prison", case: pl.position, n: pl.prison });
          }
          break;
        }
      }
    }
    // chemin : les cases où le pion se pose, dans l'ordre, pour l'animer case par case.
    var dep = { de: de, a: pl.position, valeur: valeur, cause: cause, tour: pl.tours, etapes: etapes, chemin: chemin, t: t };
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

  // --- Aujourd'hui -----------------------------------------------------------

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
      case "branches_completes": return contenu.stats.filter(function (s) { return contenu.parStat[s.id].every(function (k) { return estMaitrisee(partie, k.id); }); }).length >= cond.n;
      case "rang_maitrise": return maitrisees.some(function (k) { return k.rang >= cond.rang; });
      case "toutes_branches": return contenu.stats.every(function (s) { return contenu.parStat[s.id].some(function (k) { return estMaitrisee(partie, k.id); }); });
      case "rappels_reussis": return c.rappelsReussis >= cond.n;
      case "serie_rappels": return c.serieRappels >= cond.n;
      case "duree_maitrise": return maitrisees.some(function (k) { return joursEntre(partie.competences[k.id].maitriseDepuis, t) >= cond.jours; });
      case "niveau_stat":
        var xp = xpParStat(contenu, partie);
        return contenu.stats.some(function (s) { return niveau(contenu, xp[s.id]).niveau >= cond.niveau; });
      case "competences_regagnees": return c.regagnees >= cond.n;
      case "competences_perdues": return c.perdues >= cond.n;
      case "jours_actifs": return partie.jours.length >= cond.n;
      case "case_atteinte": return partie.plateau.tours > 0 || partie.plateau.atteinte >= cond.n;
      case "case_visitee": return (partie.plateau.visites[cond.n] || 0) > 0;
      case "tours_plateau": return partie.plateau.tours >= cond.n;
      case "sorties_prison": return c.sortiesPrison >= cond.n;
      case "eurekas": return c.eurekas >= cond.n;
      case "reculs": return c.reculs >= cond.n;
      default: return false;
    }
  }

  // Débloque succès, objets du cabinet et accessoires d'avatar. Certains dépendent des autres
  // (« 30 succès », « 10 objets », un accessoire lié à un succès) : on boucle jusqu'à stabilité.
  function verifierRecompenses(contenu, partie, t) {
    var out = { succes: [], objets: [], accessoires: [], savants: [], evenements: [], livres: [], masque: null };
    var familles = [
      ["succes", contenu.succes, partie.succes],
      ["objets", contenu.objets, partie.objets],
      ["accessoires", contenu.avatar ? contenu.avatar.accessoires : [], partie.accessoires],
      ["savants", contenu.avatar && contenu.avatar.savants ? contenu.avatar.savants : [], partie.savants || (partie.savants = {})],
      ["evenements", contenu.evenements, partie.evenements],
      ["livres", contenu.livres, partie.livres],
    ];
    var change = true;
    while (change) {
      change = false;
      familles.forEach(function (f) {
        f[1].forEach(function (x) {
          if (!f[2][x.id] && conditionRemplie(contenu, partie, x.condition, t)) {
            f[2][x.id] = t;
            out[f[0]].push(x);
            change = true;
          }
        });
      });
    }
    if (contenu.ia) {
      // Un masque nouvellement débloqué devient le dernier gagné : l'IA l'étrenne quand le ton s'y prête.
      // Le tout premier (ou le rattrapage d'une ancienne partie) se pose sans être annoncé.
      partie.masques = partie.masques || {};
      var deja = Object.keys(partie.masques).length, nouveaux = [];
      contenu.ia.masques.forEach(function (m) {
        if (!partie.masques[m.id] && (!m.condition || conditionRemplie(contenu, partie, m.condition, t))) { partie.masques[m.id] = t; nouveaux.push(m); }
      });
      if (nouveaux.length) {
        // Plusieurs d'un coup : un masque gagné par un succès précis l'emporte sur un palier.
        var precis = nouveaux.filter(function (m) { return m.condition && m.condition.type === "succes"; });
        var dernier = (precis.length ? precis : nouveaux)[(precis.length ? precis : nouveaux).length - 1];
        if (deja) { out.masque = dernier; out.masques = nouveaux; }
        partie.masque = dernier.id;
      }
      var m = masqueActuel(contenu, partie);
      if (m) partie.masque = m.id;
    }
    if (out.succes.length || out.objets.length || out.accessoires.length || out.savants.length || out.evenements.length || out.livres.length || out.masque) partie.maj = t;
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
  function masquePourTon(contenu, partie, ton, graine) {
    if (!contenu.ia) return null;
    var gagnes = contenu.ia.masques.filter(function (m) { return masqueDebloque(partie, m.id); });
    if (!gagnes.length) return contenu.ia.masques[0];
    var neuf = masqueActuel(contenu, partie), vus = partie.masques || {};
    if (neuf && (neuf.tons || []).indexOf(ton) >= 0 && vus[neuf.id] === Math.max.apply(null, gagnes.map(function (m) { return vus[m.id]; })) &&
        hacher(String(graine || "")) % 2 === 0) return neuf;
    var aptes = gagnes.filter(function (m) { return !m.tons || m.tons.indexOf(ton) >= 0; });
    var liste = aptes.length ? aptes : gagnes;
    return liste[hacher(ton + "|" + (graine || "")) % liste.length];
  }

  // v5 : aparté où l'IA se sert d'un objet ou d'un livre débloqué. Une réplique sur deux environ en a un.
  // Renvoie {texte, objet} ou {texte, livre}, ou null.
  function aparte(contenu, partie, ton, graine) {
    var lignes = contenu.apartes || [];
    if (!lignes.length) return null;
    var h = hacher("aparte|" + (graine || ""));
    if (h % 2) return null;
    var objets = contenu.objets.filter(function (o) { return partie.objets[o.id]; });
    var livres = (contenu.livres || []).filter(function (l) { return partie.livres && partie.livres[l.id]; });
    if (!objets.length && !livres.length) return null;
    var sorte = !livres.length ? "objet" : !objets.length ? "livre" : (h >>> 3) % 3 === 0 ? "livre" : "objet";
    var choix = lignes.filter(function (l) { return l.sorte === sorte && l.ton === ton; });
    if (!choix.length) choix = lignes.filter(function (l) { return l.sorte === sorte && l.ton === "neutre"; });
    if (!choix.length) return null;
    var ligne = choix[(h >>> 5) % choix.length];
    var chose = sorte === "objet" ? objets[(h >>> 9) % objets.length] : livres[(h >>> 9) % livres.length];
    var nom = sorte === "objet" ? chose.nom.fr : chose.titre.fr;
    if (sorte === "objet") nom = nom.charAt(0).toLowerCase() + nom.slice(1);
    var texte = ligne.texte.fr.replace(/\{(objet|livre)\}/g, nom);
    texte = texte.charAt(0).toUpperCase() + texte.slice(1);
    var out = { id: ligne.id, texte: { fr: texte } };
    out[sorte] = chose;
    return out;
  }

  // --- Bouton « Jouer » : l'IA choisit l'épreuve ------------------------------
  // Un rappel dû passe d'abord (le plus en retard). Sinon, parmi les quiz ouverts, l'IA tire une raison :
  // le bonus du jour, la stat la plus faible ou le hasard. Le choix reste le même tant qu'on n'a pas joué.
  function choixIA(contenu, partie, t) {
    var dus = rappelsDus(contenu, partie, t);
    if (dus.length) return { comp: dus[0], type: "rappel", raison: "rappel" };
    var dispo = disponibles(contenu, partie, t);
    if (!dispo.length) return null;
    var graine = hacher(cleJour(t) + "|" + partie.journal.length + "|" + (partie.cree || 0));
    var raisons = [];
    var bonus = contenu.plateau ? bonusDuJour(contenu, partie, t) : null;
    var dansBonus = dispo.filter(function (k) { return k.stat === bonus; });
    if (dansBonus.length) raisons.push({ raison: "bonus", liste: dansBonus });
    var sug = suggestion(contenu, partie, t);
    if (sug) raisons.push({ raison: "faible", liste: [sug] });
    raisons.push({ raison: "hasard", liste: dispo });
    var r = raisons[graine % raisons.length];
    return { comp: r.liste[(graine >>> 4) % r.liste.length], type: "quiz", raison: r.raison };
  }

  // --- Farces de l'IA --------------------------------------------------------
  var DUREE_FARCE = JOUR;
  var CHANCE_FARCE = 1 / 3;
  // Après une épreuve ratée, une fois sur trois : l'IA déguise l'avatar pour 24 h (accessoire ou savant).
  function tenterFarce(contenu, partie, t, alea) {
    if (!contenu.avatar) return null;
    alea = alea || Math.random;
    if (alea() >= CHANCE_FARCE) return null;
    var pool = [];
    (contenu.avatar.accessoires || []).forEach(function (a) { pool.push({ type: "accessoire", id: a.id, emplacement: a.emplacement }); });
    (contenu.avatar.savants || []).forEach(function (s) { if (partie.savants && partie.savants[s.id]) pool.push({ type: "savant", id: s.id }); });
    var av = partie.avatar || {}, actuelle = farceActive(partie, t);
    pool = pool.filter(function (f) {
      if (actuelle && actuelle.id === f.id) return false;
      return f.type === "savant" ? av.savant !== f.id : av[f.emplacement] !== f.id;
    });
    if (!pool.length) return null;
    var f = pool[Math.floor(alea() * pool.length)];
    partie.farce = { type: f.type, id: f.id, emplacement: f.emplacement || null, depuis: t, jusqua: t + DUREE_FARCE };
    return partie.farce;
  }
  function farceActive(partie, t) {
    var f = partie.farce;
    return f && t < f.jusqua ? f : null;
  }
  function rendreVisage(partie) { partie.farce = null; }

  function expression(contenu, contexte) {
    return (contenu.ia && contenu.ia.expressions[contexte]) || "neutre";
  }

  // Remplace {stat}, {n}… dans le texte d'une réplique, sans toucher au contenu.
  function habiller(contenu, ligne, vars) {
    var texte = {};
    Object.keys(ligne.texte).forEach(function (l) {
      texte[l] = ligne.texte[l].replace(/\{(\w+)\}/g, function (m, k) { return vars && vars[k] != null ? vars[k] : m; });
    });
    return { id: ligne.id, contexte: ligne.contexte, texte: texte, expression: expression(contenu, ligne.contexte) };
  }

  // Choisit une réplique pour le premier contexte de la liste qui en a. Dans chaque contexte,
  // aucune réplique ne revient avant que toutes aient été dites. Retient le choix dans la partie.
  function replique(contenu, partie, contextes, alea, vars) {
    alea = alea || Math.random;
    for (var i = 0; i < contextes.length; i++) {
      var ctx = contextes[i], lignes = contenu.commentairesPar[ctx];
      if (!lignes || !lignes.length) continue;
      var vues = partie.repliques[ctx] || [];
      var fraiches = lignes.filter(function (l) { return vues.indexOf(l.id) < 0; });
      if (!fraiches.length) {
        // Contexte épuisé : on repart de zéro, sauf la dernière dite, pour ne pas l'enchaîner.
        vues = vues.slice(0, 1);
        fraiches = lignes.filter(function (l) { return vues.indexOf(l.id) < 0; });
      }
      var choix = fraiches[Math.floor(alea() * fraiches.length)];
      partie.repliques[ctx] = [choix.id].concat(vues);
      return habiller(contenu, choix, vars);
    }
    return null;
  }

  // Réplique d'accueil : la même toute la journée, sans rien modifier dans la partie.
  function repliqueDuJour(contenu, partie, t) {
    var ctx = "accueil";
    if (partie.retour && joursEntre(partie.retour, t) === 0) ctx = "retour";
    else if (rappelsDus(contenu, partie, t).some(function (k) { return joursEntre(partie.competences[k.id].prochainRappel, t) >= 3; })) ctx = "retards";
    var lignes = contenu.commentairesPar[ctx] || contenu.commentairesPar.accueil;
    if (!lignes || !lignes.length) return null;
    return habiller(contenu, lignes[Math.floor(debutJour(t) / JOUR) % lignes.length]);
  }

  var Moteur = {
    FORMAT_PARTIE: FORMAT_PARTIE,
    indexerContenu: indexerContenu,
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
    replique: replique,
    repliqueDuJour: repliqueDuJour,
    masqueActuel: masqueActuel, masqueDebloque: masqueDebloque, masquePourTon: masquePourTon, aparte: aparte,
    choixIA: choixIA, tenterFarce: tenterFarce, farceActive: farceActive, rendreVisage: rendreVisage,
    expression: expression,
    bonusDuJour: bonusDuJour,
    valeurEpreuve: valeurEpreuve,
    deplacer: deplacer,
    avancerPion: avancerPion,
    cleJour: cleJour,
  };

  if (typeof module === "object" && module.exports) module.exports = Moteur;
  else racine.Moteur = Moteur;
})(typeof globalThis !== "undefined" ? globalThis : this);
