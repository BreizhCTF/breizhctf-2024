BreizhCTF 2024 - The Intrepid
==========================

À débloquer dans l'ordre suivant : 

- 1/4 débloque 2/4
- 2/4 débloque 3/4 et 4/4

## Partie 1

Difficulté : Facile

### TL;DR

*Il est conseillé de réaliser cette série de challenges dans l'ordre : 1, 2, 3 puis 4.*

**De :** `the-intrepid-journal@notproton.me`  
**À :** `dfir-independant-consulting@notproton.me` (vous)

**Objet :** [`www.dfir-independant-consulting.notcom`] Nouveau contrat : The Intrepid journal

Bonjour,

*The Intrepid* est un journal autonome et collaboratif, auquel chacun peut participer et soumettre des investigations et articles.
Nos auteurs enquêtent majoritairement sur les structures politiques et économiques de grandes envergures.

Pour permettre l'échange d'informations et fichiers sensibles, nous avons récemment développé notre propre service de partage de ressources, nommé "er-bridge".
Un identifiant est associé à chaque ressource, est connu uniquement du téléverseur, et ne peut être accédé qu'une seule fois pour téléchargement, avant d'être détruit. 
Le service est exposé derrière un reverse proxy sur le réseau TOR, et son URL d'accès est en diffusion restreinte. Il est également hébergé dans une machine virtuelle, sur notre serveur.

Cependant, nous avons reçu des plaintes d'utilisateurs, indiquant que leurs identifiants de partage n'étaient pas accessibles par leurs pairs. 
Tout nous porte à croire que quelqu'un télécharge les ressources, impliquant un accès aux identifiants de partage, pourtant transmis de manière unique entre le serveur et l'utilisateur.

Un traceur applicatif est en place sur notre service, afin de monitorer et ajuster notre code, en fonction de l'usage mémoire occasionné par les différents threads. 
Pourriez-vous en analyser les journaux, afin d'identifier si une intrusion s'est produite via l'application ? PS : L'outil d'analyse graphique peut être plus performant avec l'option `--use_external_processor`, ainsi que le navigateur Google Chrome.

---

Identifiez :

- Une première charge malveillante, injectée pour contourner l'authentification de l'application
- La CVE utilisée pour élever les privilèges, déductible de la deuxième charge malveillante, ayant réalisée une exécution de code à distance
- Le numéro de thread, durant lequel les charges ont été injectées

Format de flag : `BZHCTF{charge_contournement_authentification|cve_privesc|numero_thread}`  
Exemple de flag : `BZHCTF{'OR(5)#|CVE-2024-3094|487}`

### Auteur

Abyss Watcher

### Fichiers

- `dist/partie_1/er-bridge_source.zip`
- `dist/partie_1/viztracer.json.tar.gz`

## Partie 2 

Difficulté : Moyen

### TL;DR

**De :** `the-intrepid-journal@notproton.me`  
**À :** `dfir-independant-consulting@notproton.me` (vous)

**Objet :** Re : [`www.dfir-independant-consulting.notcom`] Nouveau contrat : The Intrepid journal

> [...] Je vous recommande d'arrêter temporairement votre application, sans re-déployer la VM. Notre objectif est d'identifier le *modus operandi* de l'intrus, afin de patcher complètement l'environnement. Pourriez-vous me fournir une capture RAM et disque de votre VM ?

Nous vous remercions pour cette première analyse, l'application est temporairement arrêtée, et nous gérons la communication utilisateur de notre côté. Le code source est également intact, aucune porte dérobée n'est présente en son sein.

Aucune trace d'exécution des charges précédemment identifiées n'ont été remarquées sur le système, qui a par ailleurs été malencontreusement redémarré par notre administrateur système, dans une tentative d'expulsion de l'attaquant. Nous ne pouvons vous fournir, comme demandé, qu'une capture RAM post-redémarrage. 
Ne vous étonnez d'ailleurs pas de retrouver quelques-unes de ses tentatives d'analyse à chaud, dans les traces.

---

Identifiez :

- Le chemin disque complet, du fichier de persistance, contenant la commande utilisée pour (re)lancer le procédé malveillant
- Le nom de l'outil/wrapper utilisé pour exécuter le processus malveillant
- Le chemin Web, employé par la charge virale, pour transmettre des informations sur les identifiants de partage, à un serveur distant

Format de flag : `BZHCTF{chemin_disque_persistence|nom_outil|chemin_web_vers_serveur}`  
Exemple de flag : `BZHCTF{/home/user/fichier.txt|empire|http://127.0.0.1/my_endpoint}`

### Auteur

Abyss Watcher

### Fichiers

- `dist/partie_2/intrepid.ram.tar.gz`
- `dist/partie_2/intrepid.vmdk.tar.gz`
- `dist/partie_2/Volatility_ressources.zip`

## Partie 3 

Difficulté : Difficile

### TL;DR

*Note à moi-même :*  

J'ai l'impression qu'une charge additionnelle s'est ancrée à la racine même du système Linux. Il faut que je parvienne à l'extraire pour en déterminer ses fonctionnalités.

---

Identifiez :

- Le code décimal, qui passé en argument d'une certaine commande système, permet d'obtenir les privilèges root

Format de flag : `BZHCTF{code_decimal}`  
Exemple de flag : `BZHCTF{94578}`

### Auteur

Abyss Watcher

### Fichiers

- `dist/partie_3/doc_perso_vol3.md`

## Partie 4

Difficulté : Difficile

### TL;DR

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

### Auteur

Abyss Watcher

### Fichiers

- `dist/partie_4/config_vagrant.txt`
- `dist/partie_4/mail_anonyme.md`