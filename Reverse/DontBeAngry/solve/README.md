_Nous avons récupéré un fichier qui semble contenir un message intéressant ainsi que l'exécutable l'ayant chiffré. Pensez-vous être capable de casser son algorithme ?_

# Introduction

Il me paraît important de préciser que si je réalise dans ce writeup l'analyse de l'exécutable à l'aide d'un désassembleur uniquement (approche statique), un gain de temps considérable pourrait être obtenu via une analyse dynamique à l'aide d'un débogueur.

# I - Analyse globale

La première chose à noter en ouvrant le binaire dans un désassembleur ou via la commande `file` est l'absence de symboles (stripped) ce qui pourrait rendre plus difficile la phase de reverse.

![](wu_images/Pasted%20image%2020240511172349.png)

Cependant, on remarque également que le binaire est lié dynamiquement (dynamically linked), nous aurons donc accès aux symboles des bibliothèques dans un désassembleur.

## main

En ouvrant le binaire dans un désassembleur (j'utiliserai BinaryNinja), on commence par analyser la fonction `main`.

![](wu_images/Pasted%20image%2020240511172320.png)

Ici, après l'affichage de la bannière, un mot de passe est demandé à l'utilisateur sur 8 octets (le neuvième étant le caractère de fin de ligne). Ensuite, si le paramètre `--decrypt` est passé au programme, un fichier semble être décodé avec notre mot de passe, probablement le ficher `flag.enc` distribué en pièce-jointe. Concentrons-nous sur l'autre cas pour le moment.
Notre mot de passe semble être considéré comme un nombre sur 8 octets (`int64_t`) plutôt qu'une chaîne de caractères car des opérations logiques sont effectuées dessus.

![](wu_images/Pasted%20image%2020240511172509.png)

Deux conditions indiquent que :
- `(input & 0x15de954d20b158aa) == (0x1054014020201002 ou 0x10004d20301002)`
- `(input | -0x118c239544492166) == (-0x118c018000490121 ou -0x188028500010125)`

![](wu_images/Pasted%20image%2020240511172808.png)

Ensuite, une variable statique est mise à 1, un `sleep` de 1 seconde est effectué (simple hasard ?) puis deux fonctions sont appelées sur notre mot de passe. La valeur de notre mot de passe en sortie de ces fonctions doit être telle que :
- `input == (0x214dabee2f9cb469 ou -0x762edd64e00a733d)`
Un nouveau `sleep` de 1 seconde est effectué (ça commence à faire beaucoup) puis la fonction `sub_1882` est appelée une nouvelle fois. La valeur de notre mot de passe en sortie de cette ultime fonction doit être telle que :
- `input == (-0x1d9e395b60a11276 ou 0x37b7f8273028c5c6)`

Un participant pressé de trouver un flag tentera peut-être ici une résolution avec un framework comme angr.

# II - Tentative de résolution prématurée

Réalisons donc un petit script avec `angr` pour tenter de trouver la solution en symbolisant notre mot de passe à 8 caractères et en spécifiant un point de succès et des points d'échec (ici on en spécifie un seul).

```python
import angr
import claripy
import logging

logging.getLogger('angr').setLevel('ERROR')
bin_name = '../dist/DontBeAngry'

input_len = 8
base_addr = 0x0
win_addr = 0x16ca + base_addr
fail_addr = [0x16e0 + base_addr]
p = angr.Project(bin_name, main_opts={'base_addr': base_addr}, auto_load_libs=True)
flag_chars = [claripy.BVS('flag_%d' % i, 8) for i in range(input_len)]
flag = claripy.Concat(*flag_chars)
entry_state = p.factory.entry_state(args=[bin_name], stdin=flag)
simgr = p.factory.simulation_manager(entry_state)
simgr.explore(find = win_addr, avoid = fail_addr)
if not len(simgr.found):
    print('Failure')
for win_state in simgr.found:
    flag_resolved = win_state.posix.dumps(0).decode()
    print(f'Password: {flag_resolved}')
    exit()
```

On lance le script et...

![](wu_images/Pasted%20image%2020240511175139.png)

Hourra ! Un mot de passe semble valider le challenge. Essayons donc de déchiffrer le fichier.

![](wu_images/Pasted%20image%2020240511175248.png)

Tout semble bien fonctionner, regardons le fichier "flag" résultant.

![](wu_images/Pasted%20image%2020240511175409.png)

On s'est bien moqué de nous... Revenons à l'analyse du binaire pour comprendre tout cela.

# III - Retour à l'analyse globale

Regardons le contenu de `sub_13bc`, la première des deux fonctions appelées dans `main`.

## sub_13bc

Voici de le code de la fonction.

![](wu_images/Pasted%20image%2020240511173006.png)

Ici, une boucle itérant sur notre mot de passe. Un indice le parcourt en partant du début (`i2`), un autre en partant de la fin (`i`). La boucle s'arrête lorsqu'ils se rencontrent, donc à la moitié du parcours. Pour chaque itération, `sub_1329` est appelée avec un pointeur vers le caractère à l'indice `i2` et un pointeur vers le caractère à l'indice `i` en paramètres.

## sub_1329

Rien de bien compliqué ici.

![](wu_images/Pasted%20image%2020240511173031.png)

Cette fonction inverse simplement deux caractères dans une chaîne. Et nous en déduisons donc que `sub_13bc` inverse notre mot de passe. Revenons dans `main`.

## main

Notre entrée est donc inversée avant d'appeler `sub_1882`.

![](wu_images/Pasted%20image%2020240511173809.png)

## sub_1882

Voici son contenu.

![](wu_images/Pasted%20image%2020240511173158.png)

Une fonction `sub_1840` est appelée deux fois, avec en paramètres deux pointeurs contenant tous deux notre mot de passe. Mais l'opération `*input = var_18` nous indique que `var_18` contiendra sans doute la sortie de `sub_1840`.

## sub_1840

Trois appels sont effectués.

![](wu_images/Pasted%20image%2020240511175803.png)

Regardons le premier d'entre eux.

## sub_170a

Ici une boucle itère sur les caractères de notre mot de passe et semble chercher des éléments dans une variable statique `data_4020`.

![](wu_images/Pasted%20image%2020240511180010.png)

Retypons cette variable statique en tant que tableau de `char` puisque les éléments en résultant sont insérés dans notre mot de passe.

![](wu_images/Pasted%20image%2020240511180429.png)

Regardons de nouveau la fonction.

![](wu_images/Pasted%20image%2020240511180519.png)

On remplace donc chaque caractère de notre mot de passe par la valeur dans `static_arr` à l'indice définit par notre caractère. C'est donc une S-Box en réalité, renommons le tout en conséquence puis passons à la fonction appelée après celle-ci.

![](wu_images/Pasted%20image%2020240511180738.png)

## sub_175b

Voici le code de cette fonction.

![](wu_images/Pasted%20image%2020240511181728.png)

Je me suis permis de renommer certaines variables pour faciliter la compréhension. Une boucle parcourt notre mot de passe et applique un xor entre l'élément courant et l'élément suivant pour former un nouveau tableau `out`. Nous appellerons cette fonction `xor_arr`.
La dernière fonction appelée dans `sub_1840` est `sub_17eb`.

## sub_17eb

Ici, une simple boucle vient appliquer un xor entre les deux tableaux passés en paramètres.

![](wu_images/Pasted%20image%2020240511182230.png)

Nous appellerons cette fonction `add_round` car elle applique le tableau calculé durant ce tour dans l'algorithme à notre entrée initiale.

## sub_1840

De retour dans `sub_1840`, constatons.

![](wu_images/Pasted%20image%2020240511182522.png)

Il s'agit en fait de réaliser un tour d'un algorithme simple sur une chaîne en entrée. Nous appellerons donc cette fonction `round`. Cet algorithme réalise des opérations destructrices lorsqu'il effectue un xor sur un élément et l'élément suivant sans qu'aucun élément initial ne soit sauvegardé dans la chaîne. Il s'agit donc d'une fonction de hachage.

## sub_1882

Cette fonction effectue donc un hash de notre mot de passe sur deux tours de l'algorithme.

![](wu_images/Pasted%20image%2020240511182841.png)

Nous l'appellerons `process_hash`.

## main

De retour dans `main`, il semble que nous disposions de tous les éléments du puzzle.

![](wu_images/Pasted%20image%2020240511183136.png)

Après avoir inversé notre mot de passe, nous le hachons une première fois et vérifions le résultat, puis une deuxième fois et observons le résultat de nouveau. Seulement, pourquoi angr renvoit-il une solution décodant un mauvais fichier. Et puis pourquoi deux valeurs sont-elles autorisées pour notre hash ? Pour avoir une piste, vérifions déjà notre mot de passe trouvé avec angr.

![](wu_images/Pasted%20image%2020240511183508.png)

Mais... il ne fonctionne tout bonnement pas ! Comment angr a-t-il pu vérifier les conditions pour atteindre le succès de notre programme. C'est donc que quelque chose dans le programme n'est pas interprété correctement par angr, pire puisqu'angr trouve un mot de passe logique c'est qu'il tombe dans un piège, d'où le nom du challenge.
Oui mais nous avons l'impression de tout avoir analysé et rien ne devrait fausser l'analyse des chemins par angr. Mais il y a ces `sleep` qui semblent ne servir à rien, puis cette variable statique... Tiens regardons ses références.

![](wu_images/Pasted%20image%2020240511183848.png)

Une fonction que nous n'avons pas analysée, intéressant.

## sub_147d

Avant de regarder son contenu, regardons déjà qui appelle cette fonction.

![](wu_images/Pasted%20image%2020240511184006.png)

Tiens tiens, elle est mise en paramètre de la fonction `signal`, ce qui signifie que lorsque un signal de type 0xe=14 est déclenché, notre fonction sera appelée, c'est un sighandler.

![](wu_images/Pasted%20image%2020240511184131.png)

D'après la liste de signaux UNIX, le signal 14 est SIGALRM, une "alarme d'horloge". D'après la documentation : `SIGALRM is an asynchronous signal. The SIGALRM signal is raised when a time interval specified in a call to the alarm or alarmd function expires`. Une de ces deux fonctions est sans doute appelée quelque part, on commence à comprendre le rôle des `sleep`. Renommons notre fonction `alarm_sighandler` puis regardons la fonction appelant `signal`.

## sub_14ae

Voici son contenu.

![](wu_images/Pasted%20image%2020240511184750.png)

Un appel à `srand` avec la graine 0x21011793. Puis notre appel à `signal` et enfin un appel à une fonction `sub_1415`. Avant de l'analyser, constatons qui appelle `sub_14ae`.

![](wu_images/Pasted%20image%2020240511184858.png)

Notre bonne vieille section `.init_array` qui permet à la libc de lancer des fonctions d'initialisation au tout début du programme, avant le `main`. Appelons notre fonction `init_func` puis analysons `sub_1415`.

## sub_1415

Voici son contenu.

![](wu_images/Pasted%20image%2020240511185049.png)

Un appel à `setitimer` est effectué. Regardons la documentation.

![](wu_images/Pasted%20image%2020240511185215.png)

Le premier paramètre, le `which` permet de définir le type de temporisation. D'après le code source de la libc, notre `which` à 0 signifie donc l'utilisation de `ITIMER_REAL`.

![](wu_images/Pasted%20image%2020240511185419.png)

Donc le temps avant le déclenchement du signal `SIGALRM` est le temps réel qui s'est écoulé. Voici les structures utilisées par le deuxième paramètre. Ajoutons les dans notre désassembleur, retypons `s` et constatons. Voici notre fonction désormais.

![](wu_images/Pasted%20image%2020240511185934.png)

Donc l'alarme est appelée au bout de 0x384 = 900 millisecondes, c'est un peu moins qu'une seconde et ça rappelle grandement les `sleep` de une seconde présents dans `main`. Renommons cette fonction `setup_alarm` et analysons le contenu de notre sighandler.

## alarm_sighandler

Voici son contenu.

![](wu_images/Pasted%20image%2020240511190222.png)

La fameuse variable globale présente dans `main` est vérifiée et si elle est non-nulle, on appelle `sub_135d`. Ensuite, `setup_alarm` est appelée de nouveau ce qui signifie que l'alarme est armée de nouveau et ce sighandler sera rappelé dans 900ms. On peut comprendre alors le rôle de la variable globale. En effet, au début de `main`, le programme attend le mot de passe de l'utilisateur. Pendant ce temps, plusieurs secondes peuvent s'écouler et ce booléen global permet donc de s'assurer que le programme a passé l'étape du `fgets` avant d'appeler `sub_135d`. Les deux `sleep` de `main` correspondent donc à deux appels déguisés à `sub_135d`.

## sub_135d

Voici le contenu de cette mystérieuse fonction.

![](wu_images/Pasted%20image%2020240511191132.png)

On itère de 256 à 0 et on réarrange la `sbox`. Pour cela, un appel à `rand`, on rappelle que la graine 0x21011793 a été associée au début du programme. Et on remplace donc le caractère à l'indice `i` de la `sbox` par `sbox[rand() % (i + 1)]`.
C'est donc ce mécanisme de détournement du flux d'exécution via l'alarme et les `sleep` qui fausse la route d'angr.

# Synthèse pré-résolution

Résumons ce que nous savons avant de résoudre le problème :

- Notre mot de passe mesure 8 caractères
- Certaines vérifications avant le hachage permettent de diminuer le nombre de valeurs d'entrée
- La S-Box de l'algorithme est mélangée avant chaque génération de hash
- Deux hashs doivent être vérifiés (avec deux S-Box différentes)

# Résolution

Il est possible d'établir un bruteforce sur les bits non-fixés par les 2 premières conditions pour résoudre le challenge. La solution est en C pour disposer d'une vitesse d'exécution satisfaisante.

```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>


uint8_t SBOX[256] = {70, 90, 117, 178, 128, 155, 173, 39, 36, 16, 3, 25, 52, 32, 97, 250, 50, 154, 153, 198, 147, 195, 87, 161, 244, 201, 156, 34, 177, 22, 133, 76, 237, 143, 30, 206, 126, 47, 5, 182, 254, 179, 139, 91, 121, 236, 238, 205, 49, 246, 109, 152, 18, 241, 181, 176, 216, 56, 62, 89, 184, 220, 255, 99, 194, 129, 101, 226, 131, 0, 83, 191, 209, 55, 183, 187, 207, 145, 208, 165, 229, 130, 95, 196, 169, 23, 132, 168, 27, 240, 26, 61, 110, 164, 210, 29, 171, 1, 57, 221, 142, 14, 200, 118, 20, 217, 92, 252, 44, 67, 96, 84, 75, 215, 180, 175, 122, 81, 211, 107, 41, 115, 59, 48, 19, 218, 120, 112, 235, 149, 93, 162, 73, 219, 86, 69, 134, 35, 174, 78, 37, 223, 66, 160, 24, 197, 98, 43, 33, 203, 38, 199, 192, 111, 186, 40, 245, 108, 151, 71, 190, 100, 150, 88, 113, 72, 60, 85, 159, 82, 170, 230, 54, 212, 9, 185, 124, 253, 28, 2, 68, 225, 63, 7, 214, 10, 204, 58, 106, 188, 148, 146, 74, 4, 163, 189, 8, 224, 243, 15, 104, 119, 105, 102, 45, 53, 248, 166, 80, 103, 167, 123, 247, 127, 125, 251, 116, 249, 12, 13, 213, 138, 77, 11, 65, 114, 46, 21, 233, 234, 172, 228, 232, 31, 79, 193, 158, 136, 94, 135, 242, 157, 17, 202, 137, 140, 64, 144, 239, 6, 141, 222, 51, 227, 231, 42};
uint8_t SBOX_1[256];
uint8_t SBOX_2[256];
const uint32_t seed = 0x21011793;

void swap(uint8_t *a, uint8_t *b) {
    uint8_t tmp = *a;
    *a = *b;
    *b = tmp;
}

void shuffle_sbox() {
    for (uint8_t i = 256 - 1; i > 0; --i) {
        uint8_t j = rand() % (i + 1);
        swap(&SBOX[i], &SBOX[j]);
    }
}

void invert_input(uint8_t input[8]) {
    int start = 0;
    int end = 8 - 1;
    while (start < end) {
        swap(&input[start], &input[end]);
        start++;
        end--;
    }
}

void apply_sbox(uint8_t input[8]) {
    for(uint8_t i = 0; i < 8; i++) {
        input[i] = SBOX[input[i]];
    }
}

void mul_add(uint8_t input[8]) {
    uint8_t output[8];
    for(uint8_t i = 0; i < 8; i++) {
        output[i] = input[i] ^ input[((i + 1) % 8)];
    }
    memcpy(input, output, 8);
}

void add_round_output(uint8_t input[8], uint8_t output[8]) {
    for(uint8_t i = 0; i < 8; i++) {
        output[i] ^= input[i];
    }
}

void round(uint8_t input[8], uint8_t output[8]) {
    apply_sbox(input);
    mul_add(input);
    add_round_output(input, output);
}

void process_hash(uint8_t input[8]) {
    uint8_t output[8];
    memcpy(output, input, 8);
    for(uint8_t i = 0; i < 2; i++) {
        round(input, output);
    }
    memcpy(input, output, 8);
}


void extract_bits(uint64_t and_val, uint64_t res1, uint64_t or_val, uint64_t res2, uint64_t* bits, uint64_t* val) {
    *bits = 0;
    *val = 0;
    for(uint8_t i = 0; i < 64; i++) {
        *bits <<= 1;
        *val <<= 1;
        uint8_t and_bit = (and_val >> (63-i)) & 1;
        uint8_t res1_bit = (res1 >> (63-i)) & 1;
        if(and_bit) {
            if(res1_bit) *val |= 1;
            *bits |= 1;
        } else {
            uint8_t or_bit = (or_val >> (63-i)) & 1;
            uint8_t res2_bit = (res2 >> (63-i)) & 1;
            if(!or_bit) {
                if(res2_bit) *val |= 1;
                *bits |= 1;
            }
        }
    }
}

bool try_val(uint64_t val) {
    uint64_t val_cpy = val;
    process_hash(&val_cpy);
    if(val_cpy == 0x214dabee2f9cb469 || val_cpy == 0x89d1229b1ff58cc3) {
        memcpy(SBOX, SBOX_2, 256);
        val_cpy = val;
        invert_input(&val_cpy);
        process_hash(&val_cpy);
        memcpy(SBOX, SBOX_1, 256);
        if(val_cpy == 0xe261c6a49f5eed8a || val_cpy == 0x37b7f8273028c5c6) {
            
            return true;
        }
    }
    return false;
}

bool bruteforce(uint64_t bits, uint64_t val, uint8_t index) {
    if(index >= 64) return false;
    if(!((bits >> index) & 1)) {
        if(try_val(val | (1LL << index))) {
            val = val | (1LL << index);
            printf("Correct input: ");
            fwrite(&val, 1, 8, stdout);
            printf("\n");
            return true;
        }
        if(bruteforce(bits, val | (1LL << index), index+1)) return true;
    }
    return bruteforce(bits, val, index+1);
}

int main() {
    srand(seed);
    shuffle_sbox();
    memcpy(SBOX_1, SBOX, 256);
    shuffle_sbox();
    memcpy(SBOX_2, SBOX, 256);
    memcpy(SBOX, SBOX_1, 256);
    uint64_t bits, val;
    extract_bits(0x15de954d20b158aa, 0x1054014020201002, 0xee73dc6abbb6de9a, 0xee73fe7fffb6fedf, &bits, &val);
    bruteforce(bits, val, 0);
    extract_bits(0x15de954d20b158aa, 0x1054014020201002, 0xee73dc6abbb6de9a, 0xfe77fd7afffefedb, &bits, &val);
    bruteforce(bits, val, 0);
    extract_bits(0x15de954d20b158aa, 0x10004d20301002, 0xee73dc6abbb6de9a, 0xee73fe7fffb6fedf, &bits, &val);
    bruteforce(bits, val, 0);
    extract_bits(0x15de954d20b158aa, 0x10004d20301002, 0xee73dc6abbb6de9a, 0xfe77fd7afffefedb, &bits, &val);
    bruteforce(bits, val, 0);
    return 0;
}
```

En lançant le script on obtient le mot de passe : `G00d_j0b`.
Déchiffrons alors le fichier de flag.

![](wu_images/Pasted%20image%2020240511192710.png)

On obtient :

![](wu_images/Pasted%20image%2020240511192825.png)

Notre flag est donc : `BZHCTF{tim3d_c0ntr0l_fl0w}`

# Conclusion

L'objectif de ce challenge était de présenter au joueur les concepts d'alarme, de sighandler, de fonction d'initialisation et de lui montrer un moyen simple de tromper un framework comme angr. Une analyse dynamique aurait pu permettre au joueur de constater les signaux d'alarme plus aisément et d'en chercher leur source.
