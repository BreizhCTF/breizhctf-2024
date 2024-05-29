BreizhCTF 2023 - Challenge
==========================

### Challenge details

| Event          | Challenge | Category  | Points | Solves |
| -------------- | --------- | --------- | ------ | ------ |
| BreizhCTF 2024 |randomguesser | Crypto | ???    | ???    |



### TL;DR


Bob vous assure qu'une signature ECDSA n'est pas distinguable d'un message aléatoire.
Prouvez à Bob que ce qu'il dit est faux.


### Méthodologie

<details>
    <summary>Solution du challenge</summary>

    Ce challenge demande à l'utilisateur de trouver un biais pour distinguer une suite d'octets random d'une vraie signature ECDSA.

    Le taux de réussite requit pour obtenir le flag est de 75%. 
    En supposant que nous nous tromperons 50% du temps sur un message random, cela implique un taux de réussite proche des 100% pour les vrais signatures.

    il faut donc trouver une propriétée qui sera toujours vraie pour une signature ECDSA.

    une signature ECDSA est composé de deux nombres : r et s.

    r correspond à la coordonnée x d'un point appartenant à la courbe : y**2 ≡ x**3 + a*x + b mod p

    Nous pouvons en déduire que x**3 +a*x +b est un résidu quadratique. (equation de la forme : k**2 ≡ j mod p)

    Cela implique que la fonction de legendre pour r**3+a*r+b retournera toujours 1 car la fonction de legendre retourne 1 si le nombre est un résidu quadratique et -1 si cela n'est pas le cas. (le cas de 0 est aussi possible si jamais r**3+a*r+b est divisible par p)

    Nous allons donc renvoyer "yes" si le résultat vaut 1, "no" si le résultat est différent.


</details>

# Flag

<details>
    <summary>Flag</summary>
    `BZHCTF{13g3ndreSymb0l1sTheK3y}`
</details>