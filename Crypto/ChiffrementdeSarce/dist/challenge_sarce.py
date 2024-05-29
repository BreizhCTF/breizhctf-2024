#!/usr/bin/env python3

flag = "REDACTED"

res = []

ALPHABET="ABCDEFGHIJKLMNOPQRSTUVWXYZ{}0123456789abcdefghijklmnopqrstuvwxyz"


for i in range(len(flag)):
    if i ==0:
        res.append(ord(flag[i]) + i)
    else:

        newValue = (ord(ALPHABET[ALPHABET.index(flag[i])]) + i) *i 
        res.append(newValue)

print(res) 
# [66, 91, 148, 210, 352, 375, 774, 406, 784, 711, 590, 1276, 1512, 1664, 1820, 1230, 1040, 2193, 2196, 1330, 2680, 2268, 1562, 3197, 1920, 2700, 3198, 3807, 3556, 3770, 4650]