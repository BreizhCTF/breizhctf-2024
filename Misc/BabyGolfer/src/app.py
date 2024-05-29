from flask import Flask, render_template, request, jsonify
from base64 import b64decode, b64encode
import random
import string
import tempfile
import shutil
import subprocess
import os
app = Flask(__name__,
            static_folder='static/')

PALINDROMS = open("/root/palindrome.txt","r").read().split("\n")[:-1]

@app.route('/')
def hello_world():
    return render_template("index.html")

@app.route('/run', methods=["POST"])
def run():
    data = request.get_json()
    if data.get("code"):
        try:
            code = b64decode(data["code"]).decode()
            if len(code) <= 55:
                to_send = "$> python3 main.py\n"
                success = True
                with tempfile.TemporaryDirectory(dir="/tmp/") as temp_dir:
                    for _ in range(30):
                        file_main = open(f"{temp_dir}/main.py","w")
                        file_main.write(b64decode(data["code"]).decode())
                        file_main.close()
                        shutil.copyfile("/root/run.sh",f"{temp_dir}/run.sh")
                        os.chmod(temp_dir, 0o777)
                        os.chmod(f"{temp_dir}/run.sh",0o777)
                        is_palindrome = False
                        word = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase, k=20))
                        if int(random.randint(0,1)):
                            word = random.choice(PALINDROMS)
                            is_palindrome = True
                        output = subprocess.check_output(["sudo","-u","nobody",f"{temp_dir}/run.sh",temp_dir,word])
                        if output.decode().strip() != str(is_palindrome):
                            success = False
                            break
                if success:
                    to_send += "Well Done! Le flag est:\nBZHCTF{w3lc0m3_t0_g0lf_g4m3_!!}"
                else:
                    to_send += "***wrong output detected***\nVotre code n'a pas retourné le résultat attendu.."
                return jsonify({"ok":to_send})
            else:
                return jsonify({"error":"Le code fourni est trop long.. il faut golfer !"})
        except Exception as e:
            print(e)
            return jsonify({"error":"La base64 fournie n'est pas correcte"})
    else:
        return jsonify({"error":"Il manque un paramètre"})

app.run(host="0.0.0.0", port=5000, debug=True)