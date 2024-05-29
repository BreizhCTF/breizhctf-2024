#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
    Upload challenges pictures to `/files/chall/*`
"""

import os
from pathlib import Path
from ctfcli.core.api import API

api = API()

# Get each images
img_list = []
for root, dirs, files in os.walk("."):
    for file in files:
        if root.count("/") <= 2 and "/doc" not in root \
            and "/dist" not in root and "/solve" not in root \
            and "/src" not in root and "/build" not in root:
            if file.endswith('.jpg') or file.endswith('.jpeg') or file.endswith('.png'):
                img_list.append(Path(f"{root}/{file}").absolute())

for img in img_list:
    img_name = img.name
    print(img_name)
    r = api.post('/api/v1/files', files={
        "file": open(img, 'rb')
    }, data={
        "location": f"chall/{img_name}",
        "type": "page"
    })
    print(r.text)
