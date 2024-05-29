BreizhCTF 2023 - Challenge
==========================

### Challenge details

| Event          | Challenge | Category  | Points | Solves |
| -------------- | --------- | --------- | ------ | ------ |
| BreizhCTF 2024 | ChiffrementdeSarce | Cryptographie | ???    | ???    |



### TL;DR

    Vous venez de reçevoir un message important de Rome, retrouvez le message.

### Méthodologie

<details>
    <summary>Solution du challenge</summary>
    Le chiffrement custom est un chiffrement où l'on fait la somme de chaque caractère avec son indice puis on  multiplie le résultat avec son indice.

    Il suffit de diviser chaque valeur par son indice, de soustraite à nouveau l'indice et de faire une conversion int to char.
</details>

# Flag

<details>
    <summary>Flag</summary>
    `BZHCTF{3ZF1irstC1ph3rW1t8Sarce}`
</details>