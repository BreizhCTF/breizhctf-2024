# OwnApp

Lorsqu'on regarde l'applicaiton, on voi qu'un SSL pinning est en place.

Il y a deux manières de résoudre le challenge :
- Reverse la librarie native c++ (très long)
- Utiliser frida et un script de sslpinning bypass

Je ne WU pas la partie reverse puisque ce n'est pas celle-ci que j'ai imaginé en écrivant ce challenge.

Pour frida :
- Il faut installer le certificat de burp sur le téléphone
- Utiliser adb pour set un proxy `adb shell settings put global http_proxy <IP>:8080`
- Utiliser frida `frida -U -f com.example.ownapp -l sslpinning.js`
- Avec burp, on voit une requête passer vers `https://ownapp.ctf.bzh/my_very_secret_secret_route?flag=0`
- Il suffit de passer `flag` à 1 pour obtenir le flag

# Flag

BZHCTF{fr1d4_0r_r3v3rs3_?}
