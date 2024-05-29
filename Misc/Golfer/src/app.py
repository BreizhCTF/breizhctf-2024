from flask import Flask, render_template, request, jsonify
from pwn import *
from base64 import b64decode, b64encode
import random
import string
import tempfile
import shutil
import subprocess
import os
app = Flask(__name__,
            static_folder='static/')

def generate_shellcode(guess):
    base_shellcode = b"\xeb\x20\x48\x31\xc0\x48\x31\xff\x48\x31\xf6\x48\x31\xd2\xb0\x01\x40\xb7\x01\x5e\xb2\x0c\x0f\x05\x48\x31\xc0\xb0\x3c\x40\xb7\x00\x0f\x05\xe8\xdb\xff\xff\xffHello World!"
    return base_shellcode.replace(b"Hello World!", guess)

@app.route('/')
def hello_world():
    return render_template("index.html")

@app.route('/run', methods=["POST"])
def run():
    data = request.get_json()
    if data.get("code"):
        try:
            code = b64decode(data["code"]).decode()
            if len(code) <= 415:
                to_guess = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase, k=12))
                shellcode_output = b64encode(generate_shellcode(to_guess.encode()))
                to_send = "$> rustc main.rs\n"
                to_send += "$> ./main\n"
                success = True
                with tempfile.TemporaryDirectory(dir="/opt/rust/tmp/") as temp_dir:
                    for _ in range(5):
                        file_main = open(f"{temp_dir}/main.rs","w")
                        file_main.write(b64decode(data["code"]).decode())
                        file_main.close()
                        shutil.copyfile("/root/run.sh",f"{temp_dir}/run.sh")
                        os.chmod(temp_dir, 0o777)
                        os.chmod(f"{temp_dir}/run.sh",0o777)
                        output = subprocess.check_output(["sudo","-u","nobody",f"{temp_dir}/run.sh",temp_dir,shellcode_output])
                        if output.decode().strip() != to_guess:
                            success = False
                            break
                if success:
                    to_send += "Well Done! Le flag est:\nBZHCTF{0h_y0ur3_4_g0lf_m4st3r_!!}"
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