
_Cet étrange programme semble effectuer des opérations incohérentes. Pourtant il semble qu'une unique chaîne de caractères le valide. Le loader et la bibliothèque issus de la glibc permettant l'exécution du binaire sont donnés et ont été associés à l'ELF GotYou._

# Introduction

Il me paraît important de préciser que si je réalise dans ce writeup l'analyse de l'exécutable à l'aide d'un désassembleur uniquement (approche statique), un gain de temps considérable pourrait être obtenu via une analyse dynamique à l'aide d'un débogueur.

# I - Analyse globale

La première chose à noter en ouvrant le binaire dans un désassembleur ou via la commande `file` est l'absence de symboles (stripped) ce qui pourrait rendre plus difficile la phase de reverse.

![](wu_images/Pasted%20image%2020240509200547.png)

Cependant, on remarque également que le binaire est lié dynamiquement (dynamically linked), nous aurons donc accès aux symboles des bibliothèques dans un désassembleur.

## main

En ouvrant le binaire dans un désassembleur (j'utiliserai BinaryNinja), on commence par analyser la fonction `main`.

![](wu_images/Pasted%20image%2020240509213241.png)

Les premières lignes du code source sont peu évocatrices. On constate un appel à la fonction `sub_16d0` avec le paramètre `mprotect` et un ajout de constantes sur la valeur de retour. Nous y reviendrons.
Ensuite, la bannière du challenge est affichée et le mot de passe est demandé à l'utilisateur, d'une taille de 0x14=20 caractères. On rentre alors dans une boucle `while` qui appelle la fonction `sub_1780` avec pour paramètre des noms de fonctions de la libc (`chmod`, `dup2`, `strncmp` et `mallopt`).

![](wu_images/Pasted%20image%2020240509235153.png)

Par la suite, une seconde boucle `while`, imbriquée dans la première et effectuant différents appels à des fonctions de la libc. On remarque déjà que certaines de ces fonctions étaient présentes en paramètre des appels à `sub_1780`, et l'on peut déjà pressentir d'un piège car ces appels les uns à la suite des autres n'ont aucun sens apparent.

![](wu_images/Pasted%20image%2020240509235533.png)

Dans l'ultime partie de la boucle, on remarque la même structure que dans la première partie, au détail près qu'un appel à `getwchar` est effectué. On remarque que le message de succès s'y situe également.
Un vrai casse-tête à première vue. Regardons la fonction `sub_1780` de plus près.

## sub_1780

Voici la fonction.

![](wu_images/Pasted%20image%2020240511122040.png)

On remarque que beaucoup d'opérations se réfèrent à des données globales statiques de la section `.bss` (les données `data_*`). Ici le plus simple serait de déboguer le programme. Mais observons les références à ces adresses.

![](wu_images/Pasted%20image%2020240511122328.png)

La fonction `sub_1200` affecte une valeur à une des variables statiques de la `.bss`. Rendons-nous dans cette fonction.

## sub_1200

Remarquons tout d'abord que cette fonction est référencée dans la section `.init_array` et est à ce titre exécutée par la libc au lancement du programme.

![](wu_images/Pasted%20image%2020240511122624.png)

Voici le contenu de la fonction.

![](wu_images/Pasted%20image%2020240511122507.png)

En deux mots, une itération a lieu sur chaque en-tête de segment (`__elf_program_headers`), et lorsque le segment `.dynamic` est trouvé, une itération est réalisée sur chacune de ses entrées. Et en fonction du type de l'entrée, l'adresse en mémoire associée est écrite dans une des variables statiques de la `.bss`. Ces types d'entrées sont disponibles dans l'enum `e_dyn_tag`.

![](wu_images/Pasted%20image%2020240511124125.png)

On peut donc renommer les variables statiques de la `.bss` en conséquence.

![](wu_images/Pasted%20image%2020240511124731.png)

Pour votre information, j'ai inséré cette fonction pour trouver les adresses de certaines sections, il ne s'agit pas d'une implémentation de la libc.
Revenons donc à `sub_1780`.

## sub_1780

Elle devient déjà bien plus lisible.

![](wu_images/Pasted%20image%2020240511124915.png)

Je me permets ici de renommer / retyper des variables pour faciliter la compréhension.

![](wu_images/Pasted%20image%2020240511131914.png)

Dans une première partie, une itération est réaliser sur les chaînes de caractères de la section typée `strtab` pour y retrouver le nom de notre fonction passée en paramètre. On calcule ensuite le décalage entre le début de la section et le début de la chaîne de caractère retrouvée dans la variable `string_off`. On se sert alors de `string_off` pour retrouver l'entrée de la section typée `symtab` qui définit un symbole à partie de notre nom. Une fois l'entrée retrouvée, on extrait l'indice de l'entrée dans `symtab_off`. Puis, on itère sur les entrées de la section typée `jmp_rel` qui associe un symbole de `symtab` (par son indice) à une adresse (relocation). Nous récupérons alors cette adresse, dans notre cas il s'agit d'une entrée en `.got` puisque nous passons des noms de fonctions de la `libc`.  Il nous manque quelques informations pour comprendre la dernière partie.

![](wu_images/Pasted%20image%2020240511132933.png)

Tout d'abord, l'adresse trouvée dans la `.got` est sommée avec une variable statique que j'avais renommée `unk_val` lors de notre première inspection de `sub_1200` que j'ai renommée `init_dynamic`. Retournons comprendre cela.

## init_dynamic

En effet dans la vue HLIL de BinaryNinja, cette constante semble nulle.

![](wu_images/Pasted%20image%2020240511133338.png)

Mais regardons ce qu'il se passe côté assembleur.

![](wu_images/Pasted%20image%2020240511133426.png)

Une instruction `call $+5` vient appeler l'instruction suivante du programme, mettant également son adresse en première position de la pile. Vient ensuite un `pop rcx` qui récupère donc cette adresse dans le registre `rcx`. Puis une soustraction de 0x1000 est effectuée suivie de l'application d'un masque ne gardant pas les 12 derniers bits de `rcx`. Il s'agit simplement de retrouver l'adresse de chargement de notre programme en mémoire. `unk_val` peut donc être renommée `base_address`.
Revenons à `sub_1780`.

## sub_1780

Nous comprenons donc que l'adresse de base du programme est ajoutée à l'adresse de la `.got` correspondant au nom de la fonction passée en paramètre dans le but de calculer son adresse durant l'exécution du programme car les adresses des relocations sont statiques.

![](wu_images/Pasted%20image%2020240511134258.png)

Par la suite, un `mprotect` est appelé pour rendre la `.got` exécutable et deux valeurs y sont écrites en prenant un décalage sur une variable statique `data_4048`. Regardons ses références.

![](wu_images/Pasted%20image%2020240511134633.png)

Elle est entre autres associée au début de `main`.

## main

Voici le code concerné.

![](wu_images/Pasted%20image%2020240511134735.png)

Un calcul est réalisé avec des décalages sur le résultat d'un appel à `sub_16d0` avec pour paramètre "mprotect".

## sub_16d0

Tiens tiens, cette fonction ressemble drôlement à `sub_1780`.

![](wu_images/Pasted%20image%2020240511134953.png)

Cependant, la partie avec les écritures sur la `.got` n'est pas présente ici. Nous comprenons donc qu'il s'agit simplement de récupérer l'adresse dans la `.got` d'une fonction à partir de son nom. Cette fonction a en fait été optimisée par inlining dans `sub_1780`.

## main

Mais alors pourquoi ces calculs sur l'adresse en `.got` de `mprotect`.

![](wu_images/Pasted%20image%2020240511135304.png)

Un premier déréférencement nous indique que nous récupérons l'adresse de `mprotect` depuis la `.got`. Il s'agit donc de son adresse en libc à laquelle nous ajoutons 0xd6350. Regardons donc dans la libc.

![](wu_images/Pasted%20image%2020240511135612.png)

`mprotect` est en 0xf9cc0, ajoutons-y 0xd6350. Nous arrivons dans une des premières adresses de la `.got` de la libc.

![](wu_images/Pasted%20image%2020240511135742.png)

Regardons ses références.

![](wu_images/Pasted%20image%2020240511135854.png)

Allons à cette fonction.

![](wu_images/Pasted%20image%2020240511140020.png)

Tiens tiens, toutes les fonctions de la `.plt` semblent appeler cette fonction. Et pour cause, c'est celle chargée de résoudre les symboles de la `.got`. Elle appelle donc une fonction du loader pour opérer, `_dl_runtime_resolve_xsavec`. Bien entendu, cela est bien plus facile à trouver par débogage. Mais le dernier calcul de décalage dans `main`, -0x126f0 était une belle indication puisqu'il s'agit de l'adresse de cette fonction dans le loader.

![](wu_images/Pasted%20image%2020240511140501.png)

Ce calcul permet donc en fait de retrouver la base du loader.

![](wu_images/Pasted%20image%2020240511140813.png)

## sub_1780

Nous comprenons donc que nous écrivons au début de la `.got`, des adresses relatives au loader.

![](wu_images/Pasted%20image%2020240511140835.png)

Nous reconnaissons bien la deuxième écriture puisque c'est l'adresse de `_dl_runtime_resolve_xsavec`. Nous ne considérerons pas la première écriture, il s'agit simplement de permettre au loader d'opérer normalement pour résoudre des symboles, alors qu'ils sont normalement déjà résolus.
La ligne qui suit a l'air complexe. Nous écrivons une valeur dans l'adresse de la `.got` de la fonction dont nous passons le nom en paramètre mais quelle est cette valeur. Eh bien le plus simple est de prendre un exemple. Prenons l'entrée `.got` de `mallopt`.

![](wu_images/Pasted%20image%2020240511141352.png)

Son adresse est en 0x3f80.

![](wu_images/Pasted%20image%2020240511143011.png)

Et en 0x1060 se trouve :

![](wu_images/Pasted%20image%2020240511143041.png)

Ce que nous devinons être la fonction de la `.plt` associée à la fonction dont nous passons le nom en paramètre. En fait, il s'agit de remettre la `.got` dans son état initial pour cette fonction dans le but de la résoudre de nouveau. Intéressant.
Renommons `sub_1780` en `unresolve_func`.

## main

Dans la fonction principale du programme, il s'agit donc de résoudre à nouveau certaines fonctions avant de les appeler.

![](wu_images/Pasted%20image%2020240511143501.png)

Ce mécanisme étrange laisse supposer que le loader a été modifié pour résoudre différemment certaines fonctions. Rendez-vous dans le loader.
Une approche intéressante serait de repérer des différences entre un loader normal et cette version modifiée. Personellement j'utiliserai le loader 2.35 de mon Ubuntu 22 pour comparer.

## \_dl\_runtime\_resolve\_xsavec

Jetons un oeil à la fonction de résolution des symboles.

__Version originale__

![](wu_images/Pasted%20image%2020240511144713.png)

__Version modifiée__
![](wu_images/Pasted%20image%2020240511143643.png)

Rien de flagrant ici. Descendons d'un cran.

## \_dl\_fixup

La fonction est trop volumineuse pour que je montre tout ici mais on retrouve globalement les mêmes opérations.

__Version originale__

![](wu_images/Pasted%20image%2020240511145142.png)

__Version modifiée__

![](wu_images/Pasted%20image%2020240511145004.png)

Une fonction au nom évocateur semble néanmoins intéressante.

![](wu_images/Pasted%20image%2020240511145233.png)

## \_dl\_lookup\_symbol\_x

Pas la peine de chercher plus loin, on comprend que quelque chose n'est pas net ici.

![](wu_images/Pasted%20image%2020240511145445.png)

Comme par hasard, les noms des fonctions que nous résolvons de nouveau sont présents ici. Même si certains morceaux sont éparpillés sur la fonction, on peut comprendre que 4 fonctions `strncmp`, `mallopt`, `chmod` et `dup2` voient leur noms remplacés respectivement par `unk_func1`, `unk_func2`, `unk_func3` et `unk_func4` ou par `check_valid` selon si un booléen est vrai ou non. Un booléen différent est associé à chacune des 4 fonctions et il change de valeur a chaque résolution de cette fonction. Ainsi, résoudre `mallopt` reviendra à résoudre `unk_func1` puis `check_valid` puis `unk_func1` (le booléen est faux initialement)...
Enfin, résoudre `ungetc` résoudra toujours `part_check` et `getwchar` résoudra toujours `check_valid`.

![](wu_images/Pasted%20image%2020240511150620.png)

Retrouvons donc les implémentations de `unk_func1`, `unk_func2`, `unk_func_3`, `unk_func4`, `part_check` et `check_valid`. Manifestement elles ne sont pas dans le loader.

![](wu_images/Pasted%20image%2020240511150744.png)

Ni dans notre programme `GotYou`... Oui vous l'avez compris elles sont dans la libc.

![](wu_images/Pasted%20image%2020240511150834.png)

## unk_func1

Observons `unk_func1`.

![](wu_images/Pasted%20image%2020240511150921.png)

Des opérations sont réalisées sur un tableau statique nommé `vals` que nous pouvons simplifier en :
- vals[0] \*= (val+1)\*7;
- vals[1] /= (val+1);
- vals[2] += val+3;
- vals[3] += val+4;
Avec `val` le troisième paramètre de la fonction.

## unk_func2

De même pour `unk_func2` on observe.

![](wu_images/Pasted%20image%2020240511151407.png)

Soit :
- vals[0] += val+8;
- vals[1] += val+5;
- vals[2] \*= (val+1)\*3;
- vals[3] /= (val+1);
Avec `val` le deuxième paramètre de la fonction.

## unk_func3

De même pour `unk_func3` on observe.

![](wu_images/Pasted%20image%2020240511151542.png)

Soit :
- vals[0] /= (val+1);
- vals[1] += val+1;
- vals[2] += val+7;
- vals[3] \*= (val+1)\*5;
Avec `val` le deuxième paramètre de la fonction.

## unk_func4

Enfin pour `unk_func4` on observe.

![](wu_images/Pasted%20image%2020240511151724.png)

Soit :
- vals[0] += val+2;
- vals[1] \*= (val+1)\*9;
- vals[2] /= (val+1);
- vals[3] += val+6;
Avec `val` le deuxième paramètre de la fonction.

## part_check

Regardons maintenant `part_check`.

![](wu_images/Pasted%20image%2020240511151857.png)

On voit qu'en fonction d'un indice passé dans le premier paramètre, 5 jeux de vérifications sont effectuées que l'on peut simplifier en :
- Si idx < 4 : `if(vals[0] == 387488 && vals[1] == 1844208 && vals[2] == 13 && vals[3] == 4661) checks[0] = true;`
- Si idx >= 4 et idx < 8 : `if(vals[0] == 10448 && vals[1] == 7463745 && vals[2] == 1458 && vals[3] == 28) checks[1] = true;`
- Si idx >= 8 et idx < 12 : `if(vals[0] == 6190 && vals[1] == 4218 && vals[2] == 701 && vals[3] == 4000) checks[2] = true;`
- Si idx >= 12 et idx < 16 : `if(vals[0] == 3942 && vals[1] == 47313 && vals[2] == 63 && vals[3] == 2027) checks[3] = true;`
- Si idx >= 16 et idx < 20 : `if(vals[0] == 857 && vals[1] == 3888 && vals[2] == 46 && vals[3] == 20741) checks[4] = true;`
Puis les valeurs dans `vals` sont toutes remises à 0.

## check_valid

Penchons-nous sur `check_valid`.

![](wu_images/Pasted%20image%2020240511152441.png)

Ici on s'assure que le tableau de `checks` soit entièrement composé de booléens à vrai.

## main

De retour dans notre fonction principale, observons les opérations de la boucle `while`.

![](wu_images/Pasted%20image%2020240511153055.png)

Tout d'abord, en fonction des quatre derniers bits du caractère courant du mot de passe, `current_last_four`, on force retire la résolution d'une des fonctions parmi `chmod`, `dup2`, `strncmp` et `mallopt`.

![](wu_images/Pasted%20image%2020240511153732.png)

Ensuite, on entre dans une boucle interne et pour chaque caractère on exécute 3 des 4 fonctions `unk_func1`, `unk_func2`, `unk_func3` et `unk_func4` avec pour `val` les 4 premiers bits du caractère courant. Attention, en réalité une des 4 fonctions n'est pas exécutée car sa résolution a été forcée lors de l'extrait de code précédent. Cette fonction aura donc pour valeur `check_valid` (aucun effet). Ensuite, `check_part` est appelé et l'on sort de cette boucle interne si les 4 derniers bits du caractère suivant ne sont pas les mêmes que pour le caractère courant.

![](wu_images/Pasted%20image%2020240511154521.png)

Dans ce cas, on force la résolution de nouveau de la fonction qui avait été remplacée par un `check_valid`. En somme, l'utilisateur peut contrôler pour chaque caractère de son mot de passe, quelle fonction par les `unk_func*` ne sera pas exécutée sur la valeur qu'il passe.

![](wu_images/Pasted%20image%2020240511154713.png)

Enfin `check_valid` est appelé et si elle retourne vrai, le message de succès est affiché.

# Synthèse pré-résolution

Résumons ce que nous savons avant de résoudre le problème :
- Le mot de passe rentré par l'utilisateur mesure 20 caractères.
- Pour chaque caractère de l'utilisateur, les 4 premiers bits codent une valeur transmise aux `unk_func*` et les 4 derniers indiquent quelle fonction ne pas exécuter.
- Les `unk_func*` modifient les valeurs d'un tableau `vals`.
- Tous les 4 caractères, ce tableau `vals` est vérifié puis remis à 0. Chaque résultat de vérification est sauvegardé dans un tableau `checks`.
- Enfin, après les 20 caractères, ce tableau `checks` est vérifié et il ne doit contenir que des résultats vrais.

# Solution

Nous pouvons donc utiliser un bruteforce sur 4 caractères pour retrouver le mot de passe, puisque le tableau de `vals` est remis à 0 tous les 4 caractères.

```python
vals = [0, 0, 0, 0]

def unk_func1(val):
    vals[0] *= (val+1)*7
    vals[1] //= (val+1)
    vals[2] += val+3
    vals[3] += val+4
    for i in range(4):
        vals[i] &= 0xFFFFFFFF

def unk_func2(val):
    vals[0] += val+8
    vals[1] += val+5
    vals[2] *= (val+1)*3
    vals[3] //= (val+1)
    for i in range(4):
        vals[i] &= 0xFFFFFFFF

def unk_func3(val):
    vals[0] //= (val+1)
    vals[1] += val+1
    vals[2] += val+7
    vals[3] *= (val+1)*5
    for i in range(4):
        vals[i] &= 0xFFFFFFFF

def unk_func4(val):
    vals[0] += val+2
    vals[1] *= (val+1)*9
    vals[2] //= (val+1)
    vals[3] += val+6
    for i in range(4):
        vals[i] &= 0xFFFFFFFF

flag = ''
funcs_arr = [
    [3, unk_func1],
    [5, unk_func2],
    [6, unk_func3],
    [7, unk_func4],
]

funcs_idx = [0, 0, 0, 0]
vals_idx = [0, 0, 0, 0]

def increase_idx(idx):
    vals_idx[idx] += 1
    if vals_idx[idx] >= 0x10:
        vals_idx[idx] = 0
        funcs_idx[idx] += 1
        if funcs_idx[idx] >= 4:
            funcs_idx[idx] = 0
            increase_idx(idx+1)

expected_res = [[387488, 1844208, 13, 4661], [10448, 7463745, 1458, 28], [6190, 4218, 701, 4000], [3942, 47313, 63, 2027], [857, 3888, 46, 20741]]
flag_parts = ['']*5
ctr = 0
found_len = 0;
while found_len < 5:
    if (ctr % 0x10000) == 0:
        print(funcs_idx, vals_idx)
    ctr += 1
    vals = [0, 0, 0, 0]
    for i in range(4):
        val = vals_idx[i]
        for func_pair in funcs_arr:
            func_idx, func = func_pair
            if func_idx != funcs_arr[funcs_idx[i]][0]:
                func(val)
    if vals in expected_res:
        found_len += 1
        flag_idx = expected_res.index(vals)
        for i2 in range(4):
            flag_parts[flag_idx] += chr((funcs_arr[funcs_idx[i2]][0] << 4) | vals_idx[i2])
    increase_idx(0)

flag = 'BZHCTF{'+''.join(flag_parts)+'}'
print('Flag:',flag)
```

En exécutant le script, on obtient notre mot de passe : `_ld_le4ds_ctr1_f10w_`
Passons le au programme :

![](wu_images/Pasted%20image%2020240511155711.png)

Notre flag est donc `BZHCTF{_ld_le4ds_ctr1_f10w_}`

# Conclusion

Ce challenge avait pour objectif de mettre en avant le mécanisme de résolution de la `.got` par le loader. Il n'était pas facile mais utiliser une approche dynamique pouvait grandement simplifier la tâche.

