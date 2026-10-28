"""v26 : un extrait du vrai livre, dans sa langue, avec sa traduction. Demande de Victor (2026-10-28).

Règle : rien d'inventé. Chaque extrait est contrôlé mot pour mot sur un texte en ligne (Gutenberg, Wikisource,
Perseus, The Latin Library, archives…) avant d'entrer ici, et la trace du contrôle est gardée dans `verification`.
Sans texte exact trouvé, pas d'extrait. outils/verifier_sources.py refuse un extrait sans vérification.

Champs : texte (original), langue, traduction (absente si le texte est en français), traducteur (qui a traduit :
une traduction publiée, ou « traduction de l'IA »), reference (où dans le livre), verification {url, date, controle}.
Livres encore protégés : une ou deux phrases au plus (droit de citation).
"""

EXTRAITS = {
    "papyrus-edwin-smith": {
        "texte": "An ailment which I will treat. · An ailment with which I will contend. · An ailment not to be treated.",
        "langue": "anglais, trad. de l'égyptien par J. H. Breasted",
        "traduction": "Un mal que je soignerai. · Un mal que je combattrai. · Un mal qu'on ne soigne pas.",
        "traducteur": "Traduction de l'IA, depuis l'anglais de Breasted (1930).",
        "reference": "Les trois verdicts qui concluent chaque cas",
        "verification": {"url": "https://en.wikipedia.org/wiki/Edwin_Smith_Papyrus", "date": "2026-10-28",
                         "controle": "Les trois formules de Breasted, mot pour mot"},
    },
    "papyrus-rhind": {
        "texte": "Accurate reckoning. The entrance into the knowledge of all existing things and all obscure secrets.",
        "langue": "anglais, trad. de l'égyptien par A. B. Chace",
        "traduction": "Calcul exact. L'entrée dans la connaissance de toutes les choses qui existent et de tous les secrets obscurs.",
        "traducteur": "Traduction de l'IA, depuis l'anglais de Chace (1927).",
        "reference": "Titre du papyrus",
        "verification": {"url": "https://en.wikipedia.org/wiki/Rhind_Mathematical_Papyrus", "date": "2026-10-28",
                         "controle": "Titre selon la table fondée sur Chace (1927-1929), mot pour mot"},
    },
    "maladie-sacree": {
        "texte": "It is thus with regard to the disease called Sacred: it appears to me to be nowise more divine nor more sacred than other diseases, but has a natural cause",
        "langue": "anglais, trad. du grec par Francis Adams",
        "traduction": "Voici ce qu'il en est de la maladie qu'on dit sacrée : elle ne me paraît en rien plus divine ni plus sacrée que les autres maladies, mais elle a une cause naturelle",
        "traducteur": "Traduction de l'IA, depuis l'anglais d'Adams (1849).",
        "reference": "Première phrase du traité",
        "verification": {"url": "https://classics.mit.edu/Hippocrates/sacred.html", "date": "2026-10-28",
                         "controle": "Phrase d'ouverture d'Adams, mot pour mot jusqu'à « natural cause » (la suite est mal transcrite sur la page, d'où la coupe)"},
    },
    "republique": {
        "texte": "Μετὰ ταῦτα δή, εἶπον, ἀπείκασον τοιούτῳ πάθει τὴν ἡμετέραν φύσιν παιδείας τε πέρι καὶ ἀπαιδευσίας.",
        "langue": "grec ancien",
        "traduction": "Et maintenant, dis-je, représente-toi notre nature, selon qu'elle est instruite ou non, par l'image que voici.",
        "traducteur": "Traduction de l'IA, avec l'anglais de Jowett en appui (« let me show in a figure how far our nature is enlightened or unenlightened »).",
        "reference": "Livre VII, 514a : début de l'allégorie de la caverne",
        "verification": {"url": "https://www.ellopos.net/elpenor/greek-texts/ancient-greece/plato-paideia-cave.asp", "date": "2026-10-28",
                         "controle": "Grec de 514a et anglais de Jowett, mot pour mot"},
    },
    "rhetorique": {
        "texte": "Rhetoric may be defined as the faculty of observing in any given case the available means of persuasion.",
        "langue": "anglais, trad. du grec par W. Rhys Roberts",
        "traduction": "On peut définir la rhétorique comme la faculté de voir, dans chaque cas, les moyens disponibles de persuader.",
        "traducteur": "Traduction de l'IA, depuis l'anglais de Roberts.",
        "reference": "Livre I, chapitre 2 : la définition",
        "verification": {"url": "https://www.ellopos.net/elpenor/greek-texts/ancient-greece/aristotle/rhetoric.asp?pg=5", "date": "2026-10-28",
                         "controle": "Phrase de la traduction Roberts, mot pour mot (partie 2)"},
    },
    "elements": {
        "texte": "Σημεῖόν ἐστιν, οὗ μέρος οὐθέν.",
        "langue": "grec ancien",
        "traduction": "Un point est ce qui n'a aucune partie.",
        "traducteur": "Traduction de l'IA ; en anglais chez Heath : « A point is that which has no part ».",
        "reference": "Livre I, définition 1",
        "verification": {"url": "https://www.maths.tcd.ie/~dwilkins/Euclid/Euclid_HeathCommentaries/EuclidElements_HeathCommentary_ElementsBk01Def01_DraftTranscription.pdf", "date": "2026-10-28",
                         "controle": "Grec et anglais de la définition 1 chez Heath ; la transcription brute porte οὖ, accent de lecture corrigé en οὗ (pronom relatif)"},
    },
    "arenaire": {
        "texte": "There are some, king Gelon, who think that the number of the sand is infinite in multitude",
        "langue": "anglais, trad. du grec",
        "traduction": "Certains pensent, roi Gélon, que le nombre des grains de sable est infini",
        "traducteur": "Traduction de l'IA, depuis l'anglais.",
        "reference": "Première phrase, adressée au roi de Syracuse",
        "verification": {"url": "https://mrob.com/pub/math/sandreckoner.html", "date": "2026-10-28",
                         "controle": "Phrase d'ouverture, mot pour mot"},
    },
    "de-architectura": {
        "texte": "Well building hath three conditions: firmness, commodity, and delight",
        "langue": "anglais, adaptation du latin par Henry Wotton (1624)",
        "traduction": "Bien bâtir demande trois choses : la solidité, la commodité et l'agrément.",
        "traducteur": "Traduction de l'IA. Le latin de Vitruve dit firmitas, utilitas, venustas.",
        "reference": "Livre I, chapitre 3, § 2",
        "verification": {"url": "https://en.wikipedia.org/wiki/De_architectura", "date": "2026-10-28",
                         "controle": "Formule de Wotton et référence I.iii.2, mot pour mot ; triade latine utilitas, firmitas, venustas"},
    },
    "pneumatiques": {
        "texte": "The investigation of the properties of Atmospheric Air having been deemed worthy of close attention by the ancient philosophers and mechanists",
        "langue": "anglais, trad. du grec par Bennet Woodcroft",
        "traduction": "L'étude des propriétés de l'air ayant été jugée digne d'une grande attention par les philosophes et les mécaniciens de l'Antiquité",
        "traducteur": "Traduction de l'IA, depuis l'anglais de Woodcroft (1851).",
        "reference": "Introduction de Héron, première phrase",
        "verification": {"url": "https://gutenberg.org/cache/epub/77400/pg77400-images.html", "date": "2026-10-28",
                         "controle": "Début de la première phrase de l'introduction, mot pour mot (Project Gutenberg 77400)"},
    },
    "arithmetica": {
        "texte": "cujus rei demonstrationem mirabilem sane detexi. Hanc marginis exiguitas non caperet.",
        "langue": "latin, de la main de Pierre de Fermat",
        "traduction": "J'en ai découvert une démonstration vraiment merveilleuse. Cette marge est trop étroite pour la contenir.",
        "traducteur": "Traduction de l'IA. Ce n'est pas Diophante qui parle : c'est la note de Fermat dans la marge de son exemplaire.",
        "reference": "Marge du problème II.8, édition de 1621 ; note publiée par son fils en 1670",
        "verification": {"url": "https://proofwiki.org/wiki/Fermat's_Marginal_Notes", "date": "2026-10-28",
                         "controle": "Latin de la note, mot pour mot ; problème II.8, édition 1621, publication 1670 (solarspell, copie de Wikipedia Fermat's Last Theorem)"},
    },
    "cryptographie-kindi": {
        "texte": "One way to solve an encrypted message, if we know its language, is to find a different plaintext of the same language long enough to fill one sheet or so, and then we count the occurrences of each letter.",
        "langue": "anglais, trad. de l'arabe citée par Simon Singh",
        "traduction": "Une façon de déchiffrer un message chiffré, si l'on connaît sa langue, est de trouver un autre texte clair dans la même langue, assez long pour remplir une feuille environ, puis de compter les occurrences de chaque lettre.",
        "traducteur": "Traduction de l'IA, depuis l'anglais cité dans The Code Book (1999).",
        "reference": "Le principe de l'analyse des fréquences",
        "verification": {"url": "https://iang.org/crypto_fiction/singh_the_arab_cryptanalysts.html", "date": "2026-10-28",
                         "controle": "Phrase entière, mot pour mot, extrait de Singh"},
    },
    "liber-abaci": {
        "texte": "Quidam posuit unum par cuniculorum in quodam loco, qui erat undique pariete circundatus",
        "langue": "latin",
        "traduction": "Un homme mit un couple de lapins dans un lieu entouré de murs de tous côtés",
        "traducteur": "Traduction de l'IA. C'est le problème d'où sort la suite de Fibonacci.",
        "reference": "Chapitre 12 : le problème des lapins",
        "verification": {"url": "https://www.math.utah.edu/~beebe/software/java/fibonacci/liber-abaci.html", "date": "2026-10-28",
                         "controle": "Latin de l'édition Boncompagni, mot pour mot (Qvidam imprimé avec un V)"},
    },
    "opus-majus": {
        "texte": "since without experience nothing can be sufficiently known",
        "langue": "anglais, trad. du latin par Robert Belle Burke",
        "traduction": "car sans l'expérience, rien ne peut être suffisamment connu",
        "traducteur": "Traduction de l'IA, depuis l'anglais de Burke (1928).",
        "reference": "Partie sur la science expérimentale",
        "verification": {"url": "https://medieval.ucdavis.edu/120B/Bacon.html", "date": "2026-10-28",
                         "controle": "Fragment de la traduction Burke, mot pour mot"},
    },
    # --- Lot 2 : Renaissance et XVIIe -------------------------------------------------
    "sidereus": {
        "texte": "Magna, longeque admirabilia spectacula pandens, suspiciendaque proponens unicuique",
        "langue": "latin",
        "traduction": "Dévoilant de grands et très admirables spectacles, et les proposant à la contemplation de chacun",
        "traducteur": "Traduction de l'IA.",
        "reference": "Page de titre (Venise, 1610)",
        "verification": {"url": "https://early-astronomy.web.itd.umich.edu/western_messenger1.php", "date": "2026-10-28",
                         "controle": "Titre latin reproduit mot pour mot (graphie « unicuique » de la page)"},
    },
    "novum-organum": {
        "texte": "Human knowledge and human power meet in one; for where the cause is not known the effect cannot be produced.",
        "langue": "anglais, traduit du latin",
        "traduction": "Savoir humain et puissance humaine se rejoignent ; car là où l'on ignore la cause, on ne peut produire l'effet.",
        "traducteur": "Traduction de l'IA, depuis l'anglais.",
        "reference": "Livre I, aphorisme III",
        "verification": {"url": "https://sourcebooks.web.fordham.edu/mod/bacon-aphor.asp", "date": "2026-10-28",
                         "controle": "Aphorisme III du livre I, mot pour mot"},
    },
    "discours": {
        "texte": "Le bon sens est la chose du monde la mieux partagée ; car chacun pense en être si bien pourvu, que ceux même qui sont les plus difficiles à contenter en toute autre chose n'ont point coutume d'en désirer plus qu'ils en ont.",
        "langue": "français (édition Cousin)",
        "reference": "Première phrase, première partie",
        "verification": {"url": "https://people.duke.edu/~garci/cibertextos/frances/DESCARTES-RENE/TRANSLATE/DISCOURS-METHODE-FR-EN.HTM", "date": "2026-10-28",
                         "controle": "Phrase complète, mot pour mot (apostrophes typographiques sur la page)"},
    },
    "micrographia": {
        "texte": "I could exceeding plainly perceive it to be all perforated and porous, much like a Honey-comb",
        "langue": "anglais",
        "traduction": "Je pouvais voir très clairement qu'il était tout percé et poreux, un peu comme un rayon de miel",
        "traducteur": "Traduction de l'IA. Il parle d'une fine lamelle de liège : ces pores, il les appelle « cells ».",
        "reference": "Observation XVIII, sur le liège",
        "verification": {"url": "https://b-s-h.org.uk/bsh-at-60/60-at-60-exhibition/tools-of-the-trade/microscopes/much-like-a-honey-comb-discovering-the-cell", "date": "2026-10-28",
                         "controle": "Phrase de Hooke mot pour mot, suivie sur la page de « These pores, or cells »"},
    },
    "principia": {
        "texte": "Mutationem motus proportionalem esse vi motrici impressæ, & fieri secundum lineam rectam qua vis illa imprimitur.",
        "langue": "latin",
        "traduction": "Le changement du mouvement est proportionnel à la force motrice imprimée, et se fait selon la ligne droite suivant laquelle cette force est imprimée.",
        "traducteur": "Traduction de l'IA. C'est la deuxième loi, celle qu'Euler mettra plus tard sous la forme F = m a.",
        "reference": "Lex II",
        "verification": {"url": "https://telescoper.blog/2019/11/13/newtons-laws-in-translation/", "date": "2026-10-28",
                         "controle": "Latin de la Lex II mot pour mot, avec la traduction anglaise de 1792"},
    },
}


def donnees(id):
    e = EXTRAITS.get(id)
    if not e:
        return None
    out = {"texte": e["texte"], "langue": e["langue"], "reference": e["reference"], "verification": e["verification"]}
    if e.get("traduction"):
        out["traduction"] = {"fr": e["traduction"]}
        out["traducteur"] = e["traducteur"]
    return out
