BreizhCTF 2024 - The Intrepid (4/4)
==========================

### Description

**De :** `the-intrepid-journal@notproton.me`  
**À :** `dfir-independant-consulting@notproton.me` (vous)

**Objet :** Re : Re : [`www.dfir-independant-consulting.notcom`] Nouveau contrat : The Intrepid journal

> [...] Je dois encore comprendre comment il lui est possible de mettre la main sur les identifiants de partage. En effet, les informations transmises entre la charge virale et le serveur ne sont que partielles. Il semblerait qu'une charge additionnelle se soit ancrée à la racine même du système Linux. Au cours de mes analyses, je serais sûrement amené à déchiffrer un fichier sur le serveur, lequel puis-je utiliser pour valider mes recherches ? Enfin, pourriez-vous me transmettre la configuration de votre machine virtuelle, afin de pouvoir mettre en place un environnement iso-prod ?

Nous vous autorisons à lire le fichier partagé `61e82b86235a2228c477f1ce8c5bb7e0bac76a82`, car nous l'avions téléversé nous-même, et il ne contient rien de confidentiel. La configuration `vagrant` est jointe à ce mail.

---

Identifiez :

- Le contenu déchiffré du fichier spécifié dans la description, ou celui du mail joint à ce challenge. Chacun contenant un secret valide, à choisir pour valider l'épreuve. PS : Les fichiers en clair sont tous deux des fichiers ZIP.

Format de flag : `BZHCTF{contenu_secret}`  
Exemple de flag : `BZHCTF{THIS_IS_THE_SECRET}`

### Fichiers fournis

- config_vagrant.txt
- mail_anonyme.md

### Lecture du mail anonyme joint au challenge


```
**De :** `anonymous-reporter@notproton.me`  
**À :** `dfir-independant-consulting@notproton.me` (vous)

**Objet :** The Intrepid journal is corrupted at its root

The Intrepid journal, which was once free and independant, is now controlled by a multinational company. This company uses the journal notoriety to insidiously orient investigators towards their concurrent activities, and discredit them.

I was about to download files, containing contracts between the journal admins and this company, but you spoiled the party. Now the application is shutdown, and my backdoor is useless. If you do not trust me, finish the investigation, reverse my logic, and decrypt the file at `/var/www/html/app/uploads/38111a8e12a77b820a9a3373a3f2810645a36e0e/38111a8e12a77b820a9a3373a3f2810645a36e0e`. You'll see that I am not a liar.
```

Il semblerait que `The Intrepid` ne soit pas une organisation si libre et indépendante que ça... Percer le mystère dans le dos de notre client, ou respecter le contrat d'investigation. Ce choix ne sera à faire qu'à la toute fin du challenge.

### Poursuite des analyses effectuées dans la partie 3 

Dans la précédente partie de cette série de challenges, nous avons pu extraire un module malveillant du système, et commencé à le disséquer et analyser. Néanmoins, certaines fonctions n'ont pas encore été investiguées en profondeur. Rappellons nous également qu'un hook kernel a été posé sur la fonction `get_random_bytes_user`, qui pourrait potentiellement être liée au chiffrement/déchiffrement des fichiers partagés sur le serveur. 

Nous n'avions pu déterminer directement quelle fonction du module supplantait `get_random_bytes_user`. Néanmoins, par élimination et déduction, il s'agit fort probablement de `the_destiny`.

#### Fonction "the_destiny"

```c
ssize_t __fastcall the_destiny(iov_iter *iter)
{
  const char *v1; // r13
  size_t count; // r12
  __int64 v3; // rbp
  __int64 v4; // rax
  int v5; // edx
  int v6; // ebx
  unsigned __int64 v7; // r15
  __int64 v8; // r12
  size_t v10; // [rsp+0h] [rbp-88h]
  timespec64 ts; // [rsp+10h] [rbp-78h] BYREF
  rnd_state prng_state; // [rsp+20h] [rbp-68h] BYREF
  char *rotate[4]; // [rsp+30h] [rbp-58h]
  unsigned __int64 v14; // [rsp+50h] [rbp-38h]

  _fentry__(iter);
  v14 = __readgsqword(0x28u);
  rotate[0] = "sCYHnZC97X";
  rotate[1] = "4W2TwpmFMz";
  rotate[2] = "ZAijP8972D";
  rotate[3] = "c63duF2UpW";
  ktime_get_real_ts64(&ts);
  v1 = rotate[prandom_u32() & 3];
  count = iter->count;
  v10 = strlen(v1);
  v3 = _kmalloc(count, 0xDC0LL);
  v4 = HIDWORD(ts.tv_sec) ^ (unsigned int)(LODWORD(ts.tv_sec) ^ (LODWORD(ts.tv_sec) << 0xA));
  if ( (unsigned int)v4 <= 1 )
  {
    prng_state.s1 = v4 + 2;
LABEL_3:
    prng_state.s2 = v4 + 8;
LABEL_4:
    prng_state.s3 = v4 + 0x10;
    goto LABEL_5;
  }
  prng_state.s1 = HIDWORD(ts.tv_sec) ^ LODWORD(ts.tv_sec) ^ (LODWORD(ts.tv_sec) << 0xA);
  if ( (unsigned int)v4 <= 7 )
    goto LABEL_3;
  prng_state.s2 = HIDWORD(ts.tv_sec) ^ LODWORD(ts.tv_sec) ^ (LODWORD(ts.tv_sec) << 0xA);
  if ( (unsigned int)v4 <= 0xF )
    goto LABEL_4;
  prng_state.s3 = HIDWORD(ts.tv_sec) ^ LODWORD(ts.tv_sec) ^ (LODWORD(ts.tv_sec) << 0xA);
  if ( (unsigned int)v4 > 0x7F )
  {
    v5 = HIDWORD(ts.tv_sec) ^ LODWORD(ts.tv_sec) ^ (LODWORD(ts.tv_sec) << 0xA);
    goto LABEL_6;
  }
LABEL_5:
  v5 = v4 + 0x80;
LABEL_6:
  prng_state.s4 = v5;
  __writegsqword(
    (unsigned int)&net_rand_noise,
    __ROL8__(((unsigned __int64)&prng_state ^ __readgsqword((unsigned int)&net_rand_noise)) + v4, 0x20));
  if ( count )
  {
    v6 = 0;
    v7 = 0LL;
    do
    {
      ++v6;
      *(_BYTE *)(v3 + v7) = v1[v7 % v10] ^ prandom_u32_state(&prng_state);
      v7 = v6;
    }
    while ( v6 < count );
    if ( count > 0x7FFFFFFF )
      BUG();
  }
  _check_object_size(v3, count, 1LL);
  v8 = copy_to_iter(v3, count, iter);
  kfree(v3);
  return v8;
}
```

Immédiatement, nous pouvons identifier quatre chaînes de caractères, contenues dans un tableau `rotate`. Une d'entre elle est choisie aléatoirement, et assignée dans la variable `v1` (il est conseillé de renommer les variables après identification, pour plus de clarté) : 

```c
v1 = rotate[prandom_u32() & 3];
```

Sa taille est également calculée : 

```c
v10 = strlen(v1);
```

Ces deux variables sont utilisées dans une logique de type XOR : 

```c
*(_BYTE *)(v3 + v7) = v1[v7 % v10] ^ prandom_u32_state(&prng_state);
```

Bien, nous savons que chaque caractère est XORé avec la sortie de la fonction `prandom_u32_state`. Une recherche sur le Web ressort [cette description](https://android.googlesource.com/kernel/common/+/refs/heads/android-4.19-stable/lib/random32.c#47) : 

```c
/**
 *	prandom_u32_state - seeded pseudo-random number generator.
 *	@state: pointer to state structure holding seeded state.
 *
 *	This is used for pseudo-randomness with no outside seeding.
 *	For more random results, use prandom_u32().
 */
u32 prandom_u32_state(struct rnd_state *state)
```

Intéressant, il semblerait que cette fonction de génération pseudo-aléatoire dépende d'une graine de génération (seed en anglais), la rendant déterministe. Afin d'en apprendre plus, nous pouvons lire le code source du kernel : 

- https://elixir.bootlin.com/linux/v5.15.87/source/include/linux/prandom.h#L66

La fonction responsable de la création de cette seed est la suivante (bien que non listée explicitement dans ida) : 

```c
/**
 * prandom_seed_state - set seed for prandom_u32_state().
 * @state: pointer to state structure to receive the seed.
 * @seed: arbitrary 64-bit value to use as a seed.
 */
static inline void prandom_seed_state(struct rnd_state *state, u64 seed)
{
	u32 i = ((seed >> 32) ^ (seed << 10) ^ seed) & 0xffffffffUL;

	state->s1 = __seed(i,   2U);
	state->s2 = __seed(i,   8U);
	state->s3 = __seed(i,  16U);
	state->s4 = __seed(i, 128U);
	PRANDOM_ADD_NOISE(state, i, 0, 0);
}
```

La décompilation d'ida peut sembler un peu barbare, mais il est possible de retrouver ce pattern dans le programme : 

```c
v4 = HIDWORD(ts.tv_sec) ^ (unsigned int)(LODWORD(ts.tv_sec) ^ (LODWORD(ts.tv_sec) << 0xA));
// [...]
prng_state.s1 = HIDWORD(ts.tv_sec) ^ LODWORD(ts.tv_sec) ^ (LODWORD(ts.tv_sec) << 0xA);
// [...]
prng_state.s2 = HIDWORD(ts.tv_sec) ^ LODWORD(ts.tv_sec) ^ (LODWORD(ts.tv_sec) << 0xA);
// [...]
prng_state.s3 = HIDWORD(ts.tv_sec) ^ LODWORD(ts.tv_sec) ^ (LODWORD(ts.tv_sec) << 0xA);
// [...]
prng_state.s4 = v5;
_writegsqword(
(unsigned int)&net_rand_noise,
__ROL8__(((unsigned __int64)&prng_state ^ __readgsqword((unsigned int)&net_rand_noise)) + v4, 0x20));
```

Désormais, il nous faut retrouver quelle est la valeur de seed utilisée pour chaque PRNG. La chaîne `ts.tv_sec` revenant régulièrement, surtout dans la (pseudo) fonction `prandom_seed_state`, nous pouvons chercher sur le Web la structure `ts` de type `timespec64` (https://elixir.bootlin.com/linux/v5.15.87/source/include/linux/time64.h#L13)

```c
struct timespec64 {
	time64_t	tv_sec;			/* seconds */
	long		tv_nsec;		/* nanoseconds */
};
```

Une définition donne ces informations additionnelles (https://stuff.mit.edu/afs/sipb/project/gnucash/src/gnucash-1.8.9/src/doc/html/structtimespec64.html) : 

> struct timespec64 is just like the unix 'struct timespec' except that we use a 64-bit signed int to store the seconds. This should adequately cover dates in the distant future as well as the distant past, as long as they're not more than a couple dozen times the age of the universe.

Il semblerait que `tv_sec` représente l'Epoch (temps Unix) en secondes ! 

En résumé :

- choix purement aléatoire d'une chaîne parmi un tableau de longueur 4
- obtention du temps Epoch en secondes, sous forme d'entier
- utilisation de l'Epoch pour seeder la fonction `prandom_seed_state`
- génération d'un flux pseudo aléatoire équivalent à un XOR entre la chaîne de caractères et la sortie de `prandom_u32_state`

La personne ayant développé ce module avait donc pour intention d'être capable de prédire des informations normalement aléatoires ! Il devient donc clair que les informations transmises à l'URL `http://82.105.114.101/6e6f7468696e6768657265` (voir partie 2) incluant le nom du fichier et sa date de création ne sont pas anodines.

### Analyse du chiffrement de fichiers par l'application er-bridge

Replongeons nous dans le code source de l'application, et plus spécifiquement le fichier `file_utils.py` contenant les fonctions de cryptographie :

```python
# safe, based on os.urandom
import secrets
# [...]
key = secrets.token_bytes(AES_KEY_SIZE)
iv = secrets.token_bytes(AES_IV_SIZE)
```

Une fois le module kernel malveillant en place, tout appel à `secrets.token_bytes` et redirigé vers la fonction `the_destiny`. Les clés et IV AES sont alors contrôlés par cette logique...

### Reproduction du module dans un environnement Vagrant

La configuration Vagrant, jointe au challenge, va nous permettre de mettre en place un système Linux dans lequel il sera possible d'insérer notre module afin de le tester :

```sh
$ mkdir vagrant && cd vagrant
$ mv ../config_vagrant.txt Vagrantfile
# Plugins vagrant
$ sudo apt-get install -y libvirt-dev
$ vagrant plugin install vagrant-timezone
$ vagrant plugin install vagrant-vbguest
$ vagrant up
```

Nous pouvons transférer le module dans la VM via la commande suivante :

```sh
$ vagrant scp ../vol2_module_output/1704168 :/home/vagrant/binfnt_misc.ko
```

Enfin, nous nous connectons dans la VM puis insérons le module : 

```sh
vagrant@ubuntu2204:~$ sudo insmod binfnt_misc.ko
```

Nous pouvons vérifier nos précédentes conjectures : 

```sh
# Test module presence
vagrant@ubuntu2204:~$ time kill 9120
-bash: kill: (9120) - No such process

real    0m3.092s
user    0m0.000s
sys     0m0.000s
# Test dissimulation
vagrant@ubuntu2204:~$ lsmod | grep binfnt_misc
vagrant@ubuntu2204:~$ kill 9119
-bash: kill: (9119) - No such process
vagrant@ubuntu2204:~$ lsmod | grep binfnt_misc
binfnt_misc            16384  0
```

Désormais, vérifions si les valeurs de sortie du module `secrets` sont suspectes : 

```sh
vagrant@ubuntu2204:~$ python3 -c 'import secrets;print([secrets.token_hex(10) for _ in range(2)])'
['84858714d832165c2b0b', 'ea93dc2aff7a422d5435']
vagrant@ubuntu2204:~$ python3 -c 'import secrets;print([secrets.token_hex(10) for _ in range(2)])'
['dde4a8a61385612d3410', 'cd91c28a08991041731f']
vagrant@ubuntu2204:~$ python3 -c 'import secrets;print([secrets.token_hex(10) for _ in range(2)])'
['f6d3a12e7d781fe91398', 'f6d3a12e7d781fe91398']
vagrant@ubuntu2204:~$ python3 -c 'import secrets;print([secrets.token_hex(10) for _ in range(2)])'
['96c5d49293b163fa4e90', '96c5d49293b163fa4e90']
```

Nous pouvons remarquer que deux demandes de `secrets.token_hex(10)` peuvent parfois renvoyer la même valeur ! En effet, la sortie de `prandom_u32_state` est constante, mais elle est XORée aléatoirement avec une des quatre chaînes du tableau. Cependant, il peut arriver que la même chaîne soit tirée au sort dans la même seconde.

### Identification des timestamps

Maintenant, nous devrions être en mesure de retrouver la valeur PRNG utilisée lors de la création des deux fichiers chiffrés dont il est question dans la description. Il nous faut simplement obtenir leur timestamp de création : 

```sh
$ stat -c "%Y" mount/fs/var/www/html/app/uploads/61e82b86235a2228c477f1ce8c5bb7e0bac76a82/61e82b86235a2228c477f1ce8c5bb7e0bac76a82
1712526390
$ stat -c "%Y" mount/fs/var/www/html/app/uploads/38111a8e12a77b820a9a3373a3f2810645a36e0e/38111a8e12a77b820a9a3373a3f2810645a36e0e
1712526401
```

### Récupération des valeurs PRNG 

Via une astuce pour changer la date du système pour une commande spécifique, nous pouvons contrôler la seed. Nous pouvons faire une requête de PRNG sur 32 octets à chaque fois :

```sh
vagrant@ubuntu2204:~$ sudo date -s "@1712526390" && sleep 0.1 && python3 -c 'import secrets;print(secrets.t
oken_hex(32))'
Sun Apr  7 23:46:30 CEST 2024
48ea1ba41d385826c16bd8ccbc798982c0c96f9e2df864551d63902cfaafc0f9
vagrant@ubuntu2204:~$ sudo date -s "@1712526401" && sleep 0.1 && python3 -c 'import secrets;print(secrets.token_hex(32))'
Sun Apr  7 23:46:41 CEST 2024
7f0571920b8d55fd70b87467c8ee982c6bdc142c8639e9b4a7b596c9e414c42c
```

Il est possible d'obtenir 4 valeurs différentes pour chaque commande. En effet, comme explicité précédemment, une clé est choisie aléatoirement pour XORer le PRNG.

Ce faisant, nous ne disposons pas de la valeur brute de `prandom_u32_state`, mais des quatre possibilités suivantes : 

```c
output = "48ea1ba41d385826c16bd8ccbc798982c0c96f9e2df864551d63902cfaafc0f9"
"sCYHnZC97X" ^ output = prandom_u32_state() // rotate[0]
"4W2TwpmFMz" ^ output = prandom_u32_state() // rotate[1]
"ZAijP8972D" ^ output = prandom_u32_state() // rotate[2]
"c63duF2UpW" ^ output = prandom_u32_state() // rotate[3]
```

Cependant, vu la quantité raisonnables de possibilités, cela reste tout à fait possible de trouver la bonne combinaison via de la force brute.

### Déchiffrement des fichiers

La logique pour déchiffrer les fichiers est disponible dans le script `decrypt.py`, et contient également des explications.

```sh
$ python3 decrypt.py mount/fs/var/www/html/app/uploads/61e82b86235a2228c477f1ce8c5bb7e0bac76a82/61e82b86235a2228c477f1ce8c5bb7e0bac76a82 48ea1ba41d385826c16bd8ccbc798982c0c96f9e2df864551d63902cfaafc0f9

{'key': b'q\x9dA\xaa8FSD\x83x\xe1\xbb\xe6w\xac\xfc\xcb\xab-\x8d\x14\x8f>[8\x1d\x9bN\xb8\xbc\xf9\x8e', 'iv': b'a\xe8+\x86#Z"(\xc4w\xf1\xce\x8c[\xb7\xe0', 'link': '61e82b86235a2228c477f1ce8c5bb7e0bac76a82#719d41aa384653448378e1bbe677acfccbab2d8d148f3e5b381d9b4eb8bcf98e61e82b86235a2228c477f1ce8c5bb7e0edff8b580e5cda5d1ef107c9'}
```

```sh
python3 decrypt.py mount/fs/var/www/html/app/uploads/38111a8e12a77b820a9a3373a3f2810645a36e0e/38111a8e12a77b820a9a3373a3f2810645a36e0e 7f0571920b8d55fd70b87467c8ee982c6bdc142c8639e9b4a7b596c9e414c42c

{'key': b'\x11\x13*\xac,\xc5\x01\x8c\x0f\x86\x1aq\x93\xd0\xbfd?\xadk\x12\xe8/\xb2\x8a\x80\xfd\xc2\xb8\x9b*\xaa:', 'iv': b'\x7f\x05q\x92\x0b\x8dU\xfdp\xb8tg\xc8\xee\x98,', 'link': '38111a8e12a77b820a9a3373a3f2810645a36e0e#11132aac2cc5018c0f861a7193d0bf643fad6b12e82fb28a80fdc2b89b2aaa3a7f0571920b8d55fd70b87467c8ee982ce241ce48e73f5a2c67b8e986'}
```

Le contenu de chaque fichier déchiffré est également joint.


### Flag

- Le contenu déchiffré du fichier spécifié dans la description, ou celui du mail joint à ce challenge. Chacun contenant un secret valide, à choisir pour valider l'épreuve. PS : Les fichiers en clair sont tous deux des fichiers ZIP. : `2.12046` OU `10.26487`.

`BZHCTF{2.12046}` OU `BZHCTF{10.26487}`
