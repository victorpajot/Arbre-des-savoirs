"""v12 : le mur de la honte. Répliques de l'IA et succès liés aux questions ratées."""
from aides import fr


def sans(texte):
    return ("sans", texte)


REPLIQUES = {
    "mur_honte": [
        sans("Vous avez raté des questions aujourd'hui. Je les ai épinglées au mur de la honte, avec des explications. Je suis serviable comme ça."),
        sans("Le mur de la honte s'est enrichi. Il y a des schémas : même vous, vous devriez comprendre."),
        sans("Je tiens un mur, pour vos erreurs. Touchez-moi, je vous y emmène. Prévoyez un mouchoir."),
        "Kepler s'est trompé sur l'orbite de Mars pendant des années, et il l'a raconté dans un livre. Votre mur est plus modeste. Pour l'instant.",
    ],
    "honte_effacee": [
        sans("Bonne réponse. Je retire le clou, mais je garde le trou."),
        sans("Réhabilité. Je raye votre nom du mur. Au crayon à papier."),
        "Ehrlich a testé des centaines de composés avant le 606, le bon. Vous, deux essais. Ne prenez pas la grosse tête.",
    ],
    "honte_ratee": [
        sans("Raté deux fois. J'ajoute un deuxième clou, par symétrie."),
        sans("Même question, même erreur. Au moins, vous êtes constant."),
        "Fermat a laissé une démonstration dans la marge, trop grande pour tenir. Vous, c'est la bonne réponse qui ne tient pas.",
    ],
    "honte_vide": [
        sans("Mur vide aujourd'hui. C'est suspect. Vous avez au moins joué ?"),
        sans("Rien au mur. Je l'ai fait repeindre pour rien."),
    ],
}

TONS = {"mur_honte": "moqueuse", "honte_effacee": "impressionnee", "honte_ratee": "decue", "honte_vide": "moqueuse"}


def succes():
    def s(id, nom, desc, cond, rec):
        return {"id": id, "nom": fr(nom), "description": fr(desc), "condition": cond, "cache": False, "recompense": rec}

    def anec(texte, source):
        return {"type": "anecdote", "texte": fr(texte), "source": source}

    return [
        s("honte-1", "Premier clou", "Rater une première question : elle rejoint le mur de la honte.", {"type": "hontes", "n": 1},
          anec("Le Salvarsan, premier traitement efficace de la syphilis, porte le numéro 606 : Paul Ehrlich et Sahachiro Hata ont testé des centaines de composés avant lui.",
               "Fritz Sörgel, « Paul Ehrlich and the magic bullet », Nature Reviews Drug Discovery, 2004")),
        s("honte-10", "Réhabilité", "Effacer 10 questions du mur de la honte en les réussissant.", {"type": "hontes_effacees", "n": 10},
          anec("Kepler a gardé une erreur de 8 minutes d'arc entre son modèle et les mesures de Tycho Brahe. Plutôt que de l'ignorer, il a abandonné les cercles : « ces huit minutes ont ouvert la voie à une réforme de toute l'astronomie ».",
               "Johannes Kepler, Astronomia nova, 1609, chapitre 19")),
        s("honte-50", "Mur porteur", "Rater 50 questions au total. Le mur tient bon.", {"type": "hontes", "n": 50},
          {"type": "citation", "texte": fr("Déjà essayé. Déjà échoué. Peu importe. Essayer encore. Échouer encore. Échouer mieux."),
           "auteur": "Samuel Beckett", "source": "Worstward Ho, 1983"}),
        s("honte-effacee-50", "Ravalement de façade", "Effacer 50 questions du mur de la honte.", {"type": "hontes_effacees", "n": 50},
          anec("En 1920, le New York Times se moque de Robert Goddard, qui croit qu'une fusée peut voler dans le vide. Le journal publie un rectificatif le 17 juillet 1969, pendant le vol d'Apollo 11.",
               "The New York Times, « A Correction », 17 juillet 1969")),
    ]
