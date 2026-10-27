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
      figures: skills.figures || {},
      questions: questions.questions,
      succes: succes.succes,
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
      objetIA: null,
      atomes: {},
      sauvages: [],
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
    return { position: 1, atteinte: 1, tours: 0, visites: { 1: 1 }, prison: 0, quarantaine: 0, historique: [], bonus: null, ennemis: null, speciaux: {} };
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
    // v6 : butin en attente (conditions remplies, pas encore tombé). Ce qui est déjà gagné reste acquis.
    out.gagnables = p.gagnables || {};
    // v7 : ennemis, duels et cadeaux à l'IA.
    out.bestiaire = p.bestiaire || {};
    out.duel = p.duel || null;
    out.cadeaux = Object.assign({ jour: null, donnes: {} }, p.cadeaux || {});
    out.objetIA = p.objetIA || null;
    // v9 : tableau périodique (z → fiche) et atomes sauvages en attente de combat.
    out.atomes = p.atomes || {};
    out.sauvages = p.sauvages || [];
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

  // v7 : un arbre est ouvert s'il est fondamental, si son succès de pionnier est obtenu, si le joueur
  // y a déjà joué (anciennes parties) ou si l'option de démo ouvre tout.
  function arbreOuvert(contenu, partie, stat) {
    var fond = contenu.regles.arbres_fondamentaux;
    if (!fond || fond.indexOf(stat) >= 0) return true;
    if (partie.options && partie.options.tousArbres) return true;
    if (contenu.succes.some(function (s) { return s.ouvre === stat && partie.succes[s.id]; })) return true;
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
  function pionnierDe(contenu, stat) { return contenu.succes.filter(function (s) { return s.ouvre === stat; })[0] || null; }

  // Statut affiché d'une compétence.
  // verrouillee : prérequis manquants ; disponible : quiz jouable ;
  // maitrisee / a_reviser : acquise, rappel à venir ou dû ;
  // gelee (drapeau) : acquise mais un prérequis a été perdu, elle ne débloque plus rien.
  // fermee : l'arbre de la compétence n'est pas encore ouvert (v7).
  function statut(contenu, partie, id, t) {
    var k = contenu.parId[id];
    if (!arbreOuvert(contenu, partie, k.stat)) return { etat: "fermee", gelee: false };
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
    if (correct) {
      partie.oublis.forEach(function (x) { if (x.q === e.q && !x.efface && x.t <= e.t) x.efface = t; });
      partie.compteurs.hontesEffacees = (partie.compteurs.hontesEffacees || 0) + 1;
    }
    partie.maj = t;
    var rec = verifierRecompenses(contenu, partie, t);
    return { efface: !!correct, essais: e.essais, replique: replique(contenu, partie, [correct ? "honte_effacee" : "honte_ratee"]), nouveauxSucces: rec.succes };
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
    epinglerOublis(partie, id, resultats, t, "quiz");
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
    if (reussi) ajouterButin(contenu, partie, rec, { type: "quiz", comp: id }, t, infos && infos.alea);
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
    // v8 : une révision forcée ne fait pas monter le palier, et la rater ne fait pas perdre la compétence :
    // son rappel devient dû, tout de suite.
    var rv = revisionEnCours(partie), revision = !!(rv && rv.comp === id);
    if (revision) partie.revision = null;
    retenirQuestions(e, resultats.map(function (x) { return x.id; }));
    marquerJour(partie, t);
    var nuit = compterSession(partie, resultats, t);
    if (retard >= 7) partie.compteurs.rappelsRetard++;
    var xp = 0, xpPerdue = 0;
    if (revision && !reussi) {
      e.prochainRappel = t;
      partie.compteurs.serieRappels = 0;
    } else if (reussi) {
      var iv = r.rappels.intervalles_jours;
      if (!revision) e.palier = (e.palier || 0) + 1;
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
    noter(partie, t, { type: "rappel", comp: id, bonnes: bonnes, total: resultats.length, xp: reussi ? xp : -xpPerdue, source: revision ? "revision" : "rappel" });
    epinglerOublis(partie, id, resultats, t, revision ? "revision" : "rappel");
    partie.maj = t;
    var contextes = [];
    if (revision) contextes.push(reussi ? "revision_reussie" : "revision_ratee");
    else if (!reussi) contextes.push("rappel_perdu");
    if (nuit) contextes.push("nuit");
    if (!revision && reussi && retard >= 3) contextes.push("rappel_retard");
    if (!revision && reussi) contextes.push("rappel_reussi");
    var jouer = !!(infos && infos.jouer);
    var dep = revision && !reussi ? null : jouerPlateau(contenu, partie, { type: "rappel", comp: id }, { reussi: reussi, parfait: false, chrono: false, jouer: jouer }, t);
    var rec = verifierRecompenses(contenu, partie, t);
    if (reussi) ajouterButin(contenu, partie, rec, { type: "rappel", comp: id }, t, infos && infos.alea);
    if (rec.masque) contextes.splice(contextes.length - 1, 0, "masque");
    var fa = reussi || revision ? null : tenterFarce(contenu, partie, t, infos && infos.alea);
    return { revision: revision, issue: reussi ? "reussi" : revision ? "revision_ratee" : "perdue", bonnes: bonnes, total: resultats.length, xp: xp, xpPerdue: xpPerdue, prochainRappel: e.prochainRappel,
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
    // v6 : une épreuve vaut le rang de sa compétence, quiz comme rappel.
    var base = r.valeurs.quiz_rang[String(k.rang)];
    var duJour = k.stat === bonusDuJour(contenu, partie, t) ? r.bonus.du_jour : 0;
    // v10 : comblée, l'IA ajoute une case ; furieuse, elle en retire une (jamais moins d'une).
    var fav = faveurIA(contenu, partie, t), faveur = fav ? fav.palier.avance : 0;
    // v11 : les masques du jour ajoutent ou retirent des cases, et durcissent ou adoucissent le rappel raté.
    var rj = reglesDuJour(contenu, partie, t), echec = epreuve.type === "rappel" ? r.echec.rappel : r.echec.quiz;
    if (epreuve.type === "rappel") echec = Math.round(echec * rj.echec);
    return {
      base: base, duJour: duJour, faveur: faveur, masques: rj.avance, total: Math.max(1, base + duJour + faveur + rj.avance),
      parfait: epreuve.type === "quiz" ? r.bonus.parfait : 0,
      chrono: epreuve.type === "quiz" ? r.bonus.chrono : 0,
      echec: echec,
    };
  }

  function caseN(contenu, n) {
    return contenu.plateau.cases[n - 1];
  }
  // v7 : la règle spéciale d'une case, en tenant compte des cases que l'IA a déplacées.
  function specialDe(contenu, partie, n) {
    var sp = partie.plateau.speciaux;
    if (sp && Object.prototype.hasOwnProperty.call(sp, n)) return sp[n];
    return caseN(contenu, n).special || null;
  }
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
    if (!tour || !contenu.plateau) return Object.assign({}, base);
    var R = contenu.plateau.regles, graine = (partie.cree || 0) + "|" + tour;
    var postes = Object.keys(base).map(Number).sort(function (a, b) { return a - b; });
    var bete = partie.bestiaire || {};
    var choisis = contenu.ennemis.filter(function (e) { return e.id !== contenu.reserve; }).map(function (e) {
      var f = bete[e.id], vu = f && (f.victoires || f.defaites);
      return { id: e.id, score: (vu ? 0 : 1000) + (f ? f.defaites * 60 : 0) + hacher(graine + "|" + e.id) % 400 };
    }).sort(function (a, b) { return b.score - a.score; }).slice(0, postes.length).map(function (x) { return x.id; });
    choisis.sort(function (a, b) { return hacher(graine + "|ordre|" + a) - hacher(graine + "|ordre|" + b); });
    var decalage = (tour * 3) % 9 - 4, out = {};
    postes.forEach(function (n, i) {
      var visee = n + decalage;
      for (var d = 0; d < 8; d++) {
        var c = visee + (d % 2 ? -1 : 1) * Math.ceil(d / 2);
        if (c > R.depart + 1 && c < R.arrivee && !out[c] && !specialDe(contenu, partie, c)) { out[c] = choisis[i]; return; }
      }
    });
    return out;
  }

  // Applique le résultat d'une épreuve au pion. `issue` : {reussi, parfait, chrono, jouer}.
  // `jouer` : l'épreuve a été lancée par le bouton « Jouer », l'IA l'a choisie ; réussie, elle rapporte un bonus.
  function jouerPlateau(contenu, partie, epreuve, issue, t) {
    if (!contenu.plateau) return null;
    var v = valeurEpreuve(contenu, partie, epreuve, t), pl = partie.plateau, c = partie.compteurs;
    var bonusJouer = issue.reussi && issue.jouer ? (contenu.plateau.regles.bonus.jouer || 0) : 0;
    var valeur = issue.reussi ? v.total + (issue.parfait ? v.parfait : 0) + (issue.chrono ? v.chrono : 0) + bonusJouer : v.echec;
    var etapes = [];
    // v11 : l'objet tenu par l'avatar donne parfois un coup de pouce après une épreuve réussie.
    var tenu = issue.reussi && partie.avatar && partie.avatar.main && (contenu.objets || []).filter(function (o) { return o.id === partie.avatar.main; })[0];
    if (tenu && tenu.bonus && hacher(String(t) + "|" + tenu.id + "|" + partie.journal.length) % 100 < 100 * ((contenu.cabinet && contenu.cabinet.chance_bonus) || 0)) {
      var bo = tenu.bonus;
      if (bo.type === "case") valeur += bo.n;
      else if (bo.type === "butin") partie.butinAssure = true;
      else if (bo.type === "faveur") { var fv = faveurIA(contenu, partie, t); if (fv) partie.faveur = { valeur: Math.min(100, fv.valeur + bo.n), maj: t }; }
      etapes.push({ type: "bonus_objet", objet: tenu.id, bonus: bo.type, n: bo.n || 0 });
    }
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
        retour_epoque: "retour_epoque", teleport: "teleport", cadeau: "cadeau_case", revision: "revision", bloque_revision: "revision", quarantaine: "quarantaine", bloque_quarantaine: "quarantaine", tour_fini: "tour_fini", ennemi: "ennemi", duel_attente: "ennemi", atome: "atome_apparait" }[e.type];
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
    var rj = reglesDuJour(contenu, partie, t);
    // v11 : un masque peut écarter les ennemis pour la journée.
    var ennemis = rj.ennemis === "absents" ? {} : ennemisPlateau(contenu, partie);
    function avancer(n) {
      var cible = pl.position + n;
      // v7 : un ennemi sur la route arrête le pion et lance un duel ; il reste `reste` cases à faire après la victoire.
      // v9 : chaque case Mendeleïev croisée (ou atteinte) fait apparaître un atome sauvage.
      for (var e = pl.position + 1; e <= Math.min(cible, R.arrivee - 1); e++) {
        var spE = specialDe(contenu, partie, e);
        if (spE && spE.type === "mendeleiev" && contenu.atomes) etapes.push(apparition(contenu, partie, e, t));
        if (ennemis[e]) {
          poser(e);
          partie.duel = { ennemi: ennemis[e], case: e, reste: cible - e, pret: true, depuis: t };
          etapes.push({ type: "ennemi", case: e, ennemi: ennemis[e], reste: cible - e });
          return false;
        }
      }
      if (cible >= R.arrivee) {
        poser(R.arrivee);
        etapes.push({ type: "tour_fini", tour: pl.tours + 1 });
        pl.tours++;
        pl.atteinte = R.arrivee;
        pl.ennemis = null; pl.speciaux = {}; ennemis = rj.ennemis === "absents" ? {} : ennemisPlateau(contenu, partie);
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
      if (pl.position < de) { c.reculs++; etapes.push({ type: "recul", n: de - pl.position, cause: cause === "cadeau" ? "cadeau" : "echec" }); }
    } else if (valeur > 0) {
      if (pl.prison > 0) etapes.push({ type: "bloque_prison", reste: pl.prison });
      else if (pl.quarantaine > 0) { pl.quarantaine--; etapes.push({ type: "bloque_quarantaine", reste: pl.quarantaine }); }
      else if (revisionEnCours(partie)) etapes.push({ type: "bloque_revision", comp: partie.revision.comp });
      else if (partie.duel && partie.duel.case === pl.position && cause !== "duel") {
        // Un duel perdu reprend à l'épreuve réussie suivante, qui vaut alors pour la suite du trajet.
        partie.duel.reste = valeur; partie.duel.pret = true;
        etapes.push({ type: "duel_attente", case: pl.position, ennemi: partie.duel.ennemi, reste: valeur });
      } else {
        var pas = valeur, garde = 0;
        while (avancer(pas) && garde++ < MAX_ENCHAINEMENT) {
          var sp = specialDe(contenu, partie, pl.position);
          if (!sp) break;
          if (sp.type === "eureka") { c.eurekas++; etapes.push({ type: "eureka", case: pl.position, n: pas }); continue; }
          if (sp.type === "avance") { pas = sp.n; etapes.push({ type: "avance", case: pl.position, n: sp.n }); continue; }
          if (rj.pieges === "neutres" && (sp.type === "recul" || sp.type === "teleport" || sp.type === "retour_epoque")) {
            etapes.push({ type: "piege_evite", case: pl.position, regle: sp.type });
          } else if (sp.type === "recul") {
            var avant = pl.position;
            poser(Math.max(R.depart, pl.position - sp.n * mult));
            c.reculs++;
            etapes.push({ type: "recul", case: avant, n: avant - pl.position, cause: "piege" });
          } else if (sp.type === "retour_epoque" || sp.type === "teleport") {
            var depuis = pl.position;
            poser(sp.vers);
            c.reculs++;
            etapes.push({ type: sp.type, case: depuis, n: depuis - sp.vers, vers: sp.vers });
          } else if (sp.type === "cadeau") {
            var cad = tirerCadeau(contenu, partie, t);
            if (cad) {
              (partie.cadeauxCase || (partie.cadeauxCase = [])).push({ famille: cad.famille, id: cad.chose.id });
              c.cadeauxCase = (c.cadeauxCase || 0) + 1;
              etapes.push({ type: "cadeau", case: pl.position, famille: cad.famille, id: cad.chose.id });
            } else etapes.push({ type: "cadeau_vide", case: pl.position });
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
          break;
        }
      }
    }
    // Le pion a quitté la case de l'ennemi (recul) : le duel est oublié.
    if (partie.duel && partie.duel.case !== pl.position) partie.duel = null;
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
    var b = tirerButin(contenu, partie, { type: "duel" }, t, alea);
    if (b) return b;
    var tour = partie.plateau.tours + 2, proches = [];
    FAMILLES_BUTIN.forEach(function (f) {
      listeFamille(contenu, f).forEach(function (x) {
        if (partie.gagnables && partie.gagnables[cleButin(f, x.id)] && !possede(partie, f, x.id) && x.lot <= tour) proches.push({ famille: f, chose: x });
      });
    });
    if (!proches.length) return null;
    b = proches[Math.floor((alea || Math.random)() * proches.length)];
    partie[b.famille][b.chose.id] = t;
    delete partie.gagnables[cleButin(b.famille, b.chose.id)];
    if (b.famille === "masques") partie.masque = b.chose.id;
    return b;
  }

  // `resultats` : [{id, correct}]. Renvoie {gagne, ennemi, bonnes, total, plateau, recompenses, butin, premiere, fiche}.
  function terminerDuel(contenu, partie, resultats, t, alea) {
    var d = partie.duel; if (!d) return null;
    var e = contenu.ennemiParId[d.ennemi], f = ficheBestiaire(partie, d.ennemi), c = partie.compteurs;
    var bonnes = resultats.filter(function (x) { return x.correct; }).length, gagne = resultats.length > 0 && bonnes === resultats.length;
    f.dernier = t;
    var out = { gagne: gagne, ennemi: e, bonnes: bonnes, total: resultats.length, plateau: null, recompenses: null, butin: null, premiere: false, fiche: f };
    if (gagne) {
      f.victoires++; f.serie++; f.meilleure = Math.max(f.meilleure, f.serie);
      c.duelsGagnes = (c.duelsGagnes || 0) + 1;
      out.premiere = f.victoires === 1;
      delete ennemisPlateau(contenu, partie)[d.case];
      partie.duel = null;
      var dep = deplacer(contenu, partie, d.reste, t, "duel");
      dep.contextes = contextesPlateau(dep);
      out.plateau = dep;
      out.butin = butinDuel(contenu, partie, t, alea);
      out.recompenses = verifierRecompenses(contenu, partie, t);
      if (out.butin) { if (out.butin.famille === "masques") out.recompenses.masque = out.butin.chose; else out.recompenses[out.butin.famille].push(out.butin.chose); }
    } else {
      f.defaites++; f.serie = 0;
      c.duelsPerdus = (c.duelsPerdus || 0) + 1;
      d.pret = false;
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
    var poids = libres.map(function (e) { return A.raretes[e.rarete].poids; }), total = poids.reduce(function (a, b) { return a + b; }, 0);
    var x = hacher(String(t) + "|" + n + "|" + partie.journal.length + "|" + attente.length) % total;
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
    return s && contenu.atomes ? { z: s.z, case: s.case, element: elementZ(contenu, s.z), attente: partie.sauvages.length } : null;
  }

  function texteMasse(e) { return e.stable ? e.masse.toFixed(1).replace(".", ",") : "[" + e.masse + "]"; }
  function sansAccents(x) { return x.normalize("NFD").replace(/[\u0300-\u036f]/g, ""); }
  function mots(x) {
    return sansAccents(x.toLowerCase()).split(/[^a-z]+/).filter(function (m) { return m.length >= 6; }).map(function (m) { return m.slice(0, 6); });
  }

  // Les trois questions du combat en cours, choix mélangés. Rien n'est enregistré : on peut les retirer.
  function tirerCombat(contenu, partie, alea) {
    var s = atomeSauvage(contenu, partie); if (!s) return null;
    alea = alea || Math.random;
    var A = contenu.atomes.elements, e = s.element, nom = e.nom.fr;
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
    var q1 = finir("symbole", "Quel est le symbole de l'atome « " + nom + " » ?", e.symbole, pS);
    // v15 : le numéro atomique (Victor ne voulait pas la masse). Leurres : des numéros voisins, à 1 à 6 près.
    var pZ = [];
    melanger([-6, -5, -4, -3, -2, -1, 1, 2, 3, 4, 5, 6], alea).forEach(function (d) {
      var z = e.z + d;
      if (pZ.length < 3 && z >= 1 && z <= A.length) pZ.push(String(z));
    });
    var q2 = finir("numero", "Quel est le numéro atomique de « " + nom + " » ?", String(e.z), pZ);
    // Où : un lieu de cet atome, et des lieux d'autres familles sans mot commun avec les siens.
    var siens = {}; e.ou.forEach(function (o) { mots(o.fr).forEach(function (m) { siens[m] = 1; }); });
    var bonne = e.ou[Math.floor(alea() * e.ou.length)].fr, pO = [];
    // Hydrogène, carbone, azote, oxygène sont partout dans le vivant : leurs leurres viennent des métaux lourds.
    var organique = [1, 6, 7, 8].indexOf(e.z) >= 0;
    melanger(A.filter(function (x) { return x.famille !== e.famille && Math.abs(x.z - e.z) > 4 && (!organique || (x.z > 20 && [25, 26, 27, 29, 30, 34, 42, 53].indexOf(x.z) < 0)); }), alea).forEach(function (x) {
      if (pO.length >= 3) return;
      var o = x.ou[Math.floor(alea() * x.ou.length)].fr;
      if (!mots(o).some(function (m) { return siens[m]; })) pO.push(o);
    });
    var q3 = finir("ou", "Où croise-t-on surtout cet atome ?", bonne, pO);
    return { z: e.z, element: e, questions: [q1, q2, q3] };
  }

  // `bonnes` : nombre de bonnes réponses. Renvoie {capture, element, bonnes, total, premiere, fiche, recompenses}.
  function terminerCombat(contenu, partie, bonnes, t) {
    var s = atomeSauvage(contenu, partie); if (!s) return null;
    var R = contenu.atomes.regles, c = partie.compteurs, f = ficheAtome(partie, s.z);
    partie.sauvages.shift();
    var capture = bonnes >= seuilAtome(contenu, partie, t), premiere = capture && !f.capture;
    if (capture) { if (!f.capture) { f.capture = t; c.atomesCaptures = (c.atomesCaptures || 0) + 1; } }
    else { f.fuites++; c.atomesEnfuis = (c.atomesEnfuis || 0) + 1; }
    var rec = verifierRecompenses(contenu, partie, t);
    partie.maj = t;
    return { capture: capture, element: s.element, bonnes: bonnes, total: R.questions, premiere: premiere, fiche: f, recompenses: rec,
      captures: Object.keys(partie.atomes).filter(function (z) { return partie.atomes[z].capture; }).length };
  }

  // --- Cadeaux à l'IA (v7) ---------------------------------------------------
  // Un cadeau par jour, une fois par objet. L'IA répond selon l'objet, garde parfois l'objet sur son masque,
  // et s'en sert sur le plateau : le pion avance ou recule, une case spéciale change de place, un ennemi arrive, ou rien.

  function cadeauPossible(contenu, partie, id, t) {
    var o = (contenu.objets || []).filter(function (x) { return x.id === id; })[0];
    if (!o || !o.cadeau || !partie.objets[id]) return { ok: false, raison: "inconnu" };
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
      for (var n = pl.position + 1; n < R.arrivee; n++) devant.push(n);
      devant.forEach(function (n) {
        var sp = specialDe(contenu, partie, n);
        if (sp && sp.type !== "retour_epoque" && sp.type !== "teleport" && sp.type !== "mendeleiev") speciales.push(n); else if (!sp && !ennemis[n]) libres.push(n);
      });
      if (speciales.length && libres.length) {
        var a = speciales[Math.floor(alea() * speciales.length)], b = libres[Math.floor(alea() * libres.length)];
        var spA = specialDe(contenu, partie, a);
        pl.speciaux[a] = null; pl.speciaux[b] = spA;
        effet.de = a; effet.vers = b; effet.regle = spA.type;
      } else effet.type = "rien";
    } else if (R && cd.effet === "ennemi") {
      var en = ennemisPlateau(contenu, partie), presents = Object.keys(en).map(function (k) { return en[k]; });
      var absents = contenu.ennemis.map(function (x) { return x.id; }).filter(function (x) { return presents.indexOf(x) < 0; });
      if (absents.indexOf(contenu.reserve) >= 0) absents = [contenu.reserve];
      var cases = [];
      for (var m = pl.position + 3; m <= Math.min(pl.position + 12, R.arrivee - 1); m++) if (!en[m] && !specialDe(contenu, partie, m)) cases.push(m);
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

  // --- Faveur de l'IA (v10) ----------------------------------------------------
  // Une jauge de 0 à 100, qui baisse chaque jour. Les cadeaux la font remonter selon leur éclat.
  // Le palier (comblée, contente, boudeuse, furieuse) change le butin, l'avancée et, furieuse, pose des pièges.
  function faveurIA(contenu, partie, t) {
    var F = contenu.ia && contenu.ia.faveur; if (!F) return null;
    if (!partie.faveur) partie.faveur = { valeur: F.depart, maj: t };
    var jours = Math.max(0, joursEntre(partie.faveur.maj, t));
    var valeur = Math.max(0, partie.faveur.valeur - F.baisse_par_jour * jours);
    var palier = F.paliers.filter(function (p) { return valeur >= p.min; })[0] || F.paliers[F.paliers.length - 1];
    return { valeur: valeur, palier: palier, demain: Math.max(0, valeur - F.baisse_par_jour), cadeauDuJour: partie.cadeaux.jour === cleJour(t) };
  }
  // Furieuse, l'IA pose chaque jour un piège sur une case libre juste devant le pion. Renvoie la case, ou null.
  function piegeIA(contenu, partie, t) {
    var fav = faveurIA(contenu, partie, t);
    if (!fav || fav.palier.id !== "furieuse" || !contenu.plateau || partie.colere === cleJour(t)) return null;
    var pl = partie.plateau, R = contenu.plateau.regles, en = ennemisPlateau(contenu, partie), libres = [];
    for (var n = pl.position + 1; n <= Math.min(pl.position + 5, R.arrivee - 1); n++) if (!specialDe(contenu, partie, n) && !en[n]) libres.push(n);
    partie.colere = cleJour(t);
    if (!libres.length) return null;
    var c = libres[hacher(cleJour(t) + "|" + pl.position) % libres.length], P = contenu.ia.faveur.piege;
    pl.speciaux[c] = { type: P.type, n: P.n, ia: true, raison: { fr: "Posé par l'IA, furieuse qu'on l'oublie. Un cadeau qui brille la calmerait." } };
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
      for (var c = pl.position + 2; c <= Math.min(pl.position + 8, R.arrivee - 1); c++) if (!en[c] && !specialDe(contenu, partie, c)) cases.push(c);
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
      case "eurekas": return c.eurekas >= cond.n;
      case "reculs": return c.reculs >= cond.n;
      default: return false;
    }
  }

  // v6 : objets, livres, accessoires et masques forment le butin. Les reliques des tours (sans `lot`) et le
  // premier masque restent donnés d'office ; le reste devient « gagnable » quand sa condition est remplie,
  // puis tombe au hasard après une épreuve réussie (voir tirerButin).
  var FAMILLES_BUTIN = ["objets", "livres", "accessoires", "masques"];
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
  function verifierRecompenses(contenu, partie, t) {
    var out = { succes: [], objets: [], accessoires: [], savants: [], evenements: [], livres: [], masque: null, gagnables: [] };
    partie.gagnables = partie.gagnables || {};
    partie.masques = partie.masques || {};
    // v8 : les cadeaux des cases, déjà rangés, rejoignent le résultat pour être montrés au joueur.
    (partie.cadeauxCase || []).forEach(function (c) {
      var x = listeFamille(contenu, c.famille).filter(function (y) { return y.id === c.id; })[0];
      if (!x) return;
      if (c.famille === "masques") out.masque = x; else out[c.famille].push(x);
    });
    partie.cadeauxCase = [];
    var directes = [
      ["succes", contenu.succes, partie.succes],
      ["savants", contenu.avatar && contenu.avatar.savants ? contenu.avatar.savants : [], partie.savants || (partie.savants = {})],
      ["evenements", contenu.evenements, partie.evenements],
    ];
    var change = true;
    while (change) {
      change = false;
      directes.forEach(function (f) {
        f[1].forEach(function (x) {
          if (!f[2][x.id] && conditionRemplie(contenu, partie, x.condition, t)) { f[2][x.id] = t; out[f[0]].push(x); change = true; }
        });
      });
      FAMILLES_BUTIN.forEach(function (f) {
        listeFamille(contenu, f).forEach(function (x) {
          if (possede(partie, f, x.id) || partie.gagnables[cleButin(f, x.id)]) return;
          if (x.condition && !conditionRemplie(contenu, partie, x.condition, t)) return;
          if (estButin(x)) { partie.gagnables[cleButin(f, x.id)] = { famille: f, id: x.id, depuis: t }; out.gagnables.push(x); return; }
          // Hors butin : reliques des tours, premier masque de l'IA.
          partie[f][x.id] = t; change = true;
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
  function butinOuvert(contenu, partie) {
    var tour = (partie.plateau ? partie.plateau.tours : 0) + 1, out = [], fin = finEpoqueCase(contenu, partie);
    FAMILLES_BUTIN.forEach(function (f) {
      listeFamille(contenu, f).forEach(function (x) {
        if (f === "livres" && fin != null && Number(x.annee) > fin) return;
        if (partie.gagnables && partie.gagnables[cleButin(f, x.id)] && !possede(partie, f, x.id) && x.lot <= tour) out.push({ famille: f, chose: x });
      });
    });
    return out;
  }
  function epoqueCase(contenu, partie) {
    var P = contenu.plateau, k = P && partie.plateau && P.cases[partie.plateau.position - 1];
    return k ? (P.epoques || []).filter(function (e) { return e.id === k.epoque; })[0] || null : null;
  }
  function finEpoqueCase(contenu, partie) { var e = epoqueCase(contenu, partie); return e ? e.fin : null; }
  // Si le sort tombe sur un livre, l'IA prend de préférence un livre de l'époque de la case, sinon le plus récent permis.
  function livreDeLaCase(contenu, partie, ouvert, alea) {
    var e = epoqueCase(contenu, partie), livres = ouvert.filter(function (b) { return b.famille === "livres"; });
    if (!e || !livres.length) return null;
    var ici = livres.filter(function (b) { var a = Number(b.chose.annee); return (e.debut == null || a >= e.debut) && (e.fin == null || a <= e.fin); });
    if (ici.length) return ici[Math.floor(alea() * ici.length)];
    return livres.slice().sort(function (a, b) { return Number(b.chose.annee) - Number(a.chose.annee); })[0];
  }
  // v8 : case cadeau. Un objet du cabinet tombe sans épreuve ; à défaut, n'importe quel autre butin ouvert.
  function tirerCadeau(contenu, partie, t) {
    var ouvert = butinOuvert(contenu, partie), objets = ouvert.filter(function (b) { return b.famille === "objets"; });
    var liste = objets.length ? objets : ouvert;
    if (!liste.length) return null;
    var b = liste[hacher(String(t) + "|" + partie.plateau.position + "|" + partie.journal.length) % liste.length];
    partie[b.famille][b.chose.id] = t;
    delete partie.gagnables[cleButin(b.famille, b.chose.id)];
    if (b.famille === "masques") partie.masque = b.chose.id;
    return b;
  }
  // Après une épreuve réussie : au plus un butin, tiré au hasard. `alea` (facultatif) pour les tests.
  function tirerButin(contenu, partie, epreuve, t, alea) {
    alea = alea || Math.random;
    var ouvert = butinOuvert(contenu, partie);
    var fav = epreuve.type === "duel" ? null : faveurIA(contenu, partie, t);
    var assure = partie.butinAssure && epreuve.type !== "duel" && ouvert.length;
    if (assure) partie.butinAssure = false;
    var mult = epreuve.type === "duel" ? 1 : reglesDuJour(contenu, partie, t).butin;
    if (!assure && (!ouvert.length || alea() >= chanceButin(contenu, epreuve) * (fav ? fav.palier.butin : 1) * mult)) return null;
    var b = ouvert[Math.floor(alea() * ouvert.length)];
    if (b.famille === "livres") b = livreDeLaCase(contenu, partie, ouvert, alea) || b;
    partie[b.famille][b.chose.id] = t;
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
      return { texte: m.fr.replace("{succes}", sc.nom.fr), ton: "impressionnee", succes: sc };
    }
    var ton = humeur(partie), l = S[ton] || S.neutre;
    return { texte: l[h % l.length].fr, ton: ton };
  }

  // --- Bouton « Jouer » : l'IA choisit l'épreuve ------------------------------
  // Un rappel dû passe d'abord (le plus en retard). Sinon, parmi les quiz ouverts, l'IA tire une raison :
  // la stat la plus faible ou le hasard. Le choix reste le même tant qu'on n'a pas joué.
  function choixIA(contenu, partie, t) {
    var rv = revisionEnCours(partie);
    if (rv) return { comp: contenu.parId[rv.comp], type: "rappel", raison: "revision" };
    var dus = rappelsDus(contenu, partie, t);
    var dispo = disponibles(contenu, partie, t);
    var graine = hacher(cleJour(t) + "|" + partie.journal.length + "|" + (partie.cree || 0));
    // v15 : la case où se tient le pion dicte l'arbre. Les rappels dus passent toujours d'abord (ceux de cet arbre
    // en tête, l'oubli n'attend pas), puis un quiz de cet arbre ; sinon l'ancien choix, annoncé comme hors case.
    var k = contenu.plateau && partie.plateau && contenu.plateau.cases[partie.plateau.position - 1];
    var st = k && k.stat;
    if (dus.length) {
      var dusIci = dus.filter(function (c) { return c.stat === st; });
      return { comp: (dusIci[0] || dus[0]), type: "rappel", raison: "rappel", stat: dusIci.length ? st : null, kase: k || null };
    }
    var porte = st && porteArbre(contenu, partie, st);
    if (porte) return { comp: porte, type: "quiz", raison: "ouvre_arbre", stat: st, kase: k };
    if (!dispo.length) return null;
    if (st) {
      var ici = dispo.filter(function (c) { return c.stat === st; });
      if (ici.length) return { comp: ici[graine % ici.length], type: "quiz", raison: "case", stat: st, kase: k };
    }
    if (st) return { comp: dispo[graine % dispo.length], type: "quiz", raison: "hors_case", stat: st, kase: k };
    var raisons = [];
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
    else {
      // v10 : hors des jours ordinaires, l'IA parle de ce qu'elle ressent pour vous.
      var fav = faveurIA(contenu, partie, t);
      if (fav && fav.palier.id !== "contente" && contenu.commentairesPar["faveur_" + fav.palier.id]) ctx = "faveur_" + fav.palier.id;
    }
    // v12 : des questions ratées aujourd'hui et pas encore effacées : l'IA vous envoie au mur de la honte.
    if (ctx !== "retour" && contenu.commentairesPar.mur_honte && murDeLaHonte(contenu, partie, t, 0).restantes) ctx = "mur_honte";
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
    choixIA: choixIA, humeur: humeur, revisionEnCours: revisionEnCours, compARevisier: compARevisier, arbreOuvert: arbreOuvert, specialDe: specialDe, ennemisPlateau: ennemisPlateau, tirerDuel: tirerDuel, terminerDuel: terminerDuel,
    faveurIA: faveurIA, piegeIA: piegeIA, masquesDuJour: masquesDuJour, reglesDuJour: reglesDuJour, questionsQuiz: questionsQuiz, seuilAtome: seuilAtome,
    atomeSauvage: atomeSauvage, tirerCombat: tirerCombat, terminerCombat: terminerCombat, estCapture: estCapture, texteMasse: texteMasse,
    ficheBestiaire: ficheBestiaire, cadeauPossible: cadeauPossible, donnerObjet: donnerObjet, pionnierDe: pionnierDe, surnom: surnom, tirerButin: tirerButin, butinOuvert: butinOuvert, chanceButin: chanceButin, savantActuel: savantActuel, tenterFarce: tenterFarce, farceActive: farceActive, rendreVisage: rendreVisage,
    expression: expression,
    bonusDuJour: bonusDuJour,
    valeurEpreuve: valeurEpreuve,
    deplacer: deplacer,
    avancerPion: avancerPion,
    cleJour: cleJour,
    jouerPlateau: jouerPlateau,
    murDeLaHonte: murDeLaHonte,
    retenterOubli: retenterOubli,
  };

  if (typeof module === "object" && module.exports) module.exports = Moteur;
  else racine.Moteur = Moteur;
})(typeof globalThis !== "undefined" ? globalThis : this);
