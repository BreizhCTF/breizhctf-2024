
_Vous voici rendu à la troisième mission de notre chevalier. Pour celle-ci, Galahad doit rejoindre la plateforme située au bout du légendaire Pont de l'épée. Mais n'imaginez pas qu'un sort de téléportation suffira, il est nécessaire que Galahad marche sur le pont, sinon le secret ne vous sera pas dévoilé._

# Introduction

Il est important de préciser que la solution ici présentée n'est pas la seule susceptible de fonctionner.

# I - Analyse de l'objectif

Après avoir un peu visité le village, vous êtes sans doute sur ce pont peu accueillant en forme d'épée. Votre objectif est de le traverser pour atteindre la plateforme située à la pointe de l'épée.

![](wu_images/Screenshot%202024-05-12%20001603.png)

Oui mais une épée c'est aiguisé et votre personnage perd de la vie lorsqu'il se déplace sur la lame. Pire, plus il marche loin sur la lame, plus sa vie chute rapidement rendant la traversée impossible.

![](wu_images/Screenshot%202024-05-12%20001630.png)

# II - Scanning mémoire

La première étape consiste à retrouver la variable codant la vie de notre personnage. Pour cela, je vous invite à lire le write-up précédant sur la quête `Age of Fire` de Galahad mais retenez simplement qu'il s'agit de la valeur codée sur un octet et visible en haut à gauche de votre écran.

![](wu_images/Screenshot%202024-05-12%20001809.png)

Une fois la variable de santé dans votre liste, analysez les instructions assembleur modifiant cette variable via l'option `Find out what writes to this address`.

![](wu_images/Screenshot%202024-05-12%20001846.png)

Une interface s'ouvre. Marchez sur le pont pour perdre de la vie puis revenez la consulter.

![](wu_images/Screenshot%202024-05-12%20001921.png)

Une instruction assembleur a édité à deux reprises notre variable de santé. Marchons plus loin sur l'épée jusqu'à provoquer la mort de notre personnage.

![](wu_images/Screenshot%202024-05-12%20001946.png)

On remarque qu'un second bout de code assembleur a modifié le niveau de santé de notre personnage. Cliquez sur `Stop` pour mettre fin à l'analyse (qui peut ralentir l'exécution du jeu).

# III - Rétro-ingénierie Unity

Ouvrez `Assembly-CSharp.dll` dans un outil d'analyse `.NET` comme `DNSpy` (si vous vous demandez pourquoi référez-vous au write-up d'`Age of Fire`). Rendez-vous à l'attribut `health` de la classe `PlayerController` et analysez cette variable pour trouver ses références.

![](wu_images/Screenshot%202024-05-12%20002116.png)

Nous constatons deux fonctions accédant à `health` en écriture. La seconde est juste son initialisation à 255 par la classe.

![](wu_images/Screenshot%202024-05-12%20002146.png)

La première provient quant à elle de la méthode `FixedUpdate` appelée à un taux d'affichage constant par le moteur de jeu Unity sur chaque objet. Rendons-nous dans cette fonction.

![](wu_images/Screenshot%202024-05-12%20002305.png)

On peut comprendre dans cet extrait de code qu'un timer nommé `sword_timer` est déclenché lorsque le joueur entre dans certaines coordonnées (celles de la lame de l'épée). Lorsque le time arrive à 0, la variable `health` se voit retirer un certain nombre (proportionnel à la distance) si cela laisse la variable positive. Sinon, elle est mise à nul, et le joueur est téléporté au spawn (`this.transform.position = ...`). Voilà donc nos deux écritures de `health` !

# IV - Analyse assembleur

Une idée nous vient alors, et si on se débrouillait pour toujours rentrer dans le second cas, celui qui ne téléporte pas le joueur mais descend juste le niveau de vie. Il doit juste s'agit d'une instruction de saut à remplacer en théorie non ? Pour le savoir, depuis l'interface listant les accès en écriture de Cheat Engine, cliquez sur le second (vie nulle), et appuyez sur le bouton `Show disassembler`.

![](wu_images/Screenshot%202024-05-12%20002353.png)

Vous voici dans l'interface de Cheat Engine permettant de désassembler les instructions du programme. Surlignée en bleu, l'instruction précise qui réécrit votre niveau de santé lorsqu'elle est nulle. Remontez légèrement dans le code assembleur jusqu'à trouver une instruction de comparaison.

![](wu_images/Screenshot%202024-05-12%20002419.png)

Tiens, tiens, une instruction `test eax, eax` suivie d'un `jg` (jump if greater). Il s'agit donc de vérifier si `eax` est supérieur à 0. C'est sans doute la condition qui nous intéresse.

# Résolution

Nous voulons que notre condition soit toujours vraie alors remplaçons le `jg` par un `jmp`. Pour cela, double-cliquez sur l'instruction.

![](wu_images/Screenshot%202024-05-12%20002510.png)

Puis retournez dans le jeu.

![](wu_images/Screenshot%202024-05-12%20002549.png)

Voilà vous pouvez marcher aussi loin que vous le souhaitez sur l'épée, votre vie passera son temps à descendre à 0 puis à revenir à 255 sans causer le moindre problème. Et une fois au bout... la récompense !

![](wu_images/Screenshot%202024-05-12%20002612.png)

Le flag est donc `BZHCTF{lancelot_crossed_this_bridge_before_you_did}`

# Conclusion

L'objectif de ce challenge était de faire découvrir des bases de rétro-ingénierie Unity, et d'introduire la notion de patching assembleur dans Cheat Engine aux joueurs ne la maîtrisant pas.
