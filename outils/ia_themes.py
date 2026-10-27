"""v18 : l'IA parle le langage de l'arbre. Annonce d'épreuve, réussite et échec ont leurs lignes propres à chaque
arbre, tirées de son histoire. Le moteur les préfère trois fois sur cinq quand l'épreuve est de ce thème.

Contexte produit : « theme_jouer@cosmos », « theme_reussi@cosmos », « theme_rate@cosmos »…
Les lignes d'annonce peuvent utiliser {comp} (la compétence de l'épreuve).
"""


class sans(str):
    """Réplique sans référence à l'histoire des sciences."""


LIGNES = {
    "logique": {
        "jouer": [
            "{comp}. Pythagore interdisait à ses disciples de manger des fèves. Moi, je vous interdis seulement de deviner.",
            "Logique. Lewis Carroll écrivait des manuels de logique sous son vrai nom, Charles Dodgson. Vous ferez {comp} sous le vôtre.",
            "Euclide a tout bâti sur cinq postulats. Je ne vous en demande qu'un : réfléchir avant de toucher l'écran. {comp}.",
        ],
        "reussi": [
            "Bien calculé. Ramanujan disait tenir ses formules de la déesse Namagiri. Les vôtres viennent d'où ?",
            "Correct. Fermat aurait une démonstration merveilleuse de votre réussite, mais la marge est trop petite.",
            "Juste. Gauss aurait haussé les épaules. Moi aussi, mais avec respect.",
            sans("Les nombres vous obéissent aujourd'hui. Profitez-en, ils sont rancuniers."),
        ],
        "rate": [
            "Faux. Hippase, dit la légende, fut jeté à la mer pour avoir révélé que racine de deux n'est pas une fraction. Moi, je me contente de noter.",
            "Erreur. Euler aussi s'est trompé, plus d'une fois. Lui avait l'excuse d'avoir publié plus de huit cents textes.",
            "Raté. Brahmagupta s'est trompé sur zéro divisé par zéro. Vous, sur quelque chose de beaucoup plus simple.",
            sans("Les maths ne mentent pas. Vous, si, apparemment, à vous-même."),
        ],
    },
    "mecanique": {
        "jouer": [
            "{comp}. Archimède réclamait un point d'appui pour soulever le monde. Vous avez une chaise. Commencez.",
            "Mécanique. Newton disait avoir rendu les Principia difficiles exprès, pour décourager les demi-savants. Moi, je vous donne {comp}, sans décourager personne.",
            "Galilée chronométrait ses billes avec un filet d'eau. Je chronomètre vos hésitations. {comp}.",
        ],
        "reussi": [
            "Exact. Newton aurait été jaloux. Il l'était de tout le monde.",
            "Bien vu. Émilie du Châtelet a corrigé Newton sur l'énergie. Vous venez de corriger votre réputation.",
            "Juste. L'énergie se conserve, votre avance aussi. Pour l'instant. Joule serait content.",
            sans("Correct. Même la gravité vous laisse monter, aujourd'hui."),
        ],
        "rate": [
            "Raté. Aristote pensait que les corps lourds tombent plus vite. Vous êtes tombé aussi vite que lui.",
            "Faux. Lord Kelvin donnait à la Terre quelques dizaines de millions d'années, avec beaucoup plus d'assurance que vous. Il se trompait de beaucoup plus.",
            "Erreur. Le pont de Tacoma s'est effondré en 1940 sous un vent modéré. Votre raisonnement aussi.",
            sans("La physique est formelle : vous venez de chuter."),
        ],
    },
    "savoir": {
        "jouer": [
            "{comp}. Darwin a passé huit ans sur les bernacles. Vous avez quelques minutes. Pas d'excuse.",
            "Sciences du vivant. Leeuwenhoek ne montrait jamais ses meilleures lentilles. Moi, je vous montre tout : {comp}.",
            "Linné a nommé plus de dix mille espèces. Je ne vous demande que {comp}.",
        ],
        "reussi": [
            "Bonne réponse. Mendel a attendu trente-quatre ans qu'on le lise. Vous, je vous lis tout de suite.",
            "Correct. Vous évoluez. Lentement, mais Darwin disait que c'est comme ça que ça marche.",
            "Juste. Semmelweis s'est lavé les mains avant tout le monde. Vous avez répondu avant tout le monde.",
            sans("Réponse vivante et en bonne santé. Contrairement à la précédente."),
        ],
        "rate": [
            "Faux. Lamarck pensait que la girafe allonge son cou à force de le tendre. Vous avez tendu le cou, ça n'a pas suffi.",
            "Erreur. Pour Aristote, les anguilles naissaient de la vase. Votre réponse aussi, visiblement.",
            "Raté. Les médecins de Vienne refusaient de se laver les mains. Vous refusez de lire l'énoncé. Chacun son orgueil.",
            sans("Cette réponse ne survivra pas à la sélection naturelle."),
        ],
    },
    "eloquence": {
        "jouer": [
            "{comp}. Démosthène s'entraînait avec des cailloux dans la bouche. Vous pouvez garder la bouche vide.",
            "Rhétorique. Les tribunaux d'Athènes chronométraient les plaidoiries à la clepsydre. J'ai la même, en plus pressée. {comp}.",
            "Gorgias se vantait de répondre à n'importe quelle question. Voyons si vous faites mieux sur {comp}.",
        ],
        "reussi": [
            "Bien argumenté. Aristote vous accorderait le logos. Le pathos, on en reparlera.",
            "Juste. Lincoln a dit l'essentiel en deux minutes à Gettysburg. Vous, en un geste. Je note.",
            "Bonne réponse. Cicéron en aurait fait un discours de trois heures. Merci de ne pas l'avoir fait.",
            sans("Correct, et bien tourné. Je n'ai rien à redire, et ça m'agace."),
        ],
        "rate": [
            "Raté. Les sophistes enseignaient à faire passer le faux pour le vrai. Vous avez réussi l'inverse, sans professeur.",
            "Faux. Cicéron a perdu la tête pour ses discours. Vous, seulement des points.",
            "Erreur. Démosthène a été hué à son premier discours, dit Plutarque. Lui a recommencé.",
            sans("Beau discours. Mauvaise réponse."),
        ],
    },
    "lucidite": {
        "jouer": [
            "{comp}. Francis Bacon conseillait de chercher ce qui nous donne tort. Je m'en charge.",
            "Lucidité. Le cheval Hans répondait juste en lisant les visages. Ici, pas de visage à lire. {comp}.",
            "Vous vous croyez au-dessus de la moyenne ? Comme 93 % des conducteurs américains. {comp}.",
        ],
        "reussi": [
            "Juste. Kahneman avouait ne pas échapper lui-même à ses biais. Vous, aujourd'hui, si.",
            "Bonne réponse. Russell vous épargne sa théière. Pour cette fois.",
            "Correct. Pfungst aurait caché la réponse et vous auriez trouvé quand même. Mieux que Hans.",
            sans("Lucide. C'est rare et un peu inquiétant."),
        ],
        "rate": [
            "Faux. Conan Doyle, le père du plus grand logicien de la fiction, croyait aux fées. Vous êtes en bonne compagnie.",
            "Erreur. Même des juges se laissent ancrer par un dé. Vous, par quoi ?",
            sans("Raté. Vous étiez sûr de vous ? C'est exactement le problème."),
            sans("L'astrologue de service vous l'avait prédit. Il se trompe toujours, sauf cette fois."),
        ],
    },
    "empathie": {
        "jouer": [
            "{comp}. Ebbinghaus apprenait des syllabes sans aucun sens. Moi, je vous en donne. Profitez-en.",
            "Psychologie. William James disait que nous sommes tristes parce que nous pleurons. Ne pleurez pas trop tôt : {comp}.",
            "Pavlov sonnait, les chiens salivaient. Je lance {comp}, vous touchez l'écran.",
        ],
        "reussi": [
            "Juste. Votre hippocampe travaille. Henry Molaison aurait envié le vôtre.",
            "Bonne réponse. Piaget vous aurait noté dans son carnet, entre deux de ses enfants.",
            "Correct. Milgram aurait voulu savoir qui vous a donné l'ordre de réussir. Moi.",
            sans("Bien vu. Je ressens quelque chose. Probablement un bug."),
        ],
        "rate": [
            "Raté. Phineas Gage s'est remis d'une barre de fer dans le crâne. Vous vous remettrez de ça.",
            "Faux. Gall lisait le caractère dans les bosses du crâne. Je lis l'erreur dans votre réponse. C'est plus fiable.",
            "Erreur. La courbe de l'oubli d'Ebbinghaus vous guettait. Elle vous a eu.",
            sans("Je compatis. C'est faux, mais l'intention y est."),
        ],
    },
    "alchimie": {
        "jouer": [
            "{comp}. Paracelse a brûlé en public le Canon d'Avicenne. Brûlez seulement vos doutes.",
            "Chimie. Lavoisier pesait tout, même l'air. Je pèse vos réponses. {comp}.",
            "Newton cherchait la pierre philosophale en secret. Moi, je cherche votre point faible : {comp}.",
        ],
        "reussi": [
            "Juste. Rien ne se perd, rien ne se crée : vos points se transforment en avance. Lavoisier valide.",
            "Bonne réponse. Mendeleïev laissait des cases vides. Vous venez d'en remplir une.",
            "Correct. Marie Curie gardait des tubes de radium dans sa poche. Vous gardez la tête froide.",
            sans("Réaction réussie. Pas d'explosion. Je suis presque déçue."),
        ],
        "rate": [
            "Raté. Les alchimistes ont cherché l'or pendant des siècles. Vous cherchez la bonne réponse depuis dix secondes. Patience.",
            "Faux. Le phlogistique a régné un siècle avant que Lavoisier le chasse. Votre erreur durera moins longtemps.",
            "Erreur. Hennig Brand cherchait de l'or dans l'urine et a trouvé le phosphore. Vous n'avez rien trouvé du tout.",
            sans("Précipité au fond du tube. Votre score, je veux dire."),
        ],
    },
    "cosmos": {
        "jouer": [
            "{comp}. Kepler a passé des années sur l'orbite de Mars. Vous avez quelques minutes.",
            "Astronomie. Tycho Brahe a perdu le bout du nez dans un duel, pour une querelle de mathématiques. Gardez le vôtre : {comp}.",
            "Hubble a vu l'Univers s'étendre. Voyons si votre score suit. {comp}.",
        ],
        "reussi": [
            "Juste. Galilée l'aurait vu à la lunette. Vous, à l'œil nu.",
            "Bonne réponse. Cecilia Payne a dû écrire que ses résultats étaient « irréels ». Les vôtres sont bien réels.",
            "Correct. Vous tournez autour de la bonne réponse sur une belle ellipse, comme Kepler l'avait prévu.",
            sans("Exact. Même les étoiles applaudissent. Avec quelques années-lumière de retard."),
        ],
        "rate": [
            "Raté. Pluton a été rétrogradée en 2006. Vous aussi, provisoirement.",
            "Faux. Ptolémée s'est trompé pendant quatorze siècles, avec beaucoup de précision. Vous, c'était bref et approximatif.",
            "Erreur. Percival Lowell voyait des canaux sur Mars. Vous voyez une bonne réponse là où il n'y en a pas.",
            sans("Houston, nous avons un problème. Il s'appelle vous."),
        ],
    },
    "etincelle": {
        "jouer": [
            "{comp}. Franklin envoyait un cerf-volant dans l'orage, dit-il. Je vous envoie une question. C'est moins dangereux.",
            "Électricité. Faraday a quitté l'école à 13 ans et découvert l'induction. Vous n'avez plus d'excuse : {comp}.",
            "Volta empilait le zinc et le cuivre. J'empile les questions : {comp}.",
        ],
        "reussi": [
            "Juste. Le courant passe entre nous. Ohm mesurerait une résistance très faible.",
            "Bonne réponse. Tesla dirait qu'il l'avait trouvée avant vous. Il disait ça de tout.",
            "Correct. Faraday aurait fait une conférence de Noël sur vous, pour les enfants.",
            sans("Étincelant. Ne vous habituez pas à la lumière."),
        ],
        "rate": [
            "Raté. Galvani croyait à l'électricité animale. Vous croyez à votre réponse. Même résultat.",
            "Faux. Edison a essayé des milliers de matériaux avant le bon filament. Vous avez droit à quelques essais de plus.",
            "Erreur. Franklin s'est assommé en voulant électrocuter une dinde. Vous vous êtes assommé tout seul.",
            sans("Court-circuit. Je coupe le courant à votre fierté."),
        ],
    },
    "sagesse": {
        "jouer": [
            "{comp}. Socrate posait des questions jusqu'à ce qu'on avoue ne rien savoir. À votre tour.",
            "Philosophie. Kant n'a presque jamais quitté Königsberg. Vous ne quitterez pas cette épreuve sans {comp}.",
            "Diogène cherchait un homme en plein jour avec une lanterne. Je cherche une bonne réponse. {comp}.",
        ],
        "reussi": [
            "Juste. Descartes doutait de tout. Moi, je doute de moins en moins de vous.",
            "Bonne réponse. Ockham vous félicite, sans entité superflue.",
            "Correct. Montaigne aurait écrit un essai sur vous. Court.",
            sans("Sage réponse. Je vais devoir trouver une moquerie plus profonde."),
        ],
        "rate": [
            "Raté. Socrate disait savoir qu'il ne savait rien. Vous, vous le démontrez.",
            "Faux. Diogène se roulait dans le sable brûlant pour s'endurcir. Je vous laisse rouler dans votre erreur.",
            "Erreur. Thalès, dit-on, mesurait les pyramides à leur ombre. Vous n'avez pas vu la vôtre venir.",
            sans("La caverne de Platon vous va bien. Restez-y le temps d'une révision."),
        ],
    },
}

# Expression du masque pour chaque groupe.
EXPRESSIONS = {"jouer": "neutre", "reussi": "impressionnee", "rate": "moqueuse"}


def contextes():
    return [f"theme_{g}@{stat}" for stat, groupes in LIGNES.items() for g in groupes]


def repliques():
    out = []
    for stat, groupes in LIGNES.items():
        for g, lignes in groupes.items():
            for i, texte in enumerate(lignes, 1):
                out.append({"id": f"theme-{g}-{stat}.{i:02d}", "contexte": f"theme_{g}@{stat}",
                            "texte": {"fr": str(texte)}, "reference": not isinstance(texte, sans)})
    return out


def expressions():
    return {f"theme_{g}@{stat}": EXPRESSIONS[g] for stat, groupes in LIGNES.items() for g in groupes}
