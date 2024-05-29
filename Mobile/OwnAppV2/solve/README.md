# OwnAppV2

Dans ce challenge, on voit que l'on a une application flutter, si on se renseigne, on voit que cette technologie bypass les proxys du téléphone.

Pour pallier ce problème, il faut utiliser :

- reFlutter, permettant de modifier l'application pour reprendre en compte le proxy
- uber-apk-signer, permettant de réaligner et signer l'application

On peut donc ensuite mettre notre proxy sur le téléphone.

/!\ Il ne faut pas utiliser un téléphone rooté, sans quoi flutter le vois et ne prend pas le proxy. A noter qu'il est possible de le faire avec frida sur un téléphone root, mais la solution la plus simple suffit de prendre un téléphone non-rooté.

Lorsqu'on atteint le score 42, on voit qu'une requete part sur `/score_from_user_app_android?score=42`, on peut donc modifier son score par `/score_from_user_app_android?score=1333378`, et on obtient le flag.

# Flag

BZHCTF{flutt3r_c4n_b3_tr1cky_t0_byp4ss}
