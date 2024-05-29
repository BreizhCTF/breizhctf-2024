_Est-il bien difficile de retrouver où est cachée la chaîne qui vous permettra de résoudre ce challenge ? Et n'existe-t-il pas un moyen encore plus simple de la récupérer ?_

# Introduction

Il me paraît important de préciser que si je réalise dans ce writeup l'analyse de l'exécutable à l'aide d'un désassembleur uniquement (approche statique), un gain de temps considérable pourrait être obtenu via une analyse dynamique à l'aide d'un débogueur.

# I - Analyse globale

La première chose à noter en ouvrant le binaire dans un désassembleur ou via la commande `file` est qu'il s'agit d'un exécutable PE (Portable Executable) destiné aux systèmes Windows sous architecture x86-64.

![](wu_images/Pasted%20image%2020240509172844.png)

Le plus simple serait donc de disposer d'un environnement Windows 64-bit pour conduire une analyse dynamique de la cible mais comme précisé, tout sera réalisé en statique.

## main

En ouvrant le binaire dans un désassembleur (j'utiliserai BinaryNinja), on commence par analyser la fonction `main`.

![](wu_images/Pasted%20image%2020240509173609.png)

On observe tout d'abord les appels à une fonction ici nommée `sub_140001010`. Comme on le devine aisément via les paramètres des appels et en ouvrant cette fonction dans le désassembleur (appel à `__stdio_common_vfprintf`), il s'agit d'un wrapper de `printf`.
Retypons et renommons la fonction en conséquence.

![](wu_images/Pasted%20image%2020240509174148.png)

Nous en déduisons donc que le buffer passé à l'appel à `fgets` qui suit n'est autre que le mot de passe saisi par l'utilisateur. La partie suivant le `fgets` est intéressante.

![](wu_images/Pasted%20image%2020240509174727.png)

Une première vérification sur le retour de `fgets` s'assure que le pointeur renvoyé n'est pas nul i.e la fonction a bien été exécutée. Ensuite, une petite boucle while vient itérer sur chaque caractère du mot de passe de l'utilisateur tant que celui-ci n'est pas nul. Le compteur incrémenté n'est autre que la taille de la chaîne et ce bout de code est la version optimisée par inlining de `strlen`. Nous pouvons donc renommer `rax_3` par `password_length`. Nous constatons ensuite que cette taille doit valoir 0x26 = 38. Donc le mot de passe mesure 38 caractères. Regardons la suite.

![](wu_images/Pasted%20image%2020240509175449.png)

Une chaîne (ici nommée `lpBuffer`) est chargée en mémoire via la fonction `LoadStringA` de l'API Windows. Selon la documentation, `LoadStringA` "charge une ressource de chaîne à partir du fichier exécutable associé à un module spécifié et copie la chaîne dans une mémoire tampon avec un caractère null de fin ou retourne un pointeur en lecture seule vers la ressource de chaîne elle-même". Le premier paramètre est le module lié à un fichier exécutable, ici la valeur de retour de `GetModuleHandleW`. En observant la documentation associée, on peut lire "Si ce paramètre (lpModuleName) a la valeur NULL, GetModuleHandle retourne un handle au fichier utilisé pour créer le processus appelant (.exe fichier)". Nous chargeons donc une ressource enfouie dans notre propre exécutable, d'où le nom du challenge.
Alors ici, bien évidemment le plus simple eut été de déboguer, de placer un point d'arrêt juste après l'appel à LoadStringA et de récupérer la valeur de la chaîne en mémoire. Mais nous verrons ici un moyen tout aussi simple de réaliser cette tâche statiquement. Pour cela installons l'outil `pefile` de `folbricht` disponible sur Github.

## pefile

![](wu_images/Pasted%20image%2020240509181352.png)

Nous pouvons ensuite lister les ressources de la section `.rsrc` de notre exécutable.

![](wu_images/Pasted%20image%2020240509181458.png)

Deux ressources sont disponibles. Extrayons-les toutes deux et constatons.

![](wu_images/Pasted%20image%2020240509181602.png)  
![](wu_images/Pasted%20image%2020240509181626.png)

Là où la seconde chaîne n'est autre qu'une en-tête XML, la première semble plus intéressante. De plus cette chaîne a la bonne idée de mesurer 39 caractères (ce qui se rapproche de notre mot de passe à 38 caractères et correspond au dernier paramètre de `LoadStringA`).

![](wu_images/Pasted%20image%2020240509182033.png)

Revenons dans le code de `main`.

## main

Une boucle `while` vient conclure le challenge. J'ai renommé la chaîne chargée par `LoadStringA` : `hidden_string`.

![](wu_images/Pasted%20image%2020240509182726.png)

On constate ici que le message de succès est affiché lorsqu'un compteur `ctr` arrive à 0x26=38 soit après avoir parcouru la taille de notre mot de passe. Sauf que, si une condition n'est pas validée pour chaque tour de boucle, nous en sortons. La condition impose que la valeur UTF-8 de chaque caractère de la chaîne cachée + 5 corresponde à chaque caractère de notre mot de passe.
Passons à la résolution !

# Solution

Rien de bien compliqué, ajoutons 5 à chaque caractère de la chaîne cachée dans un script Python.

```python
s = b'&=UC>OAvK.Za,g.nZc/q.Zn+Zh/itZa./opm.nx'
flag = ''

for i in range(len(s)):
    flag += chr(s[i] + 5)

print(flag)
```

Nous obtenons : `+BZHCTF{P3_f1l3s_h4v3_s0_m4ny_f34tur3s}`. Bien entendu le `+` en début de chaîne est une erreur due à l'extraction du premier caractère `&` par `pefile`, ce qui explique la taille de 39 caractères au lieu de 38.
Voici donc notre flag : `BZHCTF{P3_f1l3s_h4v3_s0_m4ny_f34tur3s}`.

# Conclusion

Le challenge avait pour but de faire découvrir la notion de ressources dans les exécutables PE aux joueurs qui n'y ont jamais été confrontés.
