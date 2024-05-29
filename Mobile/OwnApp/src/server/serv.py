from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def root():
    return ''

@app.route('/my_very_secret_secret_route')
def hello_world():
    flag = request.args.get('flag',0)
    print(flag)
    if flag == "1":
        return "BZHCTF{fr1d4_0r_r3v3rs3_?}"
    else:
        return 'Hello, World!'

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=80)
