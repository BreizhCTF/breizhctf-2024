import os
import names
import random


def gen_folder():
    folder_name = names.get_last_name()[:3].upper()
    folder_number = str(random.randint(0, 9999)).zfill(4)
    folder_date = (
        str(random.randint(1, 27)).zfill(2) + str(random.randint(1, 4)).zfill(2) + "24"
    )

    full = f"{folder_name}-{folder_number}-{folder_date}"
    print(full)
    os.mkdir("../intranet/" + full)


for i in range(random.randint(30, 50)):
    gen_folder()
