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
      credits: { solde: 0, gagnes: 0, parSucces: {}, record: 0, jour: null, pots: 0 },
      ultimatum: null,
      objetIA: null,
      inventaire: {},
      tresorIA: {},
      emplettes: [],
      atomes: {},
      sauvages: [],
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
  function terminerQuiz(contenu, partie, id, resultats, t, infos) {
    var r = contenu.regles, c = partie.compteurs, k = contenu.parId[id];
    ouvrirLot(partie, t, k && k.stat);
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
    if (jouer) consommerArbre(partie, k.stat);
    var avant = verifierRecompenses(contenu, partie, t);
    if (reussi) ajouterButin(contenu, partie, avant, { type: "quiz", comp: id }, t, infos && infos.alea);
    var dep = jouerPlateau(contenu, partie, { type: "quiz", comp: id }, { reussi: reussi, parfait: parfait, chrono: chrono, jouer: jouer, uneCase: !!(infos && infos.uneCase) }, t);
    var ag = agacerIA(contenu, partie, resultats.length - bonnes, !reussi, t);
    lotExceptionnel(partie, dep);
    var apres = verifierRecompenses(contenu, partie, t), rec = fusionRec(avant, apres);
    if (rec.masque) contextes.splice(contextes.length - 1, 0, "masque");
    var fa = reussi ? null : tenterFarce(contenu, partie, t, infos && infos.alea, k.stat);
    return { issue: reussi ? "maitrisee" : "echec", bonnes: bonnes, total: total, xp: xp, prochainRappel: e.prochainRappel,
      nouveauxSucces: rec.succes, nouveauxObjets: rec.objets, nouveauxAccessoires: rec.accessoires, nouveauxSavants: rec.savants,
      nouveauxEvenements: rec.evenements, nouveauxLivres: rec.livres, masque: rec.masque, plateau: dep, contextes: contextes, farce: fa, jouer: jouer, agacement: ag, credits: rec.credits,
      avantPlateau: avant, apresPlateau: apres, theme: contenu.parId[id] ? contenu.parId[id].stat : null };
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
    ouvrirLot(partie, t, contenu.parId[id] && contenu.parId[id].stat);
    var bonnes = resultats.filter(function (x) { return x.correct; }).length;
    var total = Math.max(resultats.length, (infos && infos.total) || 0);
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
    noter(partie, t, { type: "rappel", comp: id, bonnes: bonnes, total: total, xp: reussi ? xp : -xpPerdue, source: revision ? "revision" : "rappel" });
    epinglerOublis(partie, id, resultats, t, revision ? "revision" : "rappel");
    partie.maj = t;
    var contextes = [];
    if (revision) contextes.push(reussi ? "revision_reussie" : "revision_ratee");
    else if (!reussi) contextes.push("rappel_perdu");
    if (nuit) contextes.push("nuit");
    if (!revision && reussi && retard >= 3) contextes.push("rappel_retard");
    if (!revision && reussi) contextes.push("rappel_reussi");
    var jouer = !!(infos && infos.jouer);
    if (jouer && contenu.parId[id]) consommerArbre(partie, contenu.parId[id].stat);
    var avant = verifierRecompenses(contenu, partie, t);
    if (reussi) ajouterButin(contenu, partie, avant, { type: "rappel", comp: id }, t, infos && infos.alea);
    var dep = revision && !reussi ? null : jouerPlateau(contenu, partie, { type: "rappel", comp: id }, { reussi: reussi, parfait: false, chrono: false, jouer: jouer, uneCase: !!(infos && infos.uneCase) }, t);
    var ag = agacerIA(contenu, partie, resultats.length - bonnes, !reussi, t);
    lotExceptionnel(partie, dep);
    var apres = verifierRecompenses(contenu, partie, t), rec = fusionRec(avant, apres);
    if (rec.masque) contextes.splice(contextes.length - 1, 0, "masque");
    var fa = reussi || revision ? null : tenterFarce(contenu, partie, t, infos && infos.alea, contenu.parId[id] && contenu.parId[id].stat);
    return { revision: revision, issue: reussi ? "reussi" : revision ? "revision_ratee" : "perdue", bonnes: bonnes, total: total, xp: xp, xpPerdue: xpPerdue, prochainRappel: e.prochainRappel,
      retard: retard, nouveauxSucces: rec.succes, nouveauxObjets: rec.objets, nouveauxAccessoires: rec.accessoires, nouveauxSavants: rec.savants,
      nouveauxEvenements: rec.evenements, nouveauxLivres: rec.livres, masque: rec.masque, plateau: dep, contextes: contextes, farce: fa, jouer: jouer, agacement: ag, credits: rec.credits,
      avantPlateau: avant, apresPlateau: apres, theme: contenu.parId[id] ? contenu.parId[id].stat : null };
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
    return caseN(contenu, n).special || chronoDeBase(contenu, n);
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
    if (!tour || !contenu.plateau) return Object.assign({}, base);
    var R = contenu.plateau.regles, graine = (partie.cree || 0) + "|" + tour;
    var postes = Object.keys(base).map(Number).sort(function (a, b) { return a - b; });
    // v21 : le parcours fixe le nombre d'ennemis ; leurs postes se répartissent le long de sa route.
    var pc = pl.parcours, surRoute = null;
    if (pc && pc.cases) {
      surRoute = {}; pc.cases.forEach(function (n) { surRoute[n] = 1; });
      postes = [];
      for (var q = 0; q < pc.ennemis; q++) postes.push(pc.cases[Math.round((q + 1) * (pc.cases.length - 1) / (pc.ennemis + 1))]);
    }
    var bete = partie.bestiaire || {};
    var choisis = contenu.ennemis.filter(function (e) { return e.id !== contenu.reserve; }).map(function (e) {
      var f = bete[e.id], vu = f && (f.victoires || f.defaites);
      return { id: e.id, score: (vu ? 0 : 1000) + (f ? f.defaites * 60 : 0) + hacher(graine + "|" + e.id) % 400 };
    }).sort(function (a, b) { return b.score - a.score; }).slice(0, postes.length).map(function (x) { return x.id; });
    choisis.sort(function (a, b) { return hacher(graine + "|ordre|" + a) - hacher(graine + "|ordre|" + b); });
    var decalage = (tour * 3) % 9 - 4, out = {};
    var libre = function (c) { return c > R.depart + 1 && c < R.arrivee && !out[c] && !specialDe(contenu, partie, c) && (!surRoute || surRoute[c]); };
    var parId = {}; contenu.ennemis.forEach(function (e) { parId[e.id] = e; });
    postes.forEach(function (n, i) {
      // v18 : l'ennemi se poste sur une case de son thème, la plus proche de son poste ; sinon, près du poste.
      var th = themeDe(parId[choisis[i]]), ici = th ? contenu.plateau.cases.filter(function (k) { return k.stat === th && libre(k.n); }) : [];
      if (ici.length) {
        ici.sort(function (a, b) { return Math.abs(a.n - n - decalage) - Math.abs(b.n - n - decalage) || a.n - b.n; });
        out[ici[0].n] = choisis[i]; return;
      }
      var visee = n + decalage;
      for (var d = 0; d < 8; d++) {
        var c = visee + (d % 2 ? -1 : 1) * Math.ceil(d / 2);
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
  function jouerPlateau(contenu, partie, epreuve, issue, t) {
    if (!contenu.plateau) return null;
    var v = valeurEpreuve(contenu, partie, epreuve, t), pl = partie.plateau, c = partie.compteurs;
    // v15 : « avancer d'une seule case » : un pas, sans bonus, pour s'arrêter sur la case suivante et la dévoiler.
    var unPas = issue.reussi && issue.uneCase;
    // v19 : le bonus du bouton Jouer est tiré au hasard, entre bonus.jouer et bonus.jouer_max (0 à 4).
    // v20 : furieuse, l'IA ralentit le jeu : le tirage reste au minimum.
    var bj = bornesBonusJouer(contenu, partie, t), bMin = bj.min, bMax = bj.max;
    var bonusJouer = issue.reussi && issue.jouer && !unPas ? bMin + tirage("jouer|" + t + "|" + partie.journal.length, bMax - bMin + 1) : 0;
    var valeur = unPas ? 1 : issue.reussi ? v.total + (issue.parfait ? v.parfait : 0) + (issue.chrono ? v.chrono : 0) + bonusJouer : v.echec;
    var etapes = [];
    // v11 : l'objet tenu par l'avatar donne parfois un coup de pouce après une épreuve réussie.
    var tenu = issue.reussi && !unPas && partie.avatar && partie.avatar.main && (contenu.objets || []).filter(function (o) { return o.id === partie.avatar.main; })[0];
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
    pl.coups = (pl.coups || 0) + 1;
    var dep = deplacer(contenu, partie, valeur, t, epreuve.type);
    dep.etapes = etapes.concat(dep.etapes);
    dep.contextes = contextesPlateau(dep);
    dep.valeurs = v;
    dep.bonusJouer = bonusJouer; dep.jouer = !!(issue.reussi && issue.jouer && !unPas);
    dep.uneCase = !!unPas;
    var retouche = remanierRoute(contenu, partie, issue, t, issue.alea);
    if (retouche) { dep.etapes.push(retouche); dep.contextes = contextesPlateau(dep); }
    return dep;
  }

  // v15 : la case où l'IA (ou un ennemi) renvoie le pion : la plus ancienne, parmi les OUBLI_FENETRE cases derrière lui,
  // où il ne s'est jamais arrêté ; si tout y est dévoilé, la plus ancienne où il ne s'est pas arrêté dans ce tour.
  var OUBLI_FENETRE = 15;
  // `avant` et le résultat sont des places sur la route du tour.
  function caseOubliee(contenu, partie, avant) {
    var pl = partie.plateau, rt = route(contenu, partie), d = Math.max(1, avant - OUBLI_FENETRE);
    for (var j = d; j < avant; j++) if (!pl.visites[rt[j]]) return j;
    for (j = d; j < avant; j++) if (!(pl.arrets && pl.arrets[rt[j]])) return j;
    return null;
  }
  // v15 : la route du tour, de la case départ à l'arrivée. Sans retouche de l'IA, toutes les cases dans l'ordre.
  function route(contenu, partie) {
    var pl = partie.plateau, R = contenu.plateau.regles;
    if (!pl.route) {
      if (pl.parcours && pl.parcours.cases) pl.route = pl.parcours.cases.slice();
      else { pl.route = []; for (var n = R.depart; n <= R.arrivee; n++) pl.route.push(n); }
    }
    if (pl.idx == null || pl.route[pl.idx] !== pl.position) {
      pl.idx = pl.route.indexOf(pl.position);
      if (pl.idx < 0) { pl.idx = 0; pl.position = pl.route[0]; }
    }
    return pl.route;
  }
  // Place, derrière `ici`, où renvoie une téléportation vers la case `vers` (à défaut, la dernière case plus ancienne).
  function placeVers(rt, ici, vers) {
    for (var j = ici - 1; j >= 0; j--) if (rt[j] === vers) return j;
    for (j = ici - 1; j >= 0; j--) if (rt[j] <= vers) return j;
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
    var forme = formes[tirage(g + "|forme", formes.length)];
    var longueur = H.cases[0] + tirage(g + "|long", H.cases[1] - H.cases[0] + 1);
    var base = function (n) { return contenu.plateau.cases[n - 1].special || chronoDeBase(contenu, n); };
    var ordinaires = [];
    for (var n = R.depart + 1; n < R.arrivee; n++) if (!base(n)) ordinaires.push(n);
    var melange = function (l, cle) { return l.slice().sort(function (a, b) { return hacher(g + cle + a) - hacher(g + cle + b); }); };
    var retirees = {}; melange(ordinaires, "|retire|").slice(0, Math.max(0, R.arrivee - R.depart + 1 - longueur)).forEach(function (x) { retirees[x] = 1; });
    var cases = []; for (n = R.depart; n <= R.arrivee; n++) if (!retirees[n]) cases.push(n);
    // Les cases spéciales : on en retire, ou on en ajoute sur des cases ordinaires de la route (pas les trois premières).
    var speciaux = {}, libres = melange(cases.filter(function (x) { return x > R.depart + 3 && x < R.arrivee && !base(x); }), "|libre|");
    function ajuster(types, ecart, nouvelle) {
      var la = cases.filter(function (x) { var b = base(x); return b && types.indexOf(b.type) >= 0; });
      if (ecart < 0) melange(la, "|ote|" + types[0]).slice(0, -ecart).forEach(function (x) { speciaux[x] = null; });
      for (var k = 0; k < ecart && libres.length; k++) speciaux[libres.shift()] = nouvelle(k);
      return la.length + ecart;
    }
    var nAtomes = ajuster(["mendeleiev"], H.atomes - cases.filter(function (x) { return base(x) && base(x).type === "mendeleiev"; }).length, function () { return { type: "mendeleiev" }; });
    var nPieges = ajuster(TYPES_PIEGES, H.pieges, function (k) { return { type: "recul", n: 2 + k % 3, raison: { fr: "Piège ajouté par l'IA en dessinant ce parcours." } }; });
    var nCadeaux = ajuster(["cadeau"], H.cadeaux, function () { return { type: "cadeau", raison: { fr: "Case cadeau ajoutée par l'IA, de bonne humeur ce jour-là." } }; });
    // v34 : des cases Chrono, selon l'humeur (outils/parcours.py).
    var nChrono = H.chrono == null ? 0 : ajuster(["chrono"], H.chrono - cases.filter(function (x) { return base(x) && base(x).type === "chrono"; }).length, function () { return { type: "chrono" }; });
    var tours = pl.tours + 1, ennemis = Math.min(PC.ennemis_max || 12, contenu.ennemis.length - 1, H.ennemis + Math.max(0, Math.floor((tours - 2) / 2)) * (PC.ennemis_par_deux_tours || 0));
    var mots = PC.mots[palier] || [];
    return { tour: tours, forme: forme.id, palier: palier, cases: cases, longueur: cases.length, ennemis: ennemis,
      atomes: Math.max(0, nAtomes), pieges: Math.max(0, nPieges), cadeaux: Math.max(0, nCadeaux), chrono: Math.max(0, nChrono), speciaux: speciaux,
      mot: mots.length ? mots[tirage(g + "|mot", mots.length)] : null, dessine: t };
  }
  function appliquerParcours(contenu, partie) {
    var pl = partie.plateau, p = pl.parcoursSuivant; if (!p) return null;
    pl.parcours = p; pl.parcoursSuivant = null;
    pl.route = null; pl.speciaux = Object.assign({}, p.speciaux); pl.ennemis = null;
    pl.idx = 0; pl.position = contenu.plateau.regles.depart;
    route(contenu, partie);
    return p;
  }
  // Le choix de fin de tour : « tour » (refaire un tour sur le nouveau parcours) ou « donjon » (pas encore ouvert).
  function choisirSuite(contenu, partie, choix, t) {
    if (choix === "donjon") return { ok: false, raison: "bientot" };
    var p = appliquerParcours(contenu, partie);
    if (!p) return { ok: false, raison: "aucun" };
    partie.maj = t;
    return { ok: true, parcours: p };
  }
  function formeParcours(contenu, id) { return contenu.plateau && contenu.plateau.parcours ? contenu.plateau.parcours.formes.filter(function (f) { return f.id === id; })[0] || null : null; }
  function caseDecouverte(partie, n) { return !!(partie.plateau.visites[n] || partie.plateau.position === n); }

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

  // v20 : les cases qu'un désarmement acheté rend inoffensives.
  var PIEGES = { recul: 1, retour_epoque: 1, teleport: 1, oubli: 1, revision: 1, quarantaine: 1, prison: 1 };
  // Déplace le pion de `valeur` cases (négatif : recul simple, sans effet de case).
  // Mode test : on peut l'appeler directement pour parcourir le plateau.
  function deplacer(contenu, partie, valeur, t, cause) {
    var pl = partie.plateau, R = contenu.plateau.regles, c = partie.compteurs;
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
        poser(placeVers(pl.route, pl.idx, sp.vers));
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
        etapes.push(fin);
        if (record) mf[forme] = coups;
        if (coups > 0 && (pl.meilleur == null || coups < pl.meilleur)) pl.meilleur = coups;
        pl.coups = 0; pl.arrets = {};
        pl.arrets[R.depart] = 1;
        pl.tours++;
        pl.atteinte = R.arrivee;
        pl.ennemis = null; pl.speciaux = Object.assign({}, pl.parcours && pl.parcours.speciaux); ennemis = rj.ennemis === "absents" ? {} : ennemisPlateau(contenu, partie);
        pl.route = null; der = route(contenu, partie).length - 1;
        pl.idx = 0; pl.position = R.depart;
        chemin.push(R.depart); places.push(1);
        if (contenu.plateau.parcours) pl.parcoursSuivant = dessinerParcours(contenu, partie, t);
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
        while (avancer(pas) && garde++ < MAX_ENCHAINEMENT) {
          var sp = specialDe(contenu, partie, pl.position);
          if (!sp) break;
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
          } else if (sp.type === "chrono" && contenu.plateau.regles.chrono) {
            // v34 (Victor) : case Chrono. Le pion s'arrête ; la partie de Chrono sert d'épreuve de la case.
            if (chronoPossible(contenu, partie)) { etatChrono(partie).case = pl.position; etapes.push({ type: "chrono", case: pl.position }); }
            else etapes.push({ type: "chrono_vide", case: pl.position });
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
        if (partie.gagnables && partie.gagnables[cleButin(f, x.id)] && !possede(partie, f, x.id) && x.lot <= tour) proches.push({ famille: f, chose: x });
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
    ouvrirLot(partie, t, contenu.ennemiParId[d.ennemi] && contenu.ennemiParId[d.ennemi].theme);
    var e = contenu.ennemiParId[d.ennemi], f = ficheBestiaire(partie, d.ennemi), c = partie.compteurs;
    var bonnes = resultats.filter(function (x) { return x.correct; }).length, gagne = resultats.length > 0 && bonnes === resultats.length;
    f.dernier = t;
    var out = { gagne: gagne, ennemi: e, bonnes: bonnes, total: Math.max(resultats.length, total || 0), plateau: null, recompenses: null, butin: null, premiere: false, fiche: f };
    out.agacement = agacerIA(contenu, partie, resultats.length - bonnes, !gagne, t, "duel_gagne");
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
      var cr = partie.credits, vol = Math.min(cr.solde, Math.max(VOL_DUEL.min, Math.min(VOL_DUEL.max, Math.round(cr.solde * VOL_DUEL.part))));
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
    var pl = partie.plateau, prog = pl ? (pl.tours || 0) + (pl.atteinte || 1) / 63 : 2, echelle = 6 + 45 * prog;
    var poids = libres.map(function (e) { return A.raretes[e.rarete].poids * Math.exp(-(e.z - 1) / echelle) * 1000; }), total = poids.reduce(function (a, b) { return a + b; }, 0);
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
    var A = atomes.elements, nom = e.nom.fr;
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
    // v15 : le numéro atomique (Victor ne voulait pas la masse). v34 (Victor) : leurres éloignés d'au moins 12,
    // pour deviner avec la logique léger/lourd plutôt que de tout savoir par cœur.
    var pZ = [], pris = [e.z];
    melanger(A.map(function (x) { return x.z; }), alea).forEach(function (z) {
      if (pZ.length < 3 && pris.every(function (y) { return Math.abs(y - z) >= 12; })) { pZ.push(String(z)); pris.push(z); }
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
    // v34 (Victor) : le placer sur le tableau, en touchant sa case. `reponse` : le numéro de la case juste.
    var qP = { type: "place", enonce: "Où va « " + nom + " » dans le tableau ? Touche sa case.", choix: [], reponse: e.z };
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
    var av = atomes.elements[e.z - 2], ap = atomes.elements[e.z], nom = function (x) { return x.nom.fr.toLowerCase() + " (" + x.z + ")"; };
    var voisins = av && ap ? "entre " + nom(av) + " et " + nom(ap) : av ? "juste après " + nom(av) + ", tout au bout du tableau" : "le tout premier, avant " + nom(ap);
    return { texte: e.nom.fr + ", n° " + e.z + " : " + voisins + ".", voisins: [av, ap].filter(Boolean).map(function (x) { return x.z; }), illustration: schemaNumero(atomes, e, av, ap) };
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
    out.push('<text class="t" x="' + X0 + '" y="' + y + '" font-size="13" font-weight="700">' + e.nom.fr + " (" + e.symbole + ") = " + e.z + "</text>");
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ' + (X0 + 18 * T + 4) + " " + (y + 8) + '" role="img" aria-label="Tableau périodique : ' + e.nom.fr + ", numéro " + e.z + '">' + out.join("") + "</svg>";
  }
  // v34 (Victor) : l'atome dessiné couche par couche. Le nombre de couches donne la ligne ; les électrons de la couche
  // extérieure (plus ceux « en trop » de l'avant-dernière, au milieu du tableau) donnent la colonne.
  var COULEURS_COUCHES = ["#D99A0B", "#2E9E5B", "#2B7BBF", "#8A57C9", "#D9534F", "#17998A", "#A4791A"];
  function lectureCouches(atomes, e) {
    var K = atomes.couches; if (!K) return null;
    var c = K.par_z[e.z - 1].slice(), n = c.length, ext = c[n - 1], av = n > 1 ? c[n - 2] : 0, out = { couches: c, predite: e.z >= K.predites_des, lignes: [] };
    var nom = e.nom.fr, pl = function (k, mot) { return k + " " + mot + (k > 1 ? "s" : ""); };
    if (e.z === 46) {
      out.ligne = 5; out.colonne = 10; out.cas = "palladium";
      out.lignes.push("4 couches remplies, et une 5e restée vide : le palladium a gardé tous ses électrons en dessous. Il est quand même sur la ligne 5.");
      out.lignes.push("Sa 4e couche est pleine à 18 : 0 dehors + 10 = colonne 10.");
      return out;
    }
    out.ligne = n;
    out.lignes.push(pl(n, "couche") + " → ligne " + n + ".");
    if (!e.groupe) {
      out.cas = "terre_rare";
      var serie = e.z >= 89 ? "actinides" : "lanthanides";
      out.lignes.push("Sa " + (n - 2) + "e couche se remplit (" + c[n - 3] + " électrons) pendant que les deux dernières bougent à peine : c'est un des " + serie + ", rangés dans la ligne du bas.");
      return out;
    }
    if (e.z === 2) { out.cas = "helium"; out.colonne = 18; out.lignes.push("2 électrons : sa seule couche est déjà pleine. Couche extérieure pleine = gaz noble, colonne 18."); return out; }
    if (n <= 2 || av === 8 && ext <= 2 || av === 2 || av === 8 && n === 3) {
      out.cas = "principal"; out.colonne = ext <= 2 ? ext : ext + 10;
      out.lignes.push(ext <= 2 ? pl(ext, "électron") + " sur la couche extérieure → colonne " + ext + "." : pl(ext, "électron") + " sur la couche extérieure → colonne " + ext + " + 10 = " + (ext + 10) + " (on saute les 10 colonnes du milieu).");
    } else if (av === 18 || av === 32) {
      out.colonne = ext + 10; out.cas = ext <= 2 ? "fin_transition" : "principal";
      out.lignes.push(pl(ext, "électron") + " sur la couche extérieure, et la couche d'en dessous pleine à " + av + " → colonne " + ext + " + 10 = " + (ext + 10) + ".");
    } else {
      var trop = av - 8; out.cas = "transition"; out.colonne = ext + trop;
      out.lignes.push(pl(ext, "électron") + " dehors, plus " + trop + " en trop sur la couche d'en dessous (" + av + " au lieu de 8) → colonne " + ext + " + " + trop + " = " + out.colonne + ".");
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
    out.push('<text class="tm" x="' + lx + '" y="20" font-size="11">couche · électrons</text>');
    for (i = 0; i < n; i++) {
      var y = 40 + i * 24;
      out.push('<circle cx="' + (lx + 7) + '" cy="' + (y - 4) + '" r="7" fill="' + COULEURS_COUCHES[i] + '"/><text class="t" x="' + (lx + 20) + '" y="' + y + '" font-size="14" font-weight="' + (i === n - 1 ? 700 : 400) + '">' + (i + 1) + " · " + c[i] + (i === n - 1 ? " ← dehors" : "") + "</text>");
    }
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 380 250" role="img" aria-label="' + e.nom.fr + " : " + c.join(", ") + ' électrons par couche">' + out.join("") + "</svg>";
  }

  // Les questions d'un atome sur le mur : mêmes questions qu'au combat, leurres figés ; le numéro s'y écrit au clavier.
  function questionsMur(atomes, e) {
    var k = 0, graine = "mur-atome|" + e.z, alea = function () { return (hacher(graine + "|" + (k++)) % 100000) / 100000; };
    var qs = questionsCombat(atomes, e, alea), ast = astuceNumero(atomes, e);
    var lieux = e.ou.map(function (o) { return o.fr; }).join(", ");
    return qs.map(function (q) {
      var base = { id: "atome." + e.z + "." + q.type, competence: "sci.atomes", atome: e.z, enonce: { fr: q.enonce } };
      var lc = lectureCouches(atomes, e);
      if (q.type === "numero") return Object.assign(base, { type: "numerique", reponse: e.z, tolerance: 0, explication: { fr: ast.texte + (lc ? " " + lc.lignes.join(" ") : "") }, illustration_explication: (lc ? dessinCouches(atomes, e) : "") + ast.illustration });
      if (q.type === "place") return Object.assign(base, { type: "place", reponse: e.z, explication: { fr: (lc ? lc.lignes.join(" ") + " " : "") + ast.texte }, illustration_explication: (lc ? dessinCouches(atomes, e) : "") + ast.illustration });
      return Object.assign(base, { type: "qcm", choix: q.choix.map(function (c) { return { fr: c }; }), reponse: q.reponse,
        explication: { fr: q.type === "symbole" ? "Le symbole de « " + e.nom.fr + " » est " + e.symbole + ", numéro " + e.z + "." : "On le croise surtout dans " + lieux + ". " + e.anecdote.fr } });
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
      if (q && q.type === "qcm" && rep !== null) { var ix = q.choix.map(function (c) { return c.fr; }).indexOf(rep); if (ix >= 0) rep = ix; }
      return { id: id, correct: false, rep: rep };
    }).filter(function (x) { return contenu.questionParId[x.id]; }), t, "atome");
    ouvrirLot(partie, t, "alchimie");
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
    return { avantPlateau: avant, apresPlateau: apres, plateau: dep, capture: capture, element: s.element, bonnes: bonnes, total: R.questions, premiere: premiere, fiche: f, recompenses: rec, agacement: ag, indice: !!indice,
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
  function enRayon(contenu, partie, article, t) {
    var f = FAMILLE_ARTICLE[article];
    if (f) return listeFamille(contenu, f).filter(function (x) { return (estButin(x) || f === "masques") && !possede(partie, f, x.id); });
    // v34 (Victor) : le kit du chasseur, un équipement acheté une fois pour toutes.
    if (article === "kit") return contenu.atomes && !partie.kit ? [1] : [];
    if (!contenu.plateau || !contenu.placement) return [];
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
    var B = boutique(contenu); if (!B || B.prix[article] == null) return { ok: false, raison: "inconnu" };
    var prix = B.prix[article], cr = partie.credits;
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
    var mots = (B.mots && B.mots[article]) || [];
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
    var choix = Object.keys(E.poids).filter(function (a) { return B.prix[ARTICLE_EMPLETTE[a]] <= cr.ia && rayonIA(contenu, partie, a).length; });
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
      e.type = article; e.prix = B.prix[ARTICLE_EMPLETTE[article]];
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
    if (g === "honte" && r < K.honte.chance) { humeur = "honte"; facteur = K.honte.facteur; mots = K.honte.mots; }
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
      mot = { fr: v.fr + " " + pique.fr };
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
    if (!contenu.ia || !contenu.ia.credits) return { ok: false, raison: "inconnu" };
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
      if (issue !== "egal" && contenu.plateau) {
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
    if (!U || partie.ultimatum || cr.solde < U.solde_min || niveauGlobal(contenu, partie) < 1) return null;
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
    var choix = neuves.length ? neuves : dans.length ? dans : contenu.questions;
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
    var k = contenu.plateau.cases[p.case - 1], CC = contenu.plateau.competences_cases, evoque = (CC && CC[String(p.case)]) || [];
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
    return { dejoue: false, case: p.case, regle: p.regle.type, plateau: dep, replique: replique(contenu, partie, ["piege_declenche"]), recompenses: verifierRecompenses(contenu, partie, t) };
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
  function texteSiecle(k) { return k >= 0 ? chiffreRomain(k + 1) + (k === 0 ? "er" : "e") + " siècle" : chiffreRomain(-k) + "e siècle av. J.-C."; }
  // Le libellé d'un créneau : « XVIIe siècle », « 2de moitié du XVIIe siècle », « 1680-1689 », « 585 av. J.-C. ».
  function texteCreneau(k, pas, prehistoire) {
    if (prehistoire != null && k < creneau(prehistoire, pas, null)) return "Préhistoire (avant " + (-prehistoire) + " av. J.-C.)";
    if (pas === 100) return texteSiecle(k);
    if (pas === 50) { var c = Math.floor(k / 2); return (k - 2 * c ? "2de" : "1re") + " moitié du " + texteSiecle(c); }
    if (pas === 1) { var y = anneeDuCreneau(k, 1); return y > 0 ? String(y) : (-y) + " av. J.-C."; }
    var a = anneeDuCreneau(k, pas), b = k >= 0 ? k * pas + pas - 1 : k * pas + pas - 1;
    return a > 0 ? a + "-" + b : (-a) + " à " + (-b) + " av. J.-C.";
  }
  // Une phrase qui donnerait la date (un nombre de trois ou quatre chiffres) n'est pas montrée.
  function sansDate(o) { var x = o && o.fr; return x && !/\d{3,4}/.test(x) ? x : null; }
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
    var out = [], pre = R.prehistoire, maxN = R.niveaux.length;
    function ajouter(x) { if (x.debut < pre) x.max = 1; out.push(x); }
    (contenu.evenements || []).forEach(function (e) {
      if (partie.evenements && partie.evenements[e.id] != null && e.annee != null)
        ajouter({ cle: "frise:" + e.id, sorte: "frise", id: e.id, titre: e.titre.fr, texte: sansDate(e.phrase), debut: e.annee, fin: e.annee, max: maxN, source: e.source, case: e.case || null, stat: e.stat });
    });
    (contenu.livres || []).forEach(function (l) {
      if (partie.livres && partie.livres[l.id] != null && l.annee != null)
        ajouter({ cle: "livre:" + l.id, sorte: "livre", id: l.id, titre: l.titre.fr, auteur: l.auteur, texte: null, debut: l.annee, fin: l.annee, max: maxN, source: l.source, stat: l.stat });
    });
    (contenu.avatar && contenu.avatar.savants || []).forEach(function (s) {
      var a = partie.savants && partie.savants[s.id] != null && lireAnnees(s.annees);
      // Pour un savant, tout siècle de sa vie compte juste ; en mode année exacte, on demande sa naissance (Victor).
      if (a) ajouter({ cle: "savant:" + s.id, sorte: "savant", id: s.id, titre: s.nom.fr, texte: null, debut: a.debut, fin: a.fin, max: a.naissanceVers ? 2 : maxN, source: s.source, theme: s.theme });
    });
    (contenu.objets || []).forEach(function (o) {
      if (partie.objets && partie.objets[o.id] != null && o.annee != null)
        ajouter({ cle: "objet:" + o.id, sorte: "objet", id: o.id, titre: o.nom.fr, texte: sansDate(o.notice), debut: o.annee, fin: o.annee, max: maxN, source: o.source, theme: o.theme });
    });
    return out;
  }
  // La case du pion attend sa partie de Chrono.
  function chronoEnAttente(partie) { var s = partie.siecles; return !!(s && s.case && partie.plateau && s.case === partie.plateau.position); }
  // Alyca propose une partie aujourd'hui (et elle n'est pas encore jouée).
  function offreChrono(partie, t) { var s = partie.siecles; return !!(s && s.offre && s.offre === cleJour(t)); }
  function chronoPossible(contenu, partie) { var R = reglesChrono(contenu); return !!(R && reservoirChrono(contenu, partie).length >= R.min_reservoir); }
  // Après une épreuve : Alyca lance-t-elle une partie d'elle-même ? Une chance sur trois, une fois par jour au plus.
  function chronoSpontane(contenu, partie, t, alea) {
    var R = reglesChrono(contenu); if (!R) return false;
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
    if (mode === "case" ? !chronoEnAttente(partie) : !offreChrono(partie, t)) return null;
    var pool = reservoirChrono(contenu, partie);
    // Trop peu d'éléments datés : la case ne retient pas le pion.
    if (pool.length < R.min_reservoir) { if (mode === "case") s.case = null; return null; }
    alea = alea || Math.random;
    var prio = function (x) { var f = s.fiches[x.cle]; return !f ? 2 : f.rate ? 3 : 1; };
    var tries = melanger(pool, alea).sort(function (a, b) {
      var pa = prio(a), pb = prio(b);
      if (pa !== pb) return pb - pa;
      return pa === 1 ? (s.fiches[a.cle].dernier || 0) - (s.fiches[b.cle].dernier || 0) : 0;
    });
    var choix = [], siecles = {};
    tries.forEach(function (x) { var k = creneau(x.debut, 100, R.prehistoire); if (choix.length < R.evenements && !siecles[k]) { siecles[k] = 1; choix.push(x); } });
    tries.forEach(function (x) { if (choix.length < R.evenements && choix.indexOf(x) < 0) choix.push(x); });
    s.jeu = { mode: mode, depuis: t, case: mode === "case" ? s.case : null, reponses: [], questions: choix.map(function (x) {
      var f = s.fiches[x.cle], n = Math.min(f ? f.niveau : 1, x.max), N = niveauChrono(R, n);
      return Object.assign({}, x, { niveau: n, pas: N.pas, proche: N.proche, nomNiveau: N.nom.fr, naissance: x.sorte === "savant" && N.pas < 50 });
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
      // La case est jouée, réussie ou non : on n'y revient pas.
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
      ouvrirLot(partie, t, null);
      if (parfait) out.agacement = agacerIA(contenu, partie, 0, false, t);
      out.recompenses = out.avantPlateau = verifierRecompenses(contenu, partie, t);
      out.apresPlateau = { succes: [], objets: [], accessoires: [], savants: [], evenements: [], livres: [], masque: null, gagnables: [], credits: [] };
    }
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
  function fichesImposees(contenu, partie, t, n) {
    var rates = {};
    (partie.oublis || []).forEach(function (e) { var q = contenu.questionParId && contenu.questionParId[e.q]; if (q && joursEntre(e.t, t) <= 30) rates[q.competence] = (rates[q.competence] || 0) + 1; });
    function poids(k) { var e = partie.competences[k.id]; return (rates[k.id] || 0) * 1e15 + (estMaitrisee(partie, k.id) ? 1e14 - Math.max(0, e.prochainRappel - t) / 1000 : 0); }
    return contenu.competences.filter(function (k) { return k.fiche && arbreOuvert(contenu, partie, k.stat); })
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
      // v15 : une case survolée ne débloque rien ; il faut s'y être arrêté.
      case "case_atteinte": return (partie.plateau.visites[cond.n] || 0) > 0;
      case "epoque_atteinte": return partie.plateau.tours > 0 || partie.plateau.atteinte >= cond.n;
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
  function ouvrirLot(partie, t, theme) { partie.lot = { t: t, n: 0, r: 0, theme: theme || null }; }
  function lotDe(partie, t) { return partie.lot && partie.lot.t === t ? partie.lot : { t: t, n: 0, r: 0, theme: null }; }
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
          liste = place <= 0 ? [] : liste.filter(function (x) { return !f[2][x.id] && conditionRemplie(contenu, partie, x.condition, t); });
          if (lot.theme) liste = liste.filter(function (x) { return themeDe(x) === lot.theme; }).concat(liste.filter(function (x) { return themeDe(x) !== lot.theme; }));
          // Les pionniers ouvrent un arbre : ils ne font jamais la queue.
          liste = liste.filter(function (x) { return x.ouvre; }).concat(liste.filter(function (x) { return !x.ouvre; }));
          liste = liste.slice(0, Math.max(0, place));
        }
        liste.forEach(function (x) {
          if (f[2][x.id] || (FAMILLES_LOT[f[0]] && lot.n) || (f[0] !== "evenements" && lotPlein(lot)) || !conditionRemplie(contenu, partie, x.condition, t)) return;
          if (f[0] === "evenements" && !dateAtteinte(contenu, partie, x)) return;
          f[2][x.id] = t; out[f[0]].push(x); change = true; compterLot(lot, f[0]);
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
  // La frise suit le pion : pendant le premier tour, une date (gagnée par une compétence) attend que le pion
  // ait atteint son époque. Au début du parcours, on ne débloque donc que de l'antique.
  function dateAtteinte(contenu, partie, ev) {
    var P = contenu.plateau, pl = partie.plateau;
    if (!P || !pl || pl.tours > 0 || ev.annee == null) return true;
    var k = P.cases[Math.max(1, pl.atteinte || 1) - 1];
    var e = k && (P.epoques || []).filter(function (x) { return x.id === k.epoque; })[0];
    return !e || e.fin == null || Number(ev.annee) <= e.fin;
  }
  function epoqueCase(contenu, partie) {
    var P = contenu.plateau, k = P && partie.plateau && P.cases[partie.plateau.position - 1];
    return k ? (P.epoques || []).filter(function (e) { return e.id === k.epoque; })[0] || null : null;
  }
  function finEpoqueCase(contenu, partie) { var e = epoqueCase(contenu, partie); return e ? e.fin : null; }
  // --- v18 : le thème. La case du pion donne le ton : butin, cadeaux, apartés, masques, farces et répliques ---
  // Le thème d'une chose : son champ `theme` (objets, savants, masques, ennemis, succès), sinon son arbre (livres).
  function themeDe(x) { return x ? x.theme || x.stat || null : null; }
  // Le thème de la case où se tient le pion.
  function themeCase(contenu, partie) {
    var k = contenu.plateau && partie.plateau && contenu.plateau.cases[partie.plateau.position - 1];
    return k ? k.stat || null : null;
  }
  // Le thème d'une épreuve : l'arbre de sa compétence, celui de l'ennemi d'un duel, sinon celui de la case.
  function themeEpreuve(contenu, partie, epreuve) {
    if (epreuve && epreuve.comp && contenu.parId[epreuve.comp]) return contenu.parId[epreuve.comp].stat;
    if (epreuve && epreuve.ennemi && contenu.ennemiParId && contenu.ennemiParId[epreuve.ennemi]) return themeDe(contenu.ennemiParId[epreuve.ennemi]);
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

  // Si le sort tombe sur un livre, l'IA prend de préférence un livre de l'époque de la case, sinon le plus récent permis.
  // v18 : et, parmi eux, de préférence un livre du thème.
  function livreDeLaCase(contenu, partie, ouvert, alea, theme) {
    var e = epoqueCase(contenu, partie), livres = ouvert.filter(function (b) { return b.famille === "livres"; });
    if (!e || !livres.length) return null;
    var ici = livres.filter(function (b) { var a = Number(b.chose.annee); return (e.debut == null || a >= e.debut) && (e.fin == null || a <= e.fin); });
    ici = duTheme(ici, theme, "livre|" + partie.journal.length, function (b) { return b.chose; });
    if (ici.length) return ici[Math.floor(alea() * ici.length)];
    return livres.slice().sort(function (a, b) { return Number(b.chose.annee) - Number(a.chose.annee); })[0];
  }
  // v8 : case cadeau. Un objet du cabinet tombe sans épreuve ; à défaut, n'importe quel autre butin ouvert.
  function tirerCadeau(contenu, partie, t) {
    var lot = lotDe(partie, t), ouvert = horsLot(lot, butinOuvert(contenu, partie)), objets = ouvert.filter(function (b) { return b.famille === "objets"; });
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
  // Après une épreuve réussie : au plus un butin, tiré au hasard. `alea` (facultatif) pour les tests.
  function tirerButin(contenu, partie, epreuve, t, alea) {
    alea = alea || Math.random;
    var lot = lotDe(partie, t); if (lotPlein(lot)) return null;
    var ouvert = horsLot(lot, butinOuvert(contenu, partie));
    var fav = epreuve.type === "duel" ? null : faveurIA(contenu, partie, t);
    var assure = partie.butinAssure && epreuve.type !== "duel" && ouvert.length;
    if (assure) partie.butinAssure = false;
    var mult = epreuve.type === "duel" ? 1 : reglesDuJour(contenu, partie, t).butin;
    if (!assure && (!ouvert.length || alea() >= chanceButin(contenu, epreuve) * (fav ? fav.palier.butin : 1) * mult)) return null;
    // v18 : trois fois sur quatre, le butin vient du thème de l'épreuve quand il y en a un en attente.
    var th = themeEpreuve(contenu, partie, epreuve), pool = duTheme(ouvert, th, t + "|" + partie.journal.length, function (x) { return x.chose; });
    var b = pool[Math.floor(alea() * pool.length)];
    if (b.famille === "livres") b = livreDeLaCase(contenu, partie, ouvert, alea, themeDe(b.chose)) || b;
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
  var RETARD_PRIORITAIRE = 2 * JOUR;
  function choixIA(contenu, partie, t) {
    var rv = revisionEnCours(partie);
    if (rv) return { comp: contenu.parId[rv.comp], type: "rappel", raison: "revision" };
    var dus = rappelsDus(contenu, partie, t);
    var dispo = disponibles(contenu, partie, t);
    var graine = hacher(cleJour(t) + "|" + partie.journal.length + "|" + (partie.cree || 0));
    // v15 : la case où se tient le pion dicte l'arbre. Les rappels dus passent toujours d'abord (ceux de cet arbre
    // en tête, l'oubli n'attend pas), puis un quiz de cet arbre ; sinon l'ancien choix, annoncé comme hors case.
    var k = contenu.plateau && partie.plateau && contenu.plateau.cases[partie.plateau.position - 1];
    var ach = arbreAchete(partie);
    var st = ach ? ach.stat : k && k.stat;
    // v31 (Victor) : la case évoque des compétences précises (Mendel → Génétique) : elles passent avant le reste de l'arbre.
    var CC = contenu.plateau && contenu.plateau.competences_cases, evoque = (k && CC && CC[String(k.n)]) || [];
    if (ach && k && k.stat !== ach.stat) evoque = [];
    function evoquee(c) { return evoque.indexOf(c.id) >= 0; }
    // Un rappel très en retard (RETARD_PRIORITAIRE) passe avant tout ; les autres attendent leur arbre.
    var urgents = dus.filter(function (c) { return t - partie.competences[c.id].prochainRappel >= RETARD_PRIORITAIRE && c.stat !== st; });
    if (urgents.length) return { comp: urgents[0], type: "rappel", raison: "rappel", stat: null, kase: k || null, achat: false };
    var dusEvoques = dus.filter(evoquee);
    if (dusEvoques.length) return { comp: dusEvoques[0], type: "rappel", raison: "rappel", stat: st, kase: k || null, achat: !!ach, evoque: true };
    var dispoEvoques = dispo.filter(evoquee);
    if (dispoEvoques.length) return { comp: dispoEvoques[graine % dispoEvoques.length], type: "quiz", raison: "case", stat: st, kase: k, achat: !!ach, evoque: true };
    // Compétence évoquée encore verrouillée : l'IA prend le prérequis jouable qui en rapproche (Cellule avant Génétique).
    var chemin = [];
    evoque.forEach(function (id) {
      var file = (contenu.parId[id] ? contenu.parId[id].prerequis : []).slice(), vu = {};
      while (file.length) {
        var p = file.shift(); if (vu[p] || !contenu.parId[p]) continue; vu[p] = true;
        if (dispo.some(function (c) { return c.id === p; })) { if (!chemin.some(function (x) { return x.comp.id === p; })) chemin.push({ comp: contenu.parId[p], vers: id }); }
        else file = file.concat(contenu.parId[p].prerequis);
      }
    });
    if (chemin.length) { var ch = chemin[graine % chemin.length]; return { comp: ch.comp, type: "quiz", raison: "case", stat: st, kase: k, achat: !!ach, vers: contenu.parId[ch.vers] }; }
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
    if (!contenu.avatar) return null;
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
  function nomIA(contenu, partie) { return partie.alyca && contenu.ia && contenu.ia.alyca ? contenu.ia.alyca.nom : null; }

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
    var fav = faveurIA(contenu, partie, maintenant(partie)), furieuse = !!(fav && fav.palier.id === "furieuse");
    for (var i = 0; i < contextes.length; i++) {
      var ctx = contextes[i], lignes = contenu.commentairesPar[ctx];
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
    routeTour: routeTour,
    remanierRoute: remanierRoute,
    caseDecouverte: caseDecouverte,
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
    replique: replique,
    repliqueDuJour: repliqueDuJour,
    themeDe: themeDe, themeCase: themeCase, themeEpreuve: themeEpreuve,
    masqueActuel: masqueActuel, masqueDebloque: masqueDebloque, masquePourTon: masquePourTon, aparte: aparte,
    choixIA: choixIA, choixArbre: choixArbre, tarifSucces: tarifSucces, tenterUltimatum: tenterUltimatum, repondreUltimatum: repondreUltimatum, exigence: exigence, retirerNiveaux: retirerNiveaux, agacerIA: agacerIA, potPossible: potPossible, corrompre: corrompre, dateAtteinte: dateAtteinte, humeur: humeur, revisionEnCours: revisionEnCours, compARevisier: compARevisier, arbreOuvert: arbreOuvert, specialDe: specialDe, ennemisPlateau: ennemisPlateau, tirerDuel: tirerDuel, terminerDuel: terminerDuel,
    faveurIA: faveurIA, radoucirIA: radoucirIA, jeuFerme: jeuFerme, purger: purger, questionRattrapage: questionRattrapage, repondreRattrapage: repondreRattrapage, themesCorvee: themesCorvee, fichesImposees: fichesImposees, piegeIA: piegeIA, masquesDuJour: masquesDuJour, reglesDuJour: reglesDuJour, questionsQuiz: questionsQuiz, seuilAtome: seuilAtome,
    atomeSauvage: atomeSauvage, tirerCombat: tirerCombat, astuceNumero: astuceNumero, atomeDit: atomeDit, lectureCouches: lectureCouches, dessinCouches: dessinCouches, COULEURS_COUCHES: COULEURS_COUCHES, terminerCombat: terminerCombat, laisserPartir: laisserPartir, acheter: acheter, duelBloquant: duelBloquant, piegeEnAttente: piegeEnAttente, questionPiege: questionPiege, repondrePiege: repondrePiege, choisirSuite: choisirSuite, dessinerParcours: dessinerParcours, formeParcours: formeParcours, bornesBonusJouer: bornesBonusJouer, emplettesIA: emplettesIA, empletteAVoir: empletteAVoir, utiliser: utiliser, enPoche: enPoche, joker: joker, relancerAtome: relancerAtome, enRayon: enRayon, boutique: boutique, arbreAchete: arbreAchete, estCapture: estCapture, texteMasse: texteMasse,
    ficheBestiaire: ficheBestiaire, cadeauPossible: cadeauPossible, donnerObjet: donnerObjet, pionnierDe: pionnierDe, surnom: surnom, tirerButin: tirerButin, butinOuvert: butinOuvert, chanceButin: chanceButin, savantActuel: savantActuel, tenterFarce: tenterFarce, farceActive: farceActive, rendreVisage: rendreVisage, nomIA: nomIA,
    expression: expression,
    bonusDuJour: bonusDuJour,
    valeurEpreuve: valeurEpreuve,
    deplacer: deplacer,
    avancerPion: avancerPion,
    cleJour: cleJour,
    jouerPlateau: jouerPlateau,
    murDeLaHonte: murDeLaHonte,
    reglesChrono: reglesChrono, etatChrono: etatChrono, creneau: creneau, anneeDuCreneau: anneeDuCreneau, texteCreneau: texteCreneau, texteSiecle: texteSiecle,
    reservoirChrono: reservoirChrono, chronoEnAttente: chronoEnAttente, offreChrono: offreChrono, chronoPossible: chronoPossible, chronoSpontane: chronoSpontane,
    lancerChrono: lancerChrono, jeuChrono: jeuChrono, repondreChrono: repondreChrono, terminerChrono: terminerChrono, statsChrono: statsChrono,
    retenterOubli: retenterOubli,
  };

  if (typeof module === "object" && module.exports) module.exports = Moteur;
  else racine.Moteur = Moteur;
})(typeof globalThis !== "undefined" ? globalThis : this);
