const express = require('express');
const bodyParser = require('body-parser');
const session = require('express-session');
const http = require('http');
const https = require('https');
const fs = require('fs');
const path = require('path');
const list_departments = require("./departements.json");
const bot = require('./bot');
const { createChallenge, verifySolution } = require('altcha-lib');

const app = express();

app.use(express.static(path.join(__dirname, 'static')));
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());
app.use(session({
    secret: process.env.SECRET ?? 'secret',
    resave: false,
    saveUninitialized: true,
    cookie: {
        sameSite: 'None',
        secure: true,
        httpOnly: true
    }
}));

app.set('trust proxy', true);
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));
app.set('etag', false);

app.use((req, res, next) => {
    res.header('Access-Control-Allow-Origin', req.headers.origin);
    res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept, Cookie');
    res.header('Access-Control-Allow-Credentials', true);
    next();
});

// OUT OF CHALLENGE
app.get('/idea', (req, res) => {
    let data = {};
    req.session.idea_visit = true;
    if (req.session.successReport !== undefined) {
        data['success'] = req.session.successReport;
        req.session.successReport = undefined;
    } else {
        data['error'] = req.session.errorReport;
        req.session.errorReport = undefined;
    }
    res.render('report', { data });
})

app.get('/captcha', async (req, res) => {
    res.json(await createChallenge({ hmacKey: 'ABCDEF' }));
});

// OUT OF CHALLENGE
app.post('/idea', async (req, res) => {
    if (!req.body.altcha || !(await verifySolution(req.body.altcha, 'ABCDEF'))) {
        req.session.errorReport = "Erreur de captcha";
        res.redirect("/idea");
    } else if (req.session.idea_visit) {
        if (req.body.url !== undefined) {
            if (req.body.url.startsWith("http://") || req.body.url.startsWith("https://")) {
                try {
                    await bot.goto(req.body.url);
                } catch (error) {
                    console.log(`[BOT CRASH] ${error}`)
                }
                req.session.successReport = "Merci, ce formulaire est effectivement joli !";
            } else {
                req.session.errorReport = "L'URL fourni est invalide.";
            }
        } else {
            req.session.errorReport = "Aucun URL n'a été fourni.";
        }
        res.redirect("/idea");
    } else {
        res.status(400).send('Requête invalide');
    }
})

app.get('/', (req, res) => {
    req.session.has_visit = true;
    let data = {};
    if (req.session.success !== undefined) {
        data['success'] = req.session.success;
        req.session.success = undefined;
    } else {
        data['error'] = req.session.error;
        req.session.error = undefined;
    }
    res.render('index', { data });
});

app.post('/submit-form', (req, res) => {
    if (req.session.has_visit) {
        if (req.body.email !== undefined && req.body.nom !== undefined && req.body.prenom !== undefined && req.body.departement !== undefined) {
            if (!req.body.email.includes("@")) { //todo: change this to a valid pattern regex
                req.session.error = "L'email n'est pas valide.";
            }
            if (req.session.error === undefined) {
                var is_present = false;
                for (var i = 0; i < list_departments.length; i++) {
                    if (req.body.departement == list_departments[i]['code']) {
                        is_present = true;
                        break;
                    }
                }
                if (is_present) {
                    req.session.success = "Le formulaire a bien été envoyé.";
                    //todo: send the email
                } else {
                    req.session.error = "Le département " + req.body.departement + " n'existe pas.";
                }
            }
        } else {
            req.session.error = "Il manque des paramètres.";
        }
        res.redirect("/");
    } else {
        res.status(400).send('Requête invalide');
    }
});

const httpsOptions = {
    key: fs.readFileSync(path.join(__dirname, 'keys/privkey.pem')),
    cert: fs.readFileSync(path.join(__dirname, 'keys/fullchain.pem'))
};
https.createServer(httpsOptions, app).listen(443, () => {
    console.log(`Serveur HTTPS démarré sur le port 443`);
});
http.createServer(app).listen(80, () => {
    console.log(`Serveur HTTP démarré sur le port 80`);
});

process.on('SIGTERM', () => process.exit(0));
process.on('SIGINT', () => process.exit(0));
