"""v26 : présenter les ennemis. Victor a affronté Cesare Lombroso sans savoir qui c'était.

`qui` : qui il est, en clair, avant le duel. `lecon` : ce qu'on retient de son erreur, montré au verdict et au bestiaire.
Les personnages historiques ont vraiment existé ; les archétypes sont des caricatures inventées par l'IA.
"""

FICHES = {
    "sophiste": (
        "Une caricature. Les vrais sophistes étaient des professeurs d'éloquence payés, dans la Grèce du Ve siècle av. J.-C., comme Protagoras ou Gorgias. Platon les a dépeints en marchands de mots. L'IA a gardé le marchand.",
        "Un argument se juge sur sa structure, pas sur l'aplomb de celui qui le défend."),
    "platiste": (
        "Une caricature du « platiste ». Les savants du Moyen Âge savaient la Terre ronde. Le mythe d'une Église qui la croyait plate a surtout été répandu au XIXe siècle.",
        "Ne pas avoir vérifié une chose ne prouve pas son contraire."),
    "influenceur": (
        "Une caricature du vendeur de bien-être des réseaux sociaux, lointain héritier des marchands d'élixirs.",
        "Une promesse de santé sans mécanisme connu ni étude contrôlée ne vaut rien, même avec de beaux filtres."),
    "astrologue": (
        "Une caricature. L'astrologie, née en Mésopotamie, a longtemps été pratiquée par des astronomes, puis les deux disciplines se sont séparées à l'époque moderne.",
        "En 1985, des astrologues soumis à un test à l'aveugle n'ont pas fait mieux que le hasard."),
    "mesmer": (
        "Franz Anton Mesmer, médecin allemand installé à Vienne, puis à Paris en 1778. Il affirmait qu'un « fluide magnétique » circule dans tous les corps et qu'on guérit en le rééquilibrant.",
        "La commission de 1784 bande les yeux des patients : sans savoir qu'on les « magnétise », ils ne ressentent plus rien. C'est l'un des premiers tests à l'aveugle, et la preuve du pouvoir de l'imagination."),
    "lyssenko": (
        "Trofim Lyssenko, agronome soviétique devenu, avec l'appui de Staline, le maître de la biologie en URSS. La génétique y est interdite en 1948.",
        "Quand le pouvoir décide de ce qui est vrai en science, ce sont les récoltes et les chercheurs qui paient."),
    "complotiste": (
        "Une caricature : celui qui voit un plan secret derrière chaque événement.",
        "Plus un complot demande de complices qui se taisent, moins il a de chances de rester secret longtemps."),
    "charlatan": (
        "Une caricature du vendeur de remèdes miracles, des foires du Pont-Neuf au XVIIe siècle jusqu'aux boutiques en ligne.",
        "Un remède qui prétend tout soigner n'a en général rien soigné du tout."),
    "pline": (
        "Pline l'Ancien, officier et naturaliste romain. Son Histoire naturelle, en 37 livres, a servi de référence pendant plus de mille ans.",
        "Compiler sans vérifier, c'est beaucoup de savoir et beaucoup d'erreurs. Lui, au moins, citait ses sources."),
    "gall": (
        "Franz Joseph Gall, médecin allemand et anatomiste du cerveau, fondateur de la phrénologie à la fin du XVIIIe siècle.",
        "Une intuition juste, des régions du cerveau spécialisées, peut être ruinée par une méthode fausse : tâter des bosses."),
    "ussher": (
        "James Ussher, archevêque anglican d'Armagh, en Irlande, et grand érudit. Il voulait dater toute l'histoire du monde à partir des textes.",
        "Son calcul était rigoureux. Ce sont ses données de départ qui ne pouvaient pas mesurer le temps géologique."),
    "diafoirus": (
        "Un personnage de théâtre : Thomas Diafoirus, jeune médecin pédant du Malade imaginaire de Molière, qui récite ses maîtres sans jamais regarder le malade.",
        "Citer une autorité ne remplace pas une preuve."),
    "bessler": (
        "Johann Bessler, dit Orffyreus, inventeur allemand qui prétendait avoir construit une roue à mouvement perpétuel.",
        "Le mouvement perpétuel contredit la conservation de l'énergie. Dès 1775, l'Académie des sciences de Paris refuse d'examiner ces projets."),
    "raconteur": (
        "Une caricature : le colporteur d'anecdotes historiques trop belles pour être vraies.",
        "Marc Bloch le note en 1921 : une fausse nouvelle prospère quand elle confirme ce que le public croit déjà."),
    "lombroso": (
        "Cesare Lombroso, médecin italien, professeur à Turin, fondateur de « l'anthropologie criminelle ». Dans L'Homme criminel (1876), il affirme que le criminel est un être en retard dans l'évolution, reconnaissable à la forme de son corps.",
        "Des mesures prises pour confirmer un préjugé produisent une fausse science. Ses idées ont pourtant pesé sur les tribunaux et la police pendant des décennies."),
    "tribun": (
        "Une caricature : l'orateur qui parle longtemps pour ne rien dire.",
        "Pour Orwell, le langage politique sert à rendre les mensonges crédibles. Le remède : demander des faits et des chiffres sourcés."),
}
