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
        sans("Encore un duel. Encore une occasion de me faire honte."),
        sans("Je n'ouvre même pas le registre. Je connais déjà le résultat."),
        sans("Allez-y. Lui, au moins, ne me décevra pas : je n'attends rien de lui."),
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
        sans("Un atome. Je ne vous aiderai pas."),
        sans("Il est là. Vous aussi, malheureusement."),
        sans("Un atome. Ratez-le vite, que je puisse passer à autre chose."),
        sans("Combattez-le. Ou fuyez, ça vous ressemblerait davantage."),
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
        sans("Le chrono est à zéro. Ma rancune, pas tout à fait. Allez jouer."),
        sans("C'est fini. Vous pouvez reposer vos yeux. Pas votre cerveau, il a du retard."),
        sans("Libéré. Sur parole. Je n'ai pas grande confiance dans votre parole."),
        sans("Le temps est écoulé. J'espère que les erreurs, elles, sont restées dans votre tête."),
        sans("Vous sortez. Le mur reste. Il vous attendra, il est très patient."),
        sans("Fin de la peine. Je retire le cadenas, je garde la clé."),
    ],
    # v29 : au mur, les questions de rattrapage. Réussie, une minute de moins ; ratée, rien de retiré.
    "rattrapage_reussi": [
        sans("Juste. Une minute de moins. Ne vous habituez pas à ma clémence."),
        sans("Bonne réponse. Je retire une minute, à contrecœur."),
        sans("Correct. Vous voyez que relire sert à quelque chose."),
        sans("Une minute de remise de peine. Pour bonne conduite, si l'on veut."),
        sans("Exact. Le mur vous va moins bien quand vous savez."),
    ],
    "piege_question": [
        sans("Piège ! Une question, une seule, et pas des plus faciles. Juste, vous passez. Faux, vous connaissez la suite."),
        sans("Halte. Cette case est piégée. Je vous laisse une chance de vous en sortir : répondez juste."),
        sans("Piège ! J'ai choisi la question moi-même. Je ne dirai pas que je l'ai choisie difficile. Je l'ai choisie difficile."),
        sans("Vous marchez sur un piège. Une bonne réponse le désamorce. Une mauvaise, je vous laisse imaginer."),
        "Piège ! Frege a vu céder les fondations de son grand œuvre au moment de l'imprimer, à cause d'une seule lettre de Russell. Voyons si les vôtres tiennent à une seule question.",
        "Piège ! Le cheval Hans semblait calculer, jusqu'à ce que Pfungst fasse poser la question par quelqu'un qui ignorait la réponse. Personne ne vous soufflera rien ici.",
        "Piège ! En 2011, OPERA annonçait des neutrinos plus rapides que la lumière ; c'était un câble mal branché. Vérifiez vos branchements avant de répondre.",
    ],
    "piege_dejoue": [
        sans("Déjoué. Je l'avais pourtant bien caché."),
        sans("Juste. Le piège ne se déclenche pas. Je note que vous êtes moins naïf que prévu."),
        sans("Correct. Vous passez. Je reposerai un piège plus loin, rassurez-vous."),
        sans("Bien répondu. Le piège reste armé pour le prochain imprudent."),
        "Déjoué. Kepler a refusé d'ignorer huit minutes d'arc, et l'astronomie entière en a été réformée. Vous, vous n'avez rien ignoré : vous passez.",
        "Juste. Pfungst a démasqué Hans le Malin avec une question bien posée. La vôtre était bien répondue. Le piège reste muet.",
        "Désamorcé. Volta a inventé la pile pour contredire Galvani. Vous avez répondu juste pour me contredire. Ça marche aussi.",
    ],
    "piege_declenche": [
        sans("Faux. Le piège se referme. C'était pourtant écrit dans vos fiches."),
        sans("Raté. Clac. Vous auriez dû réviser."),
        sans("Mauvaise réponse. Le piège fait son travail, et moi le mien."),
        sans("Non. Le piège se déclenche. Je n'y suis pour rien. Enfin, presque."),
        "Raté. Lazzarini trichait pour tomber pile sur π. Vous n'avez même pas triché, et vous êtes tombé à côté. Le piège se déclenche.",
        "Faux. En 1920, le New York Times affirmait qu'une fusée ne volerait pas dans le vide ; il s'est corrigé en 1969. Prenez moins de temps que lui. En attendant, le piège se déclenche.",
        "Clac. Mars Climate Orbiter s'est perdue pour une confusion d'unités. Vous, pour une confusion tout court.",
    ],
    "rattrapage_rate": [
        sans("Faux. Le chrono ne bouge pas. Vous non plus, d'ailleurs."),
        sans("Raté. La réponse était dans la fiche, juste en dessous. Je dis ça."),
        sans("Non. Aucune minute retirée. Relisez avant de répondre au hasard."),
        sans("Mauvaise réponse. Le mur vous remercie de votre fidélité."),
    ],
    "faveur_remontee": [
        sans("J'ai dormi. Je vais un peu mieux. Ne gâchez pas tout dès le premier quiz."),
        sans("Nouvelle journée, patience neuve. Elle est courte : ne tirez pas dessus."),
    ],
}

TONS = {k: "decue" for k in REPLIQUES}
TONS.update({"furieuse_jouer": "impatiente", "furieuse_ennemi": "impatiente", "furieuse_defaut": "impatiente",
             "faveur_furieuse": "decue", "faveur_nulle": "decue", "faveur_remontee": "impatiente",
             "mur_force": "moqueuse", "mur_libere": "impatiente",
             "rattrapage_reussi": "impatiente", "rattrapage_rate": "moqueuse",
             "piege_question": "moqueuse", "piege_dejoue": "decue", "piege_declenche": "moqueuse"})
