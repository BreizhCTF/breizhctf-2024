#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
    Install and update challenge.yml using ctfcli

    - Sort by Category name, Difficuty and Challenge name
    - Default "Categorie" is removed
    - "Autres" category is set at the top
    - Unknown difficulties are added first
"""

import os
import sys
import traceback
from pathlib import Path
from ctfcli.cli.challenges import ChallengeCommand


cli = ChallengeCommand()

# Since requests is not able to stream file upload,
# keep track of very large files in order to skip them
big_boys = ("Miroir Miroir", )

# Get each challenge.yml
chall_list = []
for root, dirs, files in os.walk("."):
    for file in files:
        if "challenge" in file and file.endswith('.yml'):
            if "_exemple" not in root:
                chall_list.append(Path(f"{root}/{file}").absolute())


# For each file, extract category, name and difficulty
# chall_dict[category][difficulty][name]
chall_dict = {}
for f in chall_list:
    content = open(f, 'r').readlines()
    difficulty = '?'
    category = '?'
    name = '?'
    for l in content:
        if l.startswith("category: "):
            category = l.strip("category: ").strip()
        elif l.startswith("name: "):
            name = l.strip("name: ").strip().strip('"')
        elif "facile" in l.lower() or \
             "moyen" in l.lower() or \
             "difficile" in l.lower():
            difficulty = l.strip().strip('-').strip()

    if category not in chall_dict:
        chall_dict[category] = {}
    if difficulty not in chall_dict[category]:
        chall_dict[category][difficulty] = {}

    chall_dict[category][difficulty][name] = f

# Sort challenges by Category
category_order = list(chall_dict.keys())
category_order.sort()
category_order.remove("Autres")
category_order.remove("Sponsors")
category_order = ["Autres"] + category_order + ["Sponsors"]

# Then by difficulty
difficulty_order = ["?", "Très Facile", "Facile", "Moyen", "Difficile", "Très Difficile"]

intrepid = []  # Serie de chall
tampered = []  # Serie de chall

# Add challenges
for c in category_order:
    for d in difficulty_order:
        if d not in chall_dict[c] and c != "Osint":
            continue
        chall_names = list(chall_dict[c][d].keys())  # Sort by names
        chall_names.sort()
        for n in chall_names:
            if "The Intrepid" in n:
                intrepid.append(chall_dict[c][d][n])
                continue
            if "Tampered" in n:
                tampered.append(chall_dict[c][d][n])
                continue

            print(f"[+] {n}")
            path = chall_dict[c][d][n]
            try:
                cli.install(path.as_posix(), force=True, ignore="files" if n in big_boys else tuple())
            except Exception as e:
                print(f"[!!!] Error with challenge {path}")
                print(e)
                print(traceback.format_exc())
                print(sys.exc_info()[2])

intrepid.sort()
tampered.sort()

chall_dict["Mobile"]["Difficile"] = chall_dict["Mobile"]["Difficile"][::-1]

for path in intrepid+tampered:
    try:
        cli.install(path.as_posix(), True, ignore="files")
    except Exception as e:
        print(f"[!!!] Error with challenge {path}")
        print(e)
        print(traceback.format_exc())
        print(sys.exc_info()[2])
