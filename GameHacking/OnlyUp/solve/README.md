_Aidez Galahad, le plus jeune chevalier de la Table ronde à mener sa quête au travers de différentes missions. Pour le premier de ses 4 travaux, le fils de Lancelot du Lac doit se hisser sur la tour la plus haute du village. Seulement, malgré une capacité de saut défiant les lois de la physique, la tour semble bien inaccessible. À moins que..._

# Introduction

Il est important de préciser que la solution ici présentée n'est pas la seule susceptible de fonctionner.

# I - Analyse de l'objectif

Après avoir ouvert le jeu, on découvrer un univers composé d'un petit village, et d'une grande épée formant un pont vers une petite plateforme lointaine. Nous contrôlons un personnage à la troisième personne que l'on peut diriger avec ZQSD et la barre d'espace pour sauter.

![](wu_images/Screenshot%202024-05-11%20234811.png)

Notre objectif ici est d'atteindre la plus haute tour du village. Après une courte période d'observation, nous l'identifions.

![](wu_images/Screenshot%202024-05-11%20234938.png)

Seulement voilà, impossible de sauter à sa hauteur, elle est trop haute... Si seulement il était possible de se téléporter là-haut...

# II - Scanning mémoire

Utilisons Cheat Engine pour scanner la mémoire de notre processus.

![](wu_images/Screenshot%202024-05-11%20235034.png)

Il s'agit d'un logiciel avec de nombreuses fonctionnalités, une boîte à outils facile à prendre en main et primordiale quand on s'intéresse au Game Hacking. Attachons-nous au process "Galahad Quest.exe".  
Notre objectif ici va être de trouver la variable contenant la coordonnée `Y` (hauteur) de notre personnage pour la modifier en live. Pour cela, nous allons établir des scans successifs sur l'ensemble de la mémoire RAM du jeu en filtrant les valeurs lors de chaque scan. Pour cela, il nous faut connaître le type de variable de notre coordonnée `Y`. Bien souvent il s'agit d'un nombre flottant (`float` sur 4 octets ou `double` sur 8 octets), nous commencerons par `float`.

![](wu_images/Screenshot%202024-05-11%20235141.png)

Nous ne connaissons pas la valeur initiale de `Y` donc nous acceptons toutes les valeurs lors du premier scan (remplissage de la base).

![](wu_images/Screenshot%202024-05-11%20235243.png)

Nous obtenons plus de 2 millions de résultats. C'est évidemment beaucoup trop. Vient alors un dilemme, considérons-nous que `Y` augmente ou diminue lorsque nous prenons de l'altitude. Comme pour le premier choix, c'est du 1 chance sur 2, nous commencerons par considérer qu'il augmente. Dans notre deuxième scan, nous descendons notre personnage d'un étage dans le jeu puis indiquons que notre variable a diminué.

![](wu_images/Screenshot%202024-05-11%20235347.png)

Nous enchaînons ensuite les scans en indiquant tantôt que notre variable augmente, diminue, reste la même... jusqu'à arriver à environ 300 résultats. À ce niveau, rien ne sert de filtrer davantage avec des scans car presque toutes les variables continueront d'évoluer dans le même sens. Pourtant, seule une code réellement la hauteur de notre personnage. Nous allons donc ajouter la moitié des variables à notre liste et progresser par dichotomie.

![](wu_images/Screenshot%202024-05-11%20235628.png)

Une fois la moitié des variables ajoutées à la liste, on effectue un `CTRL+A` pour toutes les sélectionner puis on appuie sur la barre d'espace pour les "cocher". En cochant une variable, Cheat Engine va la réécrire en permanance avec sa valeur au moment du cochage ce qui a pour effet de la geler. Nous pouvons alors observer dans le jeu si notre personnage peut encore sauter normalement ou non. S'il peut sauter normalement, c'est que `Y` appartient à la moitié de la liste que nous n'avons pas ajoutée. Sinon c'est bien dans cette partie.

![](wu_images/Screenshot%202024-05-11%20235708.png)

Nous pouvons alors avec cette technique réduire de moitié nos listes tour à tour en supprimant la moitié de notre liste qui n'a aucun effet sur `Y`.

![](wu_images/Screenshot%202024-05-11%20235738.png)

Au bout d'un certain nombre d'itérations, nous isolons la variable requise.

![](wu_images/Screenshot%202024-05-12%20000020.png)

# III - Résolution

Plaçons nous alors à côté de la plus haute tour et modifions cette variable à 50.

![](wu_images/Screenshot%202024-05-12%20000203.png)

Notre personnage effectue un bond dans les airs et en contrôlant sa chute nous atterrissons en haut de la tour où se trouve le flag (déchiffré à la volée).

![](wu_images/Screenshot%202024-05-12%20000246.png)

Le flag est donc `BZHCTF{on_top_of_the_world}`

# Conclusion

Ce challenge était une petite mise en bouche permettant aux participants novices de prendre en main le scanning mémoire sans nécessiter de compétences / connaissances particulières.
