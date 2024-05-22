from game import Game

import easygui as eg

choix = eg.buttonbox("""Le but du jeu est de marquer toutes les cases de la map qui contiennent des bombes, en évitant de cliquer sur l’une d’entre elles.

Déroulement du jeu :
-	Le jeu se déroule sur une grille de cases.
-	Chaque case peut soit contenir une bombe, soit être vide.
-	Au début du jeu, toutes les cases sont cachées.
-	Le joueur peut cliquer, avec le clic gauche, sur une case pour la révéler (la première n’aura jamais de bombe peu importe où vous cliquez).
-	Si la case révélée contient une bombe, le joueur perd la partie.
-	Si la case révélée est vide, elle affiche le nombre de bombes voisines. Si aucune bombe n'est voisine, toutes les cases voisines sont révélées automatiquement.
-	Pour marquer une case qu'il pense contenir une bombe, le joueur peut, avec un clic droit, la flagger. Cela l'empêche de plus de cliquer accidentellement sur cette case.
-	Le jeu se termine lorsque toutes les bombe sont flaggées, auquel cas le joueur gagne, ou lorsqu'une bombe est révélée, auquel cas le joueur perd.""", 
                     "Objectif", ["Ok", "Conseils"])

if choix == "Conseils":
    eg.buttonbox("""-	Utilisez les chiffres révélés pour déduire l'emplacement des bombes.
-	Marquez les cases suspectes avec un drapeau pour éviter les clics accidentels.
-	Soyez prudents et stratégiques dans vos choix de cases à révéler.
-	Si vous n’êtes vraiment pas patient, j’ai glissé un petit outil de triche dedans, en faisant ctrl + S, les bombes apparaitront sur la map le temps que vous maintenez les boutons mais utilisez cela avec modération !
-	Si vous cliquez sur une case pour laquelle vous avez déjà flaggé le bon nombre de voisins, les cases restantes seront automatiquement révélées mais utilisez cela avec précaution car en cas de drapeau mal placé, cela révélera une bombe et vous perdrez.
""", "Conseils", ["Ok !"])
  
board = Game(20, 20, 60)
board.run()
