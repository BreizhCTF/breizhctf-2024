#!/usr/bin/env python3

flag = "BZHCTF{3ZF1irstC1ph3rW1t8Sarce}"

res = []

ALPHABET="ABCDEFGHIJKLMNOPQRSTUVWXYZ{}0123456789abcdefghijklmnopqrstuvwxyz"


for i in range(len(flag)):
    if i ==0:
        res.append(ord(flag[i]) + i)
    else:

        newValue = (ord(ALPHABET[ALPHABET.index(flag[i])]) + i) *i 
        res.append(newValue)

print(res)