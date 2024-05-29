Avant de démarrer le docker il faut build le site static avec la commande `hugo -s ./preprod`

Le site de prod est accessible sur: commissariat-jacobinks.ctf.bzh
Le site de pre-prod est accessible sur: preprod.commissariat-jacobinks.ctf.bzh

Si vous testez en local, il faudra ajouter ces noms de domaines dans votre `/etc/hosts`

Particularité:
Les dossiers "protégés" par mot de passe staticrypt dans le dossier intranet et accessible sur `https://preprod.commissariat-jacobinks.ctf.bzh/intranet` doivent être testés sur localhost/intranet/ ou sur un site avec certificat HTTPS.

La raison est que le navigateur par mesure de sécurité ne charge pas l'API Crypto sur un domaine en http
