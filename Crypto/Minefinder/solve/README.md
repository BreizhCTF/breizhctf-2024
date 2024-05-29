BreizhCTF 2023 - Challenge
==========================

### Challenge details

| Event          | Challenge | Category  | Points | Solves |
| -------------- | --------- | --------- | ------ | ------ |
| BreizhCTF 2024 | Minefinder | Cryptographie | ???    | ???    |



### TL;DR


Vous devez marcher sur un chemin dangereux, arriveriez-vous à survivre en trouvant mes mines ?

### Méthodologie

<details>
    <summary>Solution du challenge</summary>

    Pour résoudre le challenge, il faudra trouver les mines 3 rounds sur 5.

    En cas d'échec, la position des mines est révélée.

    Il faut donc perdre intentionnellent le premier round, récupérer la position des mines et retrouver les valeurs aléatoires qui seront générées par la suite.

    Il sera donc possible de trouver la position des futures mines pour les rounds suivants et obtenir le flag.

</details>

# Flag

<details>
    <summary>Flag</summary>
    `BZHCTF{g00dJob1tF1nd1n3Mine}`
</details>