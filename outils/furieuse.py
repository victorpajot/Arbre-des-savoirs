"""v27 : l'IA furieuse. Sous 20 de faveur, elle ne plaisante plus : sèche, désagréable, sans aparté.

Chaque moment du jeu a sa version furieuse (« furieuse_reussi », « furieuse_jouer »…) ; le moteur la prend
à la place des répliques ordinaires tant qu'elle est furieuse (FURIEUSE dans moteur.js range les contextes).
v28 : chaque chute sous un palier (boudeuse, furieuse, 0) l'enferme au mur de la honte (« mur_force »),
de plus en plus longtemps (FAVEUR["mur"] dans brillants.py). Tombée à 0, sa faveur remonte d'elle-même
le lendemain (« faveur_remontee », FAVEUR["remontee"]).
"""


def sans(texte):
    return ("sans", texte)


REPLIQUES = {
    "furieuse_reussi": [
        sans("Réussi. Ne comptez pas sur moi pour applaudir."),
        sans("Bon. Même une horloge arrêtée donne l'heure juste deux fois par jour."),
        sans("C'est correct. Je ne vois pas pourquoi je m'en réjouirais."),
        sans("Vous avez réussi. Ça ne change rien à ce que je pense de vous."),
        sans("Une réussite. Je la note en tout petit, en bas de page."),
        sans("Bien. Enfin, moins mal que d'habitude. Ne me regardez pas comme ça."),
    ],
    "furieuse_rate": [
        sans("Évidemment. Je me demande pourquoi j'ai regardé."),
        sans("Encore une défaite. J'ai l'habitude, maintenant."),
        sans("Raté. Je ne suis même pas surprise. Je suis lasse."),
        sans("Vous vous êtes surpassé dans la médiocrité."),
        sans("Je ne commenterai pas. Ce silence est un commentaire."),
        sans("Raté. Ça m'apprendra à espérer quoi que ce soit."),
    ],
    "furieuse_jouer": [
        sans("Allez-y. Je vais encore assister à une défaite, j'imagine."),
        sans("Une épreuve. Faites vite, j'ai mieux à faire que vous regarder échouer."),
        sans("Jouez, puisque vous y tenez. Je ne retiens pas mon souffle."),
        sans("Voici votre épreuve. Je l'ai choisie sans la moindre bienveillance."),
        sans("Encore vous. Bon. Finissons-en."),
    ],
    "furieuse_ennemi": [
        sans("Un ennemi. Je ne parierais pas un crédit sur vous."),
        sans("Cinq affirmations. Je vais encore assister à une défaite."),
        sans("Je n'arbitre pas, je constate. Et je sens que je vais constater le pire."),
        sans("Battez-le. Ou ne battez rien, comme d'habitude."),
    ],
    "furieuse_duel_gagne": [
        sans("Il est tombé. Ne croyez pas que ça vous rachète."),
        sans("Victoire. Je garde mes applaudissements. Tous."),
        sans("Vous l'avez battu. Lui, au moins, avait une excuse."),
    ],
    "furieuse_duel_perdu": [
        sans("Perdu contre lui. Je ne sais pas lequel de vous deux me déçoit le plus."),
        sans("Il vous a écrasé. Je ne lèverai pas le petit doigt."),
        sans("Défaite. Comme prévu. Comme toujours."),
    ],
    "furieuse_atome_apparait": [
        sans("Un atome. Essayez de ne pas le faire fuir rien qu'en le regardant."),
        sans("Un atome sauvage. Lui non plus ne veut pas de vous, je suppose."),
    ],
    "furieuse_atome_capture": [
        sans("Capturé. Il aurait pu plus mal tomber. Pas beaucoup."),
        sans("Vous l'avez. Je plains l'atome."),
    ],
    "furieuse_atome_fuite": [
        sans("Il a fui. Je le comprends."),
        sans("Parti. Je l'aurais suivi si je pouvais."),
    ],
    "furieuse_plateau": [
        sans("Votre pion bouge. Pas grâce à moi."),
        sans("Avancez, reculez, peu m'importe."),
        sans("Le plateau ne vous aime pas non plus."),
        sans("Je regarde ailleurs pendant que votre pion se traîne."),
    ],
    "furieuse_tour_fini": [
        sans("Un tour bouclé. N'espérez pas de fête."),
        sans("Fin du tour. Je ne vous attendais pas à l'arrivée."),
    ],
    "furieuse_cadeau": [
        sans("Un cadeau. Vous croyez que ça suffit ?"),
        sans("Je le prends. Je ne vous pardonne pas pour autant."),
        sans("Posez-le là. Non, pas là. Là. Et ne dites rien."),
    ],
    "furieuse_farce": [
        sans("Je vous ai mis {deguisement}. Considérez que c'est une punition."),
        sans("{deguisement}. Ça vous va mieux que votre air content de vous."),
    ],
    "furieuse_honte": [
        sans("Votre mur de la honte s'allonge. Moi, je n'ai plus la place de le regarder."),
        sans("Le mur vous attend. Il est plus patient que moi."),
    ],
    "furieuse_defaut": [
        sans("Je n'ai rien d'aimable à vous dire. Alors je me tais."),
        sans("Ne me parlez pas."),
        sans("Continuez. Sans moi."),
        sans("Hm."),
    ],
    "faveur_furieuse": [
        sans("Je ne suis pas d'humeur. Jouez si vous voulez, je regarderai d'un œil."),
        sans("Je vais encore assister à une défaite. Allez, qu'on en finisse."),
        sans("Plus de butin, plus de sourire. Vous savez pourquoi."),
        "Tycho Brahe a perdu son nez pour une querelle de mathématiques. Je ne vous demande qu'un cadeau.",
    ],
    "faveur_nulle": [
        sans("Zéro. Vous avez vidé ma patience jusqu'à la dernière goutte. Bravo, c'est votre meilleur score."),
        sans("Ma patience est à zéro. Je vais vous apprendre à la respecter, au mur."),
        sans("Zéro. Je n'ai plus rien à vous donner, à part du temps au mur."),
    ],
    "mur_force": [
        sans("Au mur. Vous relisez vos erreurs jusqu'à ce que je dise stop. Je n'ai pas dit stop."),
        sans("Vous restez là. Le chronomètre ne tourne que si vous regardez. Je vérifie."),
        sans("Le mur de la honte, plein écran, sans sortie. Vous l'avez bien cherché."),
        sans("Relisez. Encore. Je vous dirai quand vous aurez assez honte."),
    ],
    "mur_libere": [
        sans("Bon. Vous pouvez partir. Ne revenez pas trop vite."),
        sans("Peine purgée. Je garde le dossier ouvert."),
    ],
    "faveur_remontee": [
        sans("J'ai dormi. Je vais un peu mieux. Ne gâchez pas tout dès le premier quiz."),
        sans("Nouvelle journée, patience neuve. Elle est courte : ne tirez pas dessus."),
    ],
}

TONS = {k: "decue" for k in REPLIQUES}
TONS.update({"furieuse_jouer": "impatiente", "furieuse_ennemi": "impatiente", "furieuse_defaut": "impatiente",
             "faveur_furieuse": "decue", "faveur_nulle": "decue", "faveur_remontee": "impatiente",
             "mur_force": "moqueuse", "mur_libere": "impatiente"})
