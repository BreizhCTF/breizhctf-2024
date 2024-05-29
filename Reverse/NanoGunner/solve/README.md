_Le code source du logiciel permettant la mise à feu de projectiles de dernière génération a été perdu par un acte de sabotage interne à nos services. De plus, la clé d'activation que nous possédons semble ne plus fonctionner. Nous nécessitons vos talents en rétro-ingénierie pour en fabriquer une nouvelle et être à même d'effectuer des frappes stratégiques sur les positions ennemies. Quelques notions de physique pourraient vous être nécessaires mais nul doute qu'une intelligence artificielle bien connue saura vous aiguiller sur ce point. Vous aurez sans doute besoin d'installer la bibliothèque libgtkmm-3.0 pour avoir accès à notre interface graphique. Bon courage !_

# Introduction

Il me paraît important de préciser que si je réalise dans ce writeup l'analyse de l'exécutable à l'aide d'un désassembleur uniquement (approche statique), un gain de temps considérable pourrait être obtenu via une analyse dynamique à l'aide d'un débogueur.

# I - Analyse globale

La première chose à noter en ouvrant le binaire dans un désassembleur ou via la commande `file` est l'absence de symboles (stripped) ce qui pourrait rendre plus difficile la phase de reverse.

![](wu_images/Pasted%20image%2020240406122812.png)

Cependant, on remarque également que le binaire est lié dynamiquement (dynamically linked), nous aurons donc accès aux symboles des bibliothèques dans un désassembleur.

## main

En ouvrant le binaire dans un désassembleur (j'utiliserai BinaryNinja), on commence par analyser la fonction `main`.

![](wu_images/Pasted%20image%2020240406123513.png)

J'ai renommé certaines variables de la vue HLIL par commodité. Dans une première partie, on constate des appels à des fonctions issues de l'espace de noms `Gtk` qui opèrent donc sur la partie interface graphique. Lançons donc le programme pour obtenir davantage d'informations sur cette interface graphique :

![](wu_images/Pasted%20image%2020240406123941.png)

Aucune interface graphique n'est affichée, c'est sans doute lié au code que nous venons d'entrer "blabla" qui ne répond pas à certains critères. En continuant l'analyse statique, la fonction `sub_91a6` semble elle-même liée à des initialisations de `Gtk`. Plus loin, le programme demande un code à l'utilisateur. Voyons ce qu'il en fait.

![](wu_images/Pasted%20image%2020240406124640.png)

Tout d'abord, le programme calcule la taille du code entré par l'utilisateur et remplace le caractère de fin de ligne par un caractère nul.
Ensuite, un appel à `malloc` est effectué sur la moitié de la taille de notre code (un shift de 1 vers la droite est équivalent à une division par 2).
Ensuite un appel à la fonction `sub_79c9` est réalisé. Elle prend trois paramètres `user_code`, `user_code_len` et `unk_alloc` l'allocation que nous venons de réaliser. Le retour de cette fonction doit être de 1. Analysons donc `sub_79c9`.

## sub_79c9

Voici le code de `sub_79c9`. J'ai renommé certaines variables par commodité.

![](wu_images/Pasted%20image%2020240406141010.png)

On reconnaît aisément les constantes liées à une conversion ASCII vers hexadécimal. L'allocation du tampon de sortie étant deux fois plus petite, cela vient confirmer cette hypothèse. On imagine donc que cette fonction renvoit 1 (true) si la conversion était possible. Nous renommerons cette fonction `parse_hex`. Plutôt que de déboguer le programme, vérifions déjà si nous avons davantage de chance en entrant une chaîne hexadécimal lorsque le programme nous demande le code.

![](wu_images/Pasted%20image%2020240408214219.png)

En effet, une interface graphique s'ouvre pendant une seconde avant de se refermer. De plus, la mention "Bad shot..." vient remplacer le "Failure..." présent auparavant.

![[Screenshot from 2024-04-08 21-38-29.png)

En observant l'interface graphique, on constate différents paramètres, en l'occurrence `Xi`, `Yi`, `Xt`, `Yt`, `Kinetic Energy`, `Mass` et `Angle`. Avec un peu de déduction, on comprendra que `Xi` et `Yi` correspondent aux coordonnées initiales d'un projectile (disque rouge), `Xt` et `Yt` aux coordonnées de la cible du projectile (carré vert), `Kinetic Energetic` à l'énergie cinétique initiale du projectile, `Mass` à la masse du projectile (ici elle est nulle) et `Angle` à l'angle de tir du projectile. Cela peut être confirmé par une analyse plus poussée que nous ne traiterons pas ici.
Retournons à l'analyse de `main`.

## main

Observons le code lorsque la conversion hexadécimale par `parse_hex` réussit.

![](wu_images/Pasted%20image%2020240408221515.png)

Un coup d'oeil à `sub_c142` nous permet de comprendre qu'elle initialise deux variables globales correspondant aux code rentré par l'utilisateur et à sa taille. Nous renommons tout en conséquence.

![](wu_images/Pasted%20image%2020240408222628.png)

De retour dans `main`, renommons les deux fonctions restantes.

![](wu_images/Pasted%20image%2020240408223256.png)

Laissons de côté la fonction liée à l'interface graphique (`window_func`) et observons celle lancée sur un autre thread `thread_func`.

## thread_func

Cette fonction est particulièrement imposante et peu accueillante.

![](wu_images/Pasted%20image%2020240511205815.png)

Commençons par nous concentrer sur le `memcpy` du début.

![[Screenshot from 2024-05-11 20-53-19.png)

Un reverser ayant déjà rencontré des nombres flottants en reconnaîtra sans doute ici. En utilisant le site https://gregstoll.com/~gregstoll/floattohex/, on constate que les 4 premiers octets codent un 10, tout comme les 4 suivants.

![](wu_images/Pasted%20image%2020240511210035.png)

Ensuite vient un 750. Puis de nouveau un 10. Tiens, tiens, si l'on regarde de nouveau notre interface graphique, on retrouve bien les valeurs des coordonnées initiales du projectile et de la cible.

![](wu_images/Pasted%20image%2020240511210233.png)

Continuons à observer ce qui suit.

![](wu_images/Pasted%20image%2020240511210429.png)

On a donc 50000 puis 1 puis 70. Si l'on retrouve bien l'énergie cinétique et l'angle du projectile, la masse diffère... Intéressant car plus bas on retrouve des indications mentionnant que la masse est en cours de calcul.

![](wu_images/Pasted%20image%2020240511210707.png)

Nous pouvons donc penser que l'élement copié via le `memcpy` depuis la pile n'est autre qu'une structure contenant les paramètres initiaux du tir. Cependant, comme l'élément copié se poursuit après le `float` codant l'angle, peut-être s'agit-il d'un tableau de ladite structure. L'ensemble copié mesure 0x8c=140 octets. Et nous avons identifié 7 paramètres initiaux soit 7\*4 = 28 octets.

![](wu_images/Pasted%20image%2020240511211308.png)

On peut donc partir de l'hypothèse que 5 tirs sont réalisés avec des paramètres initiaux différents. Créons la structure en conséquence et associons un type en conséquence au tableau de la pile.

![](wu_images/Pasted%20image%2020240511211622.png)

![](wu_images/Pasted%20image%2020240511211712.png)

Pour ne pas alourdir davantage l'analyse, gardez en tête que nous allons itérer sur chaque élément de ce tableau dans la boucle qui suit et que la fonction calculant la masse prend en paramètre un élément de ce tableau. Ce résultat est facilement retrouvable par analyse dynamique et n'est pas difficile à deviner. J'ai donc retypé quelques variables.

![](wu_images/Pasted%20image%2020240511212845.png)

Bon, une belle avancée vient d'être réalisée. Nous savons que tous les paramètres sont déterminés à l'avance, sauf la masse qui est calculée à la volée. C'est sans nul doute le seul paramètre que nous contrôlons et l'analyse de la fonction `sub_c1dc` nous le rèvelera.

## sub_c1dc

Vous voici rendu au coeur du problème.

![](wu_images/Pasted%20image%2020240511213551.png)

Tout d'abord, un sémaphore est mis en place.
Ensuite, on constate que 9 variables globales sont initialisées. Les trois premières sont mises à 0 et les 6 suivantes se voient associer les paramètres du tir (sauf la masse). En regardant de plus près les adresses de ces variables, nous constatons que les 7 dernières sont collées et forment un tableau de flottant que nous nommerons `vals`.

![](wu_images/Pasted%20image%2020240511214139.png)

Partons donc avec ces paramètres :

![](wu_images/Pasted%20image%2020240511214247.png)

Ensuite, observons cette boucle.

![](wu_images/Pasted%20image%2020240511214600.png)

La fonction `sub_cc2e` renvoit simplement la taille d'un vecteur C++ dont les éléments sont codés sur 8 octets.

![](wu_images/Pasted%20image%2020240511214810.png)

En effet, les vecteurs possèdent leur adresse de début en première position, suivis de leur adresse de fin et le `>> 3` correspond à une division par `2**3 = 8`. Oui mais le vecteur en question n'a pas l'air très initialisé.

![](wu_images/Pasted%20image%2020240511215313.png)

Dans les programmes C++ il est commun de trouver des fonctions dans la section `.init_array` qui initialisent les objets (dont les vecteurs) au tout début du programme. Regardons les références de `some_int64_vec`.

![](wu_images/Pasted%20image%2020240511215503.png)

La dernière fonction mentionne des appels à `__cta_atexit`, typique des fonctions d'initialisation jetons-y un oeil.

## sub_c7a8

Tiens tiens, on dirait drôlement l'initialisation d'un tableau de fonctions. Une vérification dynamique vous le prouverait, pas la peine de chercher plus loin.

![](wu_images/Pasted%20image%2020240511215648.png)

`some_int64_vec` contient donc 16 fonctions et nous le renommerons `funcs_vec`.

## sub_c1dc

La boucle itère donc 16 fois.

![](wu_images/Pasted%20image%2020240511220231.png)

Et à chaque tour elle crée un processus enfant via un appel à `fork`. Dans le contexte de ce processus enfant `child_pid == 0`, elle invite le parent à s'attacher à lui via l'appel à `ptrace` avec le paramètre `PTRACE_TRACEME`. Puis deux variables globales sur un octet sont initialisées à partir de deux tableaux différents. Retypons les tableaux en conséquence. Nous obtenons :

![](wu_images/Pasted%20image%2020240511220618.png)

Analysons donc la fonction `sub_c768`.

## sub_c768

A première vue, un point d'arrêt est placé et c'est à peu près tout. Il s'agit sans doute pour le processus parent de contrôler le processus enfant (en attendant avec un `wait` ou `waitpid`) lorsque ce point d'arrêt est rencontré (renvoi d'un signal `SIGTRAP`).

![](wu_images/Pasted%20image%2020240511220914.png)

Oui mais s'il y a beaucoup d'octets non-analysés derrière ce point d'arrêt c'est parce que BinaryNinja n'a pas conscience que la fonction continue après ce point d'arrêt. Remplaçons-le par un `NOP` pour voir.

![](wu_images/Pasted%20image%2020240511221048.png)

Tiens tiens c'est plus intéressant ! Et un deuxième point d'arrêt apparaît. Remplaçons-le lui aussi.

![](wu_images/Pasted%20image%2020240511221141.png)

Oh la jolie boucle `while`. On constate que si la valeur de `global_user_code` à l'indice `unk_val1` est égale à la valeur de `child_var2`, le booléen `unk_val2` est mis à vrai. Renommons tout ça.

![](wu_images/Pasted%20image%2020240511221645.png)

N'oublions pas l'existence de points d'arrêt que nous avons remplacés.

## sub_c1dc

De retour dans `sub_c1dc`, observons la dernière fonctions de la boucle, dans le contexte du parent.

![](wu_images/Pasted%20image%2020240511221921.png)

Elle prend en paramètres un pointeur vers une variable `var_38` et un pointeur vers le pid `child_pid` de notre nouvel enfant. Ne soyons pas naïfs, `var_38` est un vecteur avec l'ensemble des pids et `sub_cc56` est une fonction pour ajouter des éléments dans ce vecteur. C'est plus clair ainsi :

![](wu_images/Pasted%20image%2020240511222232.png)

Observons la boucle qui suit :

![](wu_images/Pasted%20image%2020240511222408.png)

Encore une fois, on itère 16 fois et on définit un sighandler via la fonction `signal`. Ainsi pour chaque numéro de signal contenu dans `arr1`, si ce signal est déclenché, le programme exécutera `sub_c170`. Renommons le tout en conséquence.

![](wu_images/Pasted%20image%2020240511222607.png)

Nous pouvons également renommer la variable `child_var1` du contexte de l'enfant comme suit :

![](wu_images/Pasted%20image%2020240511222721.png)

Il est intéressant de constater que chaque enfant a un signal `child_signal` et un trigger `child_trigger` qui lui est associé.
Penchons-nous sur ce sighandler.

## sighandler

Voici son code.

![](wu_images/Pasted%20image%2020240511222923.png)

Tout d'abord constatons que certaines valeurs de signaux sont remplacées. En l'occurence, un signal 0x12 codera un signal 9 et un signal 0x15 codera un signal 3. Cela est dû au fait que le signal 3 est un `SIGQUIT` et le signal 9 un `SIGKILL` et que ces signaux provoquent la mort d'un processus. Ensuite, on imagine que la fonction `sub_cb24` permet de récupérer un élément dans un vecteur 64 bits et l'on récupère donc la fonction à l'indice `signal_n - 1` dans `funcs_vec`. Puis on incrémente l'indice `global_user_code_idx` et on libère le sémaphore (qui a été activé auparavant mais on ne sait pas encore où).

## sub_c1dc

Voici le coeur de la bête.

![](wu_images/Pasted%20image%2020240511223634.png)

Dans cette grande boucle, on itère sur le code rentré par l'utilisateur.

![](wu_images/Pasted%20image%2020240511223817.png)

Au début, on remarque que `rbx_3` pointe sur l'octet courant. Et si l'on imagine que `sub_cce7` renvoit la fin du vecteur `triggers` et `sub_ccd5` son début il devient aisé de comprendre que `sub_ccfd` est la fonction standard `find` qui permet de savoir si un élément est contenu dans un tableau. Ceci peut être démontré par une analyse plus poussée. Ici, on regarde donc si l'octet courant dans la chaîne saisie par l'utilisateur est contenue dans le vecteur `triggers`.

![](wu_images/Pasted%20image%2020240511224351.png)

Si ce n'est pas le cas, on incrémente l'indice du code. En revanche si l'octet est contenu dans la liste de triggers, on itère sur l'ensemble des pids.

![](wu_images/Pasted%20image%2020240511224632.png)

Pour chaque pid d'enfant, on appelle `waitpid` pour attendre le prochain signal. En l'occurence étant donné la logique de l'enfant, on attend de taper le prochain point d'arrêt.

![](wu_images/Pasted%20image%2020240511224838.png)

Lorsqu'il est atteint, le parent observe le signal renvoyé et s'assure qu'il s'agit d'un point d'arrêt. La condition sur le `stat_loc` est équivalente à `WIFSTOPPED(stat_loc) && WSTOPSIG(stat_loc) == SIGTRAP`. Ensuite, via `PEEK_DATA` et `POKE_DATA`, le parent lit le mot de 8 octets à l'adresse de `global_user_code_idx` et y écrit son propre `global_user_code_idx` pour synchroniser l'enfant sur la même partie du code de l'utilisateur. Puis il demande à l'enfant de continuer son exécution jusqu'au prochain point d'arrêt.
Notons que l'enfant va à ce moment précis regarder si le code à l'indice qui vient de lui être transmis par son parent correspond à son `trigger`.

![](wu_images/Pasted%20image%2020240511225502.png)

Si c'est le cas, il mettera son booléen `triggered` à vrai. Dans la suite du parent, un second `waitpid` attend que le point d'arrêt situé après l'assignation du booléen `triggered` de l'enfant ait été réalisée.

![](wu_images/Pasted%20image%2020240511225707.png)

Le parent vient ensuite récupérer l'état de `triggered` dans l'enfant via `PTRACE_PEEKDATA`. S'il est à vrai, le signal de l'enfant est lu puis lancé via `kill` sur le `pid` du parent.

![](wu_images/Pasted%20image%2020240511225845.png)

Le sémaphore est activé via `sem_wait` et sera désactivé à la fin du sighandler comme vu précédemment pour éviter la concurrence. Ensuite, l'enfant est redémarré.
Nous venons donc de comprendre comment fonctionne la chaîne rentrée par l'utilisateur. Elle doit être composée d'éléments du vecteur `triggers` en sachant que chaque trigger est associé à un signal via la logique des enfants. De même, chaque signal est associé à une fonction. Nous comprenons doucement que nous avons affaire à une machine virtuelle (VM) et notre chaîne hexadécimale en forme les instructions (bytecode).
Regardons la fin de la fonction.

![](wu_images/Pasted%20image%2020240511230509.png)

Après la destruction du sémaphore, l'ensemble des enfants sont tués via leur pid. Ensuite, le registre `zmm0` se voit affecter `vals[0]`. Pourquoi cela, parce qu'en réalité le type de retour de notre fonction est un `float` et qu'il est contenu dans `xmm0`. Nous pouvons donc en déduire qu'à la fin de la fonction, la masse calculée doit se retrouver dans `vals[0]` ou plutôt dans `regs[0]`, car nous nous plaçons désormais dans le contexte d'une VM et renommerons ce tableau en conséquence. De même, `global_user_code` devient `bytecode`, `global_user_code_len` devient `bytecode_len`, `global_user_code_idx` devient `pc` et `funcs_vec` devient `instrs`. Examinons donc les instructions de notre VM à savoir les fonctions dans `instrs`.

## sub_b28e

Voici notre première instruction.

![](wu_images/Pasted%20image%2020240511231316.png)

Elle commence par vérifier qu'au moins deux octets d'opérandes sont disponibles dans le bytecode à la suite de notre opcode (`trigger`) et que la valeur du premier opérande est inférieure ou égale à 6 ce qui n'est pas sans rappeler nos 7 registres. Si tel est le cas, on associe la valeur du deuxième opérande au registre à l'indice correspondant au premier opérande. Puis `pc` est incrémenté de 2. Il s'agit simplement d'un `movabs`, une instruction permettant d'assigner une valeur constante à un registre.

# II - Compréhension profonde de la VM

On donne par souci de temps (et car ce n'est pas difficile à comprendre) la liste de l'ensemble des instructions dans l'ordre de rangement de `instrs` :
- `movabs`
- `mov`
- `mov_gravity_const` (9.81)
- `mov_pi_const` (3.14159)
- `addabs`
- `subabs`
- `mulabs`
- `divabs`
- `add`
- `sub`
- `mul`
- `div`
- `square`
- `sqrt`
- `cos`
- `sin`  
Oui oui on va pouvoir en faire de la trigonométrie avec tout ça. Mais d'abord, il nous faut trouver la correspondance entre une instruction et son trigger. Tout d'abord, via le tableau `signals` et en appliquant la modification des deux signaux dans `sighandler`, on établit la correpondance des instructions en fonction de l'enfant.
- Enfant 1 : Signal 2 : `mov`
- Enfant 2 : Signal 1 : `movabs`
- Enfant 3 : Signal 15 : `cos`
- Enfant 4 : Signal 13 : `square`
- Enfant 5 : Signal 10 : `sub`
- Enfant 6 : Signal 8 : `divabs`
- Enfant 7 : Signal 5 : `addabs`
- Enfant 8 : Signal 4 : `mov_pi_const`
- Enfant 9 : Signal 7 : `mulabs`
- Enfant 10 : Signal 3 : `mov_gravity_const`
- Enfant 11 : Signal 11 : `mul`
- Enfant 12 : Signal 12 : `div`
- Enfant 13 : Signal 6 : `subabs`
- Enfant 14 : Signal 16 : `sin`
- Enfant 15 : Signal 14 : `sqrt`
- Enfant 16 : Signal 9 : `add`  
Puis on fait de même pour la correspondance des triggers (opcodes) en fonction de l'enfant.
- Enfant 1 : `8b`
- Enfant 2 : `6c`
- Enfant 3 : `51`
- Enfant 4 : `36`
- Enfant 5 : `39`
- Enfant 6 : `72`
- Enfant 7 : `f5`
- Enfant 8 : `bd`
- Enfant 9 : `55`
- Enfant 10 : `69`
- Enfant 11 : `10`
- Enfant 12 : `77`
- Enfant 13 : `01`
- Enfant 14 : `12`
- Enfant 15 : `ac`
- Enfant 16 : `48`  
Et on obtient donc la liste des instructions en fonction de l'opcode :
- `8b` : `mov`
- `6c` : `movabs`
- `51` : `cos`
- `36` : `square`
- `39` : `sub`
- `72` : `divabs`
- `f5` : `addabs`
- `bd` : `mov_pi_const`
- `55` : `mulabs`
- `69` : `mov_gravity_const`
- `10` : `mul`
- `77` : `div`
- `01` : `subabs`
- `12` : `sin`
- `ac` : `sqrt`
- `48` : `add`  
Testons cela en mettant la valeur de pi dans le registre 0 (masse). Il faudra donc exécuter `bd00`.

![](wu_images/Pasted%20image%2020240511234516.png)

Parfait !

# Résolution

Nous avons respectivement dans les registres 1 à 6 : `init_x`, `init_y`, `target_x`, `target_y`, `ke` et `angle`. Nous voulons en sortie dans le registre 0 la masse du projectile. Pour cela, un peu de balistique s'impose.
La physique nous apprend que dans un référentiel terrestre supposé galiléen et sans frottement (seule la gravité agit), nous avons les équations temporelles suivantes :
- `x(t) = xi + vxi * t` avec xi l'abscisse initiale du projectile (en m), vxi la composante horizontale de la vitesse initiale (en m.s-1) et t le temps (en s).
- `y(t) = yi + vyi * t - 0.5 * g * (t**2)` avec yi l'ordonnée initiale du projectile (en m), vyi la composante verticale de la vitesse initiale (en m.s-1), g la constante gravitationelle (9.81 m.s-2) et t le temps (en s).  
De plus, on observe que les ordonnées initiales et finales sont toujours égales (yi=yf). Donc la flèche (point le plus haut atteint par un projectile) est située à t/2 dans le domaine temporel. Or c'est également le point où la vitesse verticale est nulle (point de bascule).
Nous avons également l'équation temporelle suivante sur la vitesse verticale.
- `vy(t) ​= vyi​ - gt`
Donc à la flèche, on a :
- `vyi - gt = 0` i.e `t = vyi/g`. Or la flèche est située à la moitié du parcours.
Donc à la fin du parcours on a :
- `t = 2 * (vyi/g)`
On peut donc remplacer dans notre première équation temporelle pour obtenir une équation indépendante du temps :
- `xf = xi + vxi * (vyi/g) * 2` avec xf l'abscisse finale du projectile (en m).
Or on peut décomposer la vitesse initiale en ses composantes comme suit :
- `vxi = vi * cos(θ)` avec θ l'angle de tir en radian.
- `vyi = vi * sin(θ)` avec θ l'angle de tir en radian.
On obtient donc :
- `xf = xi + (2 * (v**2) * cos(θ) * sin(θ)) / g` i.e `xf = xi + ((v**2) * sin(2 * θ)) / g` car `2 * sin(a) * cos(a) = sin(2 * a)`
Puis on exprime la vitesse en fonction de l'énergie cinétique en faisant apparaître la masse :
- `ke = 0.5 * m * (v**2)` d'où `v = sqrt((2 * ke) / m)` avec ke l'énergie cinétique (en J).
On remplace :
- `xf = xi + ((2 * ke)/m * sin(2 * θ)) / g`
Puis :
- `(2 * ke)/m = ((xf - xi) * g) / sin(2 * θ)` i.e `m = (2 * ke) / (((xf - xi) * g) / sin(2 * θ))`
Enfin, on considère θ en degrés :
- `m = (2 * ke) / (((xf - xi) * g) / sin(2 * θ * pi / 180))`
Parfait ! On peut poser cette formule sous forme de bytecode :
- `regs[5] = ke * 2 -> mul(5, 2) -> 550502`
- `regs[3] = xf - xi -> sub(3, 1) -> 390301`
- `regs[0] = g -> mov_gravity_const(0) -> 6900`
- `regs[3] = (xf - xi) * g -> mul(3, 0) -> 100300`
- `regs[0] = pi -> mov_pi_const(0) -> bd00`
- `regs[0] = pi / 90 -> divabs(0, 90) -> 72005a`
- `regs[6] = θ * pi / 90 -> mul(6, 0) -> 100600`1206
- `regs[6] = sin(θ * pi / 90) -> sin(6) -> 1206`
- `regs[3] = ((xf - xi) * g) / sin(θ * pi / 90) -> div(3, 6) -> 770306`
- `regs[5] = (ke * 2) / (((xf - xi) * g) / sin(θ * pi / 90)) -> div(5, 3) -> 770503`
- `regs[0] = (ke * 2) / (((xf - xi) * g) / sin(θ * pi / 90)) -> mov(0, 5) -> 8b0005`
On obtient donc le bytecode `5505023903016900100300bd0072005a10060012067703067705038b0005`.
Essayons-le !

![](wu_images/Pasted%20image%2020240512005350.png)

Les tirs réussissent les uns à la suite des autres ! Regardons le terminal.

![](wu_images/Pasted%20image%2020240512005523.png)

Nous voici en possession du flag : `BZHCTF{art1ll3ry_a1mb0t}`

# Conclusion

Ce challenge était d'une grande difficulté dans le temps imparti pour les participants. Il demande des connaissances en rétro-ingénierie C++, en rétro-ingénierie de VM, en communication parent/enfant, en gestion UNIX des signaux ainsi que des bases en physique. Mais il faut bien départager les plus talentueux.
