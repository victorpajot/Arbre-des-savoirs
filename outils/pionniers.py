"""v7 : succès des pionniers. Au départ, seuls les arbres fondamentaux sont ouverts ;
chaque autre arbre s'ouvre avec le succès qui porte le nom d'un pionnier de sa spécialité."""

from aides import anecdote, citation, succes

FONDAMENTAUX = ["logique", "mecanique", "savoir"]


def pionnier(id, nom, stat, branche, n, recompense):
    s = succes(id, nom, f"Maîtriser {n} compétences. L'arbre {branche} s'ouvre.",
               {"type": "competences_maitrisees", "n": n}, recompense, cache=False)
    s["ouvre"] = stat
    return s


SUCCES = [
    pionnier("pionnier-ciceron", "Cicéron", "eloquence", "de la Rhétorique", 2,
             citation("Ô temps ! Ô mœurs !", "Cicéron", "Première Catilinaire, 63 av. J.-C.")),
    pionnier("pionnier-lavoisier", "Lavoisier", "alchimie", "de la Chimie", 3,
             anecdote("« Rien ne se perd, rien ne se crée, tout se transforme » n'est pas de Lavoisier mot pour mot. Il écrit en 1789 que « rien ne se crée, ni dans les opérations de l'art, ni dans celles de la nature ». La formule bien frappée est venue après lui.",
                      "Antoine Lavoisier, Traité élémentaire de chimie, 1789, chapitre XIII")),
    pionnier("pionnier-galilee", "Galilée", "cosmos", "de l'Astronomie", 4,
             anecdote("« Et pourtant elle tourne » : Galilée ne l'a sans doute jamais murmuré devant ses juges en 1633. La phrase apparaît pour la première fois en 1757, dans un livre de Giuseppe Baretti, plus d'un siècle après le procès.",
                      "Giuseppe Baretti, The Italian Library, Londres, 1757")),
    pionnier("pionnier-bacon", "Francis Bacon", "lucidite", "des Biais cognitifs", 5,
             citation("L'entendement humain, une fois qu'il s'est plu à certaines opinions, y ramène tout le reste pour les appuyer et les confirmer.",
                      "Francis Bacon", "Novum Organum, 1620, livre I, aphorisme 46 (traduction)")),
    pionnier("pionnier-faraday", "Faraday", "etincelle", "de l'Électricité", 6,
             anecdote("En 1825, Michael Faraday lance à la Royal Institution des conférences de Noël pour les enfants. Il en donne lui-même dix-neuf séries. Elles ont lieu chaque année depuis, sauf pendant la Seconde Guerre mondiale.",
                      "Royal Institution, histoire des Christmas Lectures")),
    pionnier("pionnier-william-james", "William James", "empathie", "de la Psychologie", 7,
             citation("L'art d'être sage est l'art de savoir ce qu'il faut négliger.",
                      "William James", "The Principles of Psychology, 1890, chapitre XXII (traduction)")),
    pionnier("pionnier-socrate", "Socrate", "sagesse", "de la Philosophie", 9,
             citation("Une vie sans examen ne vaut pas d'être vécue.", "Socrate", "Platon, Apologie de Socrate, 38a")),
]
