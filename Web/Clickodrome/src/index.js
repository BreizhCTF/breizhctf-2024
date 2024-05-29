const express = require('express');
const path = require('path')
const bodyParser = require('body-parser');
const data = require("./cards.json");
const bot = require("./bot");
const valid_refs = ["100€","200€","300€","400€","500€","useless"];
const local_allowed_ips = ["::ffff:127.0.0.1","::1"];

const app = express();
const port = process.env.PORT ?? 3000;
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());

app.use(express.static(path.resolve('./public')));
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));
app.set('etag', false);

app.get('/', (req, res) => {
    res.render('index', {data});
});

app.get('/reports', (req, res) => {
    if(local_allowed_ips.includes(req.socket.remoteAddress)) {
        if(req.query.ref !== undefined && req.query.reason !== undefined) {
            console.log(req.query);
            let data = {"ref": req.query.ref, "reason": atob(req.query.reason)};
            res.render('report', {data});
        } else {
            res.json({"message":"Il manque des paramètres"});
        }
    } else {
        console.log(req.socket.remoteAddress)
        res.status(403).json({"message":"Accès interdit."});
    }
})

app.post('/report', async (req, res) => {
    let data = {};
    if(req.body.ref !== undefined && req.body.reason !== undefined){
        if(valid_refs.includes(req.body.ref)) {
            try {
                let res = await bot.goto(port, req.body.ref, req.body.reason);
                if(res){
                    data = {"message":"Merci pour votre rapport !"};
                } else {
                    data = {"message":"Une erreur est survenue."};
                }
            } catch(err) {
                console.log(`[BOT - ERROR] ${err}`)
                data = {"message":"Une erreur est survenue."};
            }
        } else {
            data = {"message":"La référence n'est pas valide."};
        }
    } else {
        data = {"message":"Il manque des paramètres."};
    }
    res.json(data);
})


app.listen(port, () => {
    console.log(`Example app listening on port ${port}`)
})

process.on('SIGTERM', () => process.exit());
process.on('SIGINT', () => process.exit());