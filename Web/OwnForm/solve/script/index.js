const express = require('express');
const https = require('https');
const fs = require('fs');
const path = require('path');

const app = express();

app.get('/', (req, res) => {
  console.log("REQUEST RECEIVED");
  res.sendFile(path.join(__dirname, 'index.html'))
});

const httpsOptions = {
  key: fs.readFileSync(path.join(__dirname, 'keys/privkey.pem')),
  cert: fs.readFileSync(path.join(__dirname, 'keys/fullchain.pem'))
};

https.createServer(httpsOptions, app).listen(30001, () => {
  console.log('Serveur d\'attaque HTTPS démarré sur le port 4443');
});