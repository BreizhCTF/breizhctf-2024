# New World - Partie 2

## Informations de base
- L'architecture du CPU est amd64.
- Les binaires ELF sont envoyés par le serveur en base64
- Votre objectif est de déterminer la sortie du binaire sur la machine distante dix fois à la suite.
- La sortie attendue est donnée si votre entrée est incorrecte.
- Vous trouverez en dessous la documentation trouvée pour les syscalls à implémenter
- Vous n'avez que quelques secondes pour répondre

## Syscalls New World

### Custom mmap - numéro 31337
Créer une zone mémoire à l'adresse 0x13370000 de taille 0x10000

### md5sum - numéro 31338
Réalise le condensat MD5 d'une zone mémoire.
Paramètres :
- x64 : rdi - zone sur laquelle est réalisée le condensat
- x64 : rsi - zone de destination du condensat
- x64 : rbx - longueur à condenser

### sha1sum - numéro 31339
Réalise le condensat SHA1 d'une zone mémoire.
Paramètres :
- x64 : rdi - zone sur laquelle est réalisée le condensat
- x64 : rsi - zone de destination du condensat
- x64 : rbx - longueur à condenser

### sha256sum - numéro 31340
Réalise le condensat SHA256 d'une zone mémoire.
Paramètres :
- x64 : rdi - zone sur laquelle est réalisée le condensat
- x64 : rsi - zone de destination du condensat
- x64 : rbx - longueur à condenser

### write modifié - numéro 31341
Réalise un affichage sur la sortie avec un encodage en fonction d'un index passé en paramètre.

Paramètres :
- rdi - zone à afficher
- rsi - longueur de la zone prise en compte pour l'affichage (avant encodage)
- rbx - index pour l'encodage
    - 1 : base64
    - 2 : base32
    - 3 : base16
    - 4 : base85