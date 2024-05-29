BreizhCTF 2023 - Challenge
==========================

### Challenge details

| Event          | Challenge | Category  | Points | Solves |
| -------------- | --------- | --------- | ------ | ------ |
| BreizhCTF 2024 | squareOrNot | Cryptographie | ???    | ???    |



### TL;DR

Votre ami charlie a créé un nouveau système de chiffrement inviolable.
Obtenez la clef et Charlie vous donnera une récompense. 


### Méthodologie

<details>
    <summary>Solution du challenge</summary>

    Il  est possible d'interagir avec le challenge de plusieurs manières possibles.

    Il est possible d'envoyer des messages, de les combiner ainsi que de les mesurer.

    On remarque qu'il n'est pas possible de soumettre deux fois le même message par octet de clef à deviner.

    Cependant, il est possible d'obtenir un message prévisible avant de mesurer.

    Si nous soumettons 256 messages identiques mais avec un octet qui varie de 0 à 255 à la même position,

    et que nous combinons ces messages, le résultat est un message avec chaque élément avec teta et phi à zéro.

    Nous pouvons donc généré 256 messages prévisible et utiliser la fonction de mesure pour retrouver l'octet de la clef.

    Il est possible de discrimier l'octet en question avec une grande probabilité car si teta et phi valent 0, alors l'octet de sortie vaudra lui aussi 0.
    
    il faut soumettre la clef octet par octet afin d'obtenir le flag.
    
</details>

# Flag

<details>
    <summary>Flag</summary>
    `BZHCTF{Bloc15ph3r31sinterest1nG}`
</details>