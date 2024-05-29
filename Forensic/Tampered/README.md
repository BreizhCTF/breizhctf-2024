

## Description - Partie 1 

Pour ce CTF Attaque/Défense, les administrateurs nous ont fournis des machines virtuelles sur lesquelles les services tournent, une machine à attirer notre attention ne pouvant pas lire le flag dessus... On pense à un sabotage d'une équipe qui auraient réussi à faire en sorte que la machine virtuelle que l'on nous a donnée est déjà compromise... Veuillez nous aider à investiguer.

On veut premièrement que vous trouviez le malware et comment persiste-t-il à chaque redémarrage de la VM.

Le format de flag est : `BZHCTF{chemin_du_malware:chemin_du_fichier_utilisé_pour_la_persistence}`

Exemple : `BZHCTF{/var/superfichier1.txt:/var/superfichier2.txt}`

sha256sum vm-tampered.ova : `ce4932eb4478241215873161d535d66f61848295ade3be1b364c8ed1eab35941`

## Description - Partie 2 - Débloquée une fois la partie 1 réussie

Super vous avez trouvé le malware, maintenant on veut savoir ce qu'il fait. Voici ce que vous devez trouver :
- (1) Trouver les commandes qui sont interdites par le malware
- (2) Trouver la commande qui désactive le malware
- (3) Trouver la commande secrète qui déclenche un dernier comportement malveillant
- (4) Trouver la sous chaine de caractère qui est vérifiée afin de bloquer la lecture un certain fichier particulier, permettant de bloquer une dernière commande

Le format de flag est : `BZHCTF{(1):(2):(3):(4)}`
Pour les commandes interdites, vous les séparerez les commandes par des virgules, dans l'ordre alphabétique.

Voici un exemple de flag : `BZHCTF{id,whoami:grep:strings}`

sha256sum vm-tampered.ova : `ce4932eb4478241215873161d535d66f61848295ade3be1b364c8ed1eab35941`

