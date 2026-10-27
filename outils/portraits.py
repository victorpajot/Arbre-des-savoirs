"""v15 : portraits des personnes qu'une question fait choisir par leur nom.

Quand la bonne réponse d'un QCM est le nom d'un savant ou d'un penseur, le retour de la question montre
son portrait en pixel art (même gabarit que les savants jouables) et une courte biographie sourcée.
Les savants jouables déjà dessinés servent tels quels ; les autres sont ici.
Quelques personnes citées par les questions n'ont pas de portrait, volontairement (Adolf Eichmann).
"""
import savants
from savants import c

# id, nom (tel qu'il apparaît dans les réponses), années, peau, tenue, couleurs, coiffure, barbe, objet, biographie, source
PORTRAITS = [
    ("quetelet", "Adolphe Quetelet", "1796 / 1874", "claire", "manteau", c("#2F3B59", "#3B3B3B", "#E8E8EE"), ("court", "cheveux", 1), ("favoris", "cheveux", 1), "carnet",
     "Astronome et statisticien belge, il applique la courbe en cloche aux mesures humaines et invente l'« homme moyen ». On lui doit aussi l'indice de masse corporelle, défini pour décrire des populations, pas pour juger une personne.",
     "Adolphe Quetelet, Sur l'homme et le développement de ses facultés, 1835"),
    ("jeffreys", "Alec Jeffreys", "né en 1950", "claire", "blouse", c("#E8E8EE", "#2F3B59", "#3D63D9"), ("court", "gris", 3), None, "photo51",
     "Généticien britannique, il découvre en 1984 l'empreinte génétique en regardant un film de radiographie d'ADN. En 1986, la méthode innocente un suspect et mène au vrai coupable d'un double meurtre.",
     "Alec Jeffreys et al., Nature, 1985"),
    ("volta", "Alessandro Volta", "1745 / 1827", "claire", "manteau", c("#7A5418", "#3B3B3B", "#F2C14E"), ("perruque_courte", "gris", 4), None, "bobine",
     "Physicien italien, il empile en 1800 des disques de zinc et de cuivre séparés de carton imbibé de saumure : la première pile électrique. Il voulait montrer à Galvani que l'électricité ne venait pas des grenouilles.",
     "Alessandro Volta, Philosophical Transactions, 1800"),
    ("wallace", "Alfred Russel Wallace", "1823 / 1913", "claire", "manteau", c("#6B6B3A", "#3B3B3B", "#E8DDC0"), ("court", "gris", 3), ("fleuve", "gris", 3), "carnet",
     "Naturaliste britannique, il conçoit la sélection naturelle en 1858, fiévreux, aux Moluques, et l'écrit à Darwin. Leurs deux textes sont lus ensemble à la Linnean Society de Londres.",
     "Darwin et Wallace, Journal of the Proceedings of the Linnean Society, 1858"),
    ("jung", "Carl Gustav Jung", "1875 / 1961", "claire", "manteau", c("#3B3B3B", "#2B2B33", "#E8E8EE"), ("court", "gris", 3), None, "carnet",
     "Psychiatre suisse, d'abord proche de Freud, il rompt avec lui en 1913. Il propose les notions d'introversion et d'extraversion, et un inconscient collectif peuplé d'archétypes.",
     "Carl Gustav Jung, Types psychologiques, 1921"),
    ("sagan", "Carl Sagan", "1934 / 1996", "claire", "pull", c("#8E2424", "#2F3B59", "#E8DDC0"), ("court", "cheveux", 1), None, "lunette",
     "Astronome américain, il conçoit le disque d'or des sondes Voyager et présente la série Cosmos en 1980. En 1990, il obtient que Voyager 1 se retourne pour photographier la Terre : le « point bleu pâle ».",
     "Carl Sagan, Pale Blue Dot, 1994"),
    ("goleman", "Daniel Goleman", "né en 1946", "claire", "cardigan", c("#5D6470", "#2F3B59", "#E8E8EE"), ("couronne", "gris", 3), None, "carnet",
     "Psychologue et journaliste scientifique américain, il popularise en 1995 l'« intelligence émotionnelle », une notion proposée cinq ans plus tôt par Peter Salovey et John Mayer.",
     "Daniel Goleman, Emotional Intelligence, 1995 ; Salovey et Mayer, 1990"),
    ("kahneman", "Daniel Kahneman", "1934 / 2024", "claire", "cardigan", c("#9A6534", "#2F3B59", "#E8E8EE"), ("couronne", "gris", 3), None, "balance",
     "Psychologue israélo-américain, il étudie avec Amos Tversky les biais du jugement et notre façon de peser gains et pertes. Il reçoit en 2002 le prix d'économie de la Banque de Suède sans avoir jamais suivi de cours d'économie.",
     "Daniel Kahneman, Système 1 / Système 2, 2011"),
    ("fermi", "Enrico Fermi", "1901 / 1954", "claire", "manteau", c("#5D6470", "#3B3B3B", "#E8E8EE"), ("raie", "cheveux", 1), None, "craie",
     "Physicien italien, prix Nobel en 1938, il quitte l'Italie fasciste avec sa femme, qui est juive. À Chicago, il dirige en 1942 la première réaction nucléaire en chaîne contrôlée. Il adorait estimer n'importe quoi de tête.",
     "Laura Fermi, Atoms in the Family, 1954"),
    ("haeckel", "Ernst Haeckel", "1834 / 1919", "claire", "manteau", c("#2E7D32", "#3B3B3B", "#E8DDC0"), ("court", "gris", 3), ("pleine", "gris", 3), "plume",
     "Biologiste allemand, il invente le mot « écologie » en 1866 et dessine des planches d'organismes marins d'une grande beauté. Certains de ses dessins d'embryons, trop arrangés, lui valent des accusations de fraude.",
     "Ernst Haeckel, Generelle Morphologie der Organismen, 1866 ; Kunstformen der Natur, 1904"),
    ("viete", "François Viète", "1540 / 1603", "claire", "robe", c("#1E1A2B", "#3B3B3B", "#E8E8EE"), ("court", "cheveux", 1), ("pleine", "cheveux", 1), "ardoise",
     "Juriste et conseiller d'Henri IV, il note les inconnues par des lettres et invente le calcul littéral. Il casse aussi un chiffre secret espagnol, au point que Philippe II accuse la France de sorcellerie.",
     "François Viète, In artem analyticem isagoge, 1591"),
    ("lemaitre", "Georges Lemaître", "1894 / 1966", "claire", "robe", c("#1E1A2B", "#2B2B33", "#E8E8EE"), ("court", "cheveux", 1), None, "craie",
     "Prêtre et physicien belge, il propose en 1927 que l'Univers est en expansion, puis qu'il est né d'un « atome primitif » : l'idée qui deviendra le Big Bang. Il refusait de mêler sa foi à sa cosmologie.",
     "Georges Lemaître, Annales de la Société scientifique de Bruxelles, 1927"),
    ("lewis", "Gilbert Lewis", "1875 / 1946", "claire", "manteau", c("#3B3B3B", "#2B2B33", "#E8E8EE"), ("court", "cheveux", 1), None, "fiole",
     "Chimiste américain, il propose en 1916 que la liaison chimique est une paire d'électrons partagée, et invente la notation à points qui porte son nom. Proposé des dizaines de fois au Nobel, il ne l'a jamais reçu.",
     "Gilbert Lewis, Journal of the American Chemical Society, 1916"),
    ("mendel", "Gregor Mendel", "1822 / 1884", "claire", "robe", c("#1E1A2B", "#3B3B3B", "#E8E8EE"), ("couronne", "cheveux", 1), None, "carnet",
     "Moine à Brno, il croise pendant huit ans des milliers de pieds de petits pois et en tire les lois de l'hérédité, publiées en 1866. Elles restent ignorées jusqu'en 1900.",
     "Gregor Mendel, Versuche über Pflanzen-Hybriden, 1866"),
    ("freudenberger", "Herbert Freudenberger", "1926 / 1999", "claire", "cardigan", c("#5D6470", "#2F3B59", "#E8E8EE"), ("court", "gris", 3), None, "carnet",
     "Psychologue américain, il décrit en 1974 le « burn-out » chez les bénévoles d'une clinique gratuite de New York, et chez lui-même.",
     "Herbert Freudenberger, Journal of Social Issues, 1974"),
    ("semmelweis", "Ignace Semmelweis", "1818 / 1865", "claire", "blouse", c("#E8E8EE", "#3B3B3B", "#2F3B59"), ("couronne", "cheveux", 1), ("favoris", "cheveux", 1), "fiole",
     "Médecin hongrois à Vienne, il impose en 1847 le lavage des mains au chlore et fait chuter la mortalité des accouchées. Ses collègues le rejettent ; il meurt interné.",
     "Ignace Semmelweis, Die Ätiologie, der Begriff und die Prophylaxis des Kindbettfiebers, 1861"),
    ("hubble", "Edwin Hubble", "1889 / 1953", "claire", "manteau", c("#6E4429", "#3B3B3B", "#E8DDC0"), ("raie", "cheveux", 1), None, "lunette",
     "Astronome américain, il montre en 1924 qu'Andromède est une autre galaxie, puis en 1929 que les galaxies s'éloignent d'autant plus vite qu'elles sont loin. Il s'appuie sur la méthode d'Henrietta Leavitt.",
     "Edwin Hubble, PNAS, 1929"),
    ("kant", "Kant", "1724 / 1804", "claire", "manteau", c("#2F3B59", "#3B3B3B", "#E8E8EE"), ("perruque_courte", "gris", 4), None, "plume",
     "Emmanuel Kant, philosophe de Königsberg, ville qu'il n'a presque jamais quittée. Dans la Critique de la raison pure, il cherche ce que la raison peut connaître. Ses voisins, dit la légende, réglaient leur montre sur sa promenade.",
     "Emmanuel Kant, Critique de la raison pure, 1781"),
    ("marx", "Karl Marx", "1818 / 1883", "claire", "manteau", c("#3B3B3B", "#2B2B33", "#E8E8EE"), ("ebouriffe", "gris", 3), ("fleuve", "gris", 3), "carnet",
     "Philosophe et économiste allemand, il écrit avec Engels le Manifeste du parti communiste en 1848, puis Le Capital, préparé pendant des années à la salle de lecture du British Museum.",
     "Karl Marx, Le Capital, livre I, 1867"),
    ("popper", "Karl Popper", "1902 / 1994", "claire", "cardigan", c("#5D6470", "#2F3B59", "#E8E8EE"), ("couronne", "gris", 3), None, "carnet",
     "Philosophe autrichien puis britannique, il soutient qu'une théorie n'est scientifique que si une observation pourrait la réfuter. Selon lui, l'astrologie et la psychanalyse échouaient à ce test.",
     "Karl Popper, Logik der Forschung, 1934"),
    ("foot", "Philippa Foot", "1920 / 2010", "claire", "cardigan", c("#3E6B48", "#2F3B59", "#E8DDC0"), ("court", "gris", 3), None, "carnet",
     "Philosophe britannique, elle imagine en 1967 le dilemme du tramway pour discuter de la différence entre faire et laisser faire. L'exemple a fini par vivre sa propre vie.",
     "Philippa Foot, Oxford Review, 1967"),
    ("hooke", "Robert Hooke", "1635 / 1703", "claire", "manteau", c("#6E4429", "#3B3B3B", "#E8DDC0"), ("longs", "cheveux", 1), None, "lentille",
     "Savant anglais, il observe le liège au microscope et nomme « cellules » les petites chambres qu'il y voit. Rival de Newton, il n'a laissé aucun portrait authentifié : celui-ci est imaginé.",
     "Robert Hooke, Micrographia, 1665"),
    ("beauvoir", "Simone de Beauvoir", "1908 / 1986", "claire", "robe", c("#8E2424", "#2F3B59", "#E8DDC0"), ("chignon", "cheveux", 0), None, "plume",
     "Philosophe et romancière, elle écrit en 1949 Le Deuxième Sexe : « On ne naît pas femme : on le devient. » Le Vatican met le livre à l'Index.",
     "Simone de Beauvoir, Le Deuxième Sexe, 1949"),
    ("thales", "Thalès de Milet", "vers -625 / vers -547", "claire", "toge", c("#E8DDC0", "#A8905E", "#3D63D9"), ("couronne", "gris", 3), ("pleine", "gris", 3), "astrolabe",
     "Tenu pour le premier philosophe grec, il cherche des causes naturelles plutôt que divines : selon lui, tout vient de l'eau. Hérodote lui attribue la prédiction d'une éclipse en 585 avant notre ère.",
     "Hérodote, Histoires, I, 74 ; Aristote, Métaphysique, A, 3"),
    ("nagel", "Thomas Nagel", "né en 1937", "claire", "cardigan", c("#5D6470", "#2F3B59", "#E8E8EE"), ("couronne", "gris", 3), None, "carnet",
     "Philosophe américain, il demande en 1974 « Quel effet cela fait-il d'être une chauve-souris ? » : la science peut décrire le sonar, pas ce que la chauve-souris ressent.",
     "Thomas Nagel, The Philosophical Review, 1974"),
    ("thucydide", "Thucydide", "vers -460 / vers -400", "claire", "toge", c("#E8DDC0", "#A8905E", "#8E2424"), ("court", "cheveux", 1), ("pleine", "cheveux", 1), "rouleau",
     "Général athénien exilé, il raconte la guerre du Péloponnèse en recoupant les témoins, sans dieux ni présages pour l'expliquer. Il décrit aussi la peste d'Athènes, qu'il a attrapée et à laquelle il a survécu.",
     "Thucydide, La Guerre du Péloponnèse, II, 48"),
    ("leverrier", "Urbain Le Verrier", "1811 / 1877", "claire", "manteau", c("#2F3B59", "#3B3B3B", "#E8E8EE"), ("court", "cheveux", 1), ("favoris", "cheveux", 1), "trajectoire",
     "Astronome français, il calcule en 1846 la position d'une planète inconnue d'après les écarts de l'orbite d'Uranus. Johann Galle la trouve le soir même où il reçoit sa lettre : c'est Neptune.",
     "Urbain Le Verrier, Comptes rendus de l'Académie des sciences, 1846"),
    ("maxwell", "James Clerk Maxwell", "1831 / 1879", "claire", "manteau", c("#3B3B3B", "#2B2B33", "#E8E8EE"), ("court", "cheveux", 1), ("pleine", "cheveux", 1), "bobine",
     "Physicien écossais, il réunit électricité, magnétisme et lumière dans une même théorie en 1865. Il fait aussi réaliser en 1861 la première photographie en couleurs, celle d'un ruban de tartan.",
     "James Clerk Maxwell, Philosophical Transactions, 1865"),
    ("terechkova", "Valentina Terechkova", "née en 1937", "claire", "pull", c("#E8873A", "#5D6470", "#E8E8EE"), ("court", "cheveux", 1), None, None,
     "Ouvrière du textile et parachutiste amateur, elle devient en 1963 la première femme dans l'espace, à bord de Vostok 6 : 48 orbites en près de trois jours. La deuxième volera dix-neuf ans plus tard.",
     "Agence spatiale européenne, « Valentina Tereshkova »"),
    ("la-boetie", "Étienne de La Boétie", "1530 / 1563", "claire", "robe", c("#1E1A2B", "#3B3B3B", "#E8E8EE"), ("court", "cheveux", 1), ("pleine", "cheveux", 1), "plume",
     "Ami de Montaigne, il écrit très jeune le Discours de la servitude volontaire : un tyran n'a de pouvoir que celui qu'on lui donne. Montaigne dira de leur amitié : « Parce que c'était lui, parce que c'était moi. »",
     "Étienne de La Boétie, Discours de la servitude volontaire ; Montaigne, Essais, I, 28"),
]

SANS_PORTRAIT = {"Adolf Eichmann"}


def donnees():
    out = []
    for p in PORTRAITS:
        id, nom, annees, peau, tenue_, couleurs, coif, barbe_, objet_, bio, source = p
        base, cheveux = savants.savant((id, nom, annees, peau, tenue_, couleurs, coif, barbe_, objet_ or "aucun", None, bio, source))
        out.append({"id": id, "nom": {"fr": nom}, "annees": annees, "bio": {"fr": bio}, "source": source,
                    "couleurs": couleurs, "base": base.lignes(), "cheveux": cheveux.lignes()})
    return out


def par_nom():
    """Nom tel qu'écrit dans les réponses → (famille, id) : un savant jouable ou un portrait."""
    out = {s[1]: ("savant", s[0]) for s in savants.SAVANTS}
    out.update({p[1]: ("portrait", p[0]) for p in PORTRAITS})
    return out
