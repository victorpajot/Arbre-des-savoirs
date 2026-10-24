/* Moteur du jeu : règles pures, sans affichage ni stockage.
 * Le même calcul doit être reproduit à l'identique sur mobile et dans Unreal :
 * toutes les valeurs (XP, seuils, intervalles) viennent de regles.json.
 * Une « partie » est un objet JSON simple, versionné par son champ `format`.
 */
(function (racine) {
  "use strict";

  var FORMAT_PARTIE = 2;
  var JOUR = 86400000;
  var MAX_JOURNAL = 200;
  var MAX_RECENTES = 6;
  var MAX_REPLIQUES = 12;
  var ECLAIR_MS = 2000;       // réponse fausse plus rapide que ça : « éclair »
  var QUIZ_ECLAIR_MS = 60000; // quiz raté plus vite que ça
  var ABSENCE_RETOUR = 14;    // jours sans visite qui comptent comme un retour

  // --- Contenu ---------------------------------------------------------------

  // `extras` (facultatif) : { commentaires, objets, avatar }, les fichiers du même nom.
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
      avatar: { tete: null, visage: null, main: null },
      compteurs: {
        quizParfaits: 0, quizRates: 0, rappelsReussis: 0, serieRappels: 0, perdues: 0, regagnees: 0,
        quizJoues: 0, quizEclairRates: 0, quizZero: 0, quizNuit: 0, quizAube: 0, chronoParfaits: 0,
        reponsesEclairFausses: 0, rappelsRetard: 0, retours: 0, modeTest: 0, parfaitsParStat: {},
      },
      jours: [],
      journal: [],
      repliques: [],
      derniereVisite: t,
      retour: null,
      options: { chrono: false },
    };
  }

  // Remet une partie lue (stockage, import) au format courant.
  // v1 → v2 : nouveaux compteurs, objets, accessoires et avatar ; la progression reste intacte.
  function migrer(p) {
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
    out.avatar = Object.assign({ tete: null, visage: null, main: null }, p.avatar || {});
    out.jours = p.jours || [];
    out.journal = p.journal || [];
    out.repliques = p.repliques || [];
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
    var rec = verifierRecompenses(contenu, partie, t);
    return { issue: reussi ? "maitrisee" : "echec", bonnes: bonnes, total: total, xp: xp, prochainRappel: e.prochainRappel,
      nouveauxSucces: rec.succes, nouveauxObjets: rec.objets, nouveauxAccessoires: rec.accessoires, contextes: contextes };
  }

  // Termine un rappel. Réussi : l'intervalle suivant s'allonge. Raté : la compétence est perdue.
  function terminerRappel(contenu, partie, id, resultats, t) {
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
      xp = r.xp.par_rappel_reussi + bonusChrono(contenu, resultats);
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
    var rec = verifierRecompenses(contenu, partie, t);
    return { issue: reussi ? "reussi" : "perdue", bonnes: bonnes, total: resultats.length, xp: xp, xpPerdue: xpPerdue, prochainRappel: e.prochainRappel,
      retard: retard, nouveauxSucces: rec.succes, nouveauxObjets: rec.objets, nouveauxAccessoires: rec.accessoires, contextes: contextes };
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
    return { succes: [], objets: [], accessoires: [] };
  }

  // Mode test : avance l'horloge du jeu de `jours` jours (0 = retour à l'heure réelle).
  function avancerHorloge(contenu, partie, jours) {
    if (jours) {
      partie.decalage = (partie.decalage || 0) + jours * JOUR;
      partie.compteurs.modeTest++;
    } else partie.decalage = 0;
    return verifierRecompenses(contenu, partie, maintenant(partie));
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
      case "branche_complete": return contenu.parStat[cond.stat].every(function (k) { return estMaitrisee(partie, k.id); });
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
      default: return false;
    }
  }

  // Débloque succès, objets du cabinet et accessoires d'avatar. Certains dépendent des autres
  // (« 30 succès », « 10 objets », un accessoire lié à un succès) : on boucle jusqu'à stabilité.
  function verifierRecompenses(contenu, partie, t) {
    var out = { succes: [], objets: [], accessoires: [] };
    var familles = [
      ["succes", contenu.succes, partie.succes],
      ["objets", contenu.objets, partie.objets],
      ["accessoires", contenu.avatar ? contenu.avatar.accessoires : [], partie.accessoires],
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
    if (out.succes.length || out.objets.length || out.accessoires.length) partie.maj = t;
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

  // Choisit une réplique du narrateur pour le premier contexte de la liste qui en a,
  // en évitant les dernières déjà entendues. Retient le choix dans la partie.
  function replique(contenu, partie, contextes, alea) {
    alea = alea || Math.random;
    for (var i = 0; i < contextes.length; i++) {
      var lignes = contenu.commentairesPar[contextes[i]];
      if (!lignes || !lignes.length) continue;
      var fraiches = lignes.filter(function (l) { return partie.repliques.indexOf(l.id) < 0; });
      var choix = (fraiches.length ? fraiches : lignes)[Math.floor(alea() * (fraiches.length || lignes.length))];
      partie.repliques.unshift(choix.id);
      partie.repliques.length = Math.min(partie.repliques.length, MAX_REPLIQUES);
      return choix;
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
    return lignes[Math.floor(debutJour(t) / JOUR) % lignes.length];
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
    niveau: niveau,
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
  };

  if (typeof module === "object" && module.exports) module.exports = Moteur;
  else racine.Moteur = Moteur;
})(typeof globalThis !== "undefined" ? globalThis : this);
