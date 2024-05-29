# Writeup

La vuln ici est une CRLF dans le nom du fichier lors du download. Ainsi on peut ajouter un header Set-Cookie avec un cookie de session PHP.
On envoie l'URL au bot et il va telecharger le fichier puis se connecter. Avec un cookie qu'on controle en tant qu'attaquant. Ensuite il suffit d'utiliser son cookie et on sera connecte au compte de l'admin. On peut donc recuperer le flag.


